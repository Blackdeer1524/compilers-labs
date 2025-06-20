from collections import defaultdict
from functools import reduce
from typing import DefaultDict
from src.scanning.scanner import Ident, QuotedStr
from src.table_synthesis.semantics import RULE_TAIL_T, ProductionInfo
from src.text.processors import Position


class SynthError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

DIRECTIVE_PREFIX = "#"
EOF_DIRECTIVE = f"{DIRECTIVE_PREFIX}EOF"

LL1_TABLE_T = dict[str, DefaultDict[str, RULE_TAIL_T | None]]

INIT_NODE_NAME = "Init"


def render_table(table: LL1_TABLE_T) -> str:
    init: set[str] = set()
    keys = list(
        reduce(lambda l, r: l.union(r), (set(v.keys()) for v in table.values()), init)
    )

    res = ""
    res += "|   |"
    for key in keys:
        res += f"{key}|"
    res += "\n"

    res += "|-|"
    for key in keys:
        res += "-|"
    res += "\n"

    for nt, row in table.items():
        res += f"|{nt}|"
        for key in keys:
            rule = row[key]
            if rule is None:
                res += f"-|"
            elif len(rule) == 0:
                res += f"𝓔|"
            else:
                res += " ".join((i.value for i in rule)) + "|"
        res += "\n"
    return res


class Synthesizer:
    def __init__(self):
        self.reset()

    def reset(self):
        self.axiom = ""
        self.productions: dict[str, ProductionInfo] = {}

        self.accepts_epsilon: set[str] = set()
        self.seen: set[str] = set()

        self.first_sets: DefaultDict[str, set[str]] = defaultdict(set)
        self.follow_sets: DefaultDict[str, set[str]] = defaultdict(set)
        self.table: LL1_TABLE_T = defaultdict(lambda: defaultdict(lambda: None))

    def calculate_first_sets(self, lhs: str):
        if lhs in self.seen:
            return

        self.seen.add(lhs)
        self.first_sets[lhs] = set()
        for rule in self.productions[lhs].rhs:
            match rule:
                case "epsilon":
                    self.accepts_epsilon.add(lhs)
                case list():
                    for item in rule:
                        match item:
                            case Ident() as nonterm:
                                if nonterm.value not in self.first_sets:
                                    assert nonterm.value in self.productions
                                    self.calculate_first_sets(nonterm.value)

                                for symbol in self.first_sets[nonterm.value]:
                                    if (
                                        already_defined := self.table[lhs].get(symbol)
                                    ) is not None:
                                        raise SynthError(
                                            f"ambiguity found for {lhs}: "
                                            f"tried to assign a rule {rule} to the "
                                            f"entry [{lhs}][{symbol}], but another "
                                            f"rule is already defined there: {already_defined}"
                                        )
                                    self.table[lhs][symbol] = rule

                                self.first_sets[lhs].update(
                                    self.first_sets[nonterm.value]
                                )
                                if nonterm.value not in self.accepts_epsilon:
                                    break
                            case QuotedStr() as terminal:
                                if (
                                    already_defined := self.table[lhs].get(
                                        terminal.value
                                    )
                                ) is not None:
                                    raise SynthError(
                                        f"ambiguity found for {lhs}: "
                                        f"tried to assign a rule {rule} to the "
                                        f"entry [{lhs}][{terminal.value}], but another "
                                        f"rule is already defined there: {already_defined}"
                                    )
                                self.table[lhs][terminal.value] = rule
                                self.first_sets[lhs].add(terminal.value)
                                break

    def calculate_follow_sets(self):
        while True:
            updated = False
            for nonterm, info in self.productions.items():
                for rule in info.rhs:
                    match rule:
                        case "epsilon":
                            continue
                        case list():
                            for i in range(len(rule) - 1):
                                cur = rule[i]
                                match cur:
                                    case Ident():
                                        broke_the_loop = False
                                        for after in rule[i + 1 :]:
                                            match after:
                                                case QuotedStr():
                                                    prev_len = len( self.follow_sets[cur.value])
                                                    self.follow_sets[cur.value].add( after.value)
                                                    if len(self.follow_sets[cur.value]) != prev_len:
                                                        updated = True
                                                    broke_the_loop = True
                                                    break
                                                case Ident():
                                                    prev_len = len(self.follow_sets[cur.value])

                                                    assert after.value in self.productions
                                                    self.follow_sets[cur.value].update(self.first_sets[after.value])

                                                    if len(self.follow_sets[cur.value]) != prev_len:
                                                        updated = True
                                                    if after.value not in self.accepts_epsilon:
                                                        broke_the_loop = True
                                                        break

                                        if not broke_the_loop and rule[-1].value in self.accepts_epsilon:
                                            prev_len = len(self.follow_sets[cur.value])
                                            self.follow_sets[cur.value].update(self.follow_sets[nonterm])
                                            if len(self.follow_sets[cur.value]) != prev_len:
                                                updated = True
                                    case QuotedStr():
                                        continue
                            last = rule[-1]
                            prev_len = len(self.follow_sets[last.value])
                            self.follow_sets[last.value].update(self.follow_sets[nonterm])
                            if len(self.follow_sets[last.value]) != prev_len:
                                updated = True
            if not updated:
                break

    def ensure_nonterms_are_valid(self):
        errors: list[str] = []
        for _, rules in self.productions.items():
            for rule in rules.rhs:
                match rule:
                    case "epsilon":
                        continue
                    case list():
                        for item in rule:
                            match item:
                                case Ident():
                                    if item.value not in self.productions:
                                        errors.append(item.value)
                                case QuotedStr():
                                    continue
        if len(errors) > 0:
            raise SyntaxError(f"found non-terminals without productions: {errors}")

    def setup_table_keys(self):
        symbols: set[str] = set()
        for nonterm, info in self.productions.items():
            self.table[nonterm] = defaultdict(lambda: None) 
 
            for rule in info.rhs:
                match rule:
                    case "epsilon":
                        continue
                    case list():
                        for term in rule:
                            match term:
                                case QuotedStr(value=value):
                                    symbols.add(value)
                                case Ident():
                                    continue
        
        for key in self.table:
            for symbol in symbols:
                if self.table[key].get(symbol) is None:
                    self.table[key][symbol] = None
                    

    def process(
        self, axiom: str, productions: dict[str, ProductionInfo]
    ) -> LL1_TABLE_T:
        self.reset()
        self.productions = productions

        self.axiom = axiom
        if axiom not in self.productions:
            raise SynthError(
                f"axiom {axiom} not found in productions: {self.productions.keys()}"
            )
        self.ensure_nonterms_are_valid()

        DUMMY_POS = Position(-1, -1)
        self.productions[INIT_NODE_NAME] = ProductionInfo(
            Ident(INIT_NODE_NAME, start=DUMMY_POS, end=DUMMY_POS),
            [
                [
                    Ident(axiom, start=DUMMY_POS, end=DUMMY_POS),
                    QuotedStr(EOF_DIRECTIVE, start=DUMMY_POS, end=DUMMY_POS),
                ]
            ],
        )
        self.setup_table_keys()

        for nonterm in productions:
            self.calculate_first_sets(nonterm)
        self.calculate_follow_sets()

        for eps_nonterm in self.accepts_epsilon:
            for symbol in self.follow_sets[eps_nonterm]:
                if (already_defined := self.table[eps_nonterm].get(symbol)) is not None:
                    raise SynthError(
                        f"ambiguity found for {eps_nonterm}: "
                        f"tried to assign a rule {[]} to the "
                        f"entry [{eps_nonterm}][{symbol}], but another "
                        f"rule is already defined there: {already_defined}"
                    )
                self.table[eps_nonterm][symbol] = []

        return self.table
