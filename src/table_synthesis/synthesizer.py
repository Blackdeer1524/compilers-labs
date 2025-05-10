from dataclasses import dataclass
from typing import Literal, Optional
from src.scanning.scanner import Ident, QuotedStr
from src.analysis.ast import *
from src.text.processors import Position

RULE_T = list[Ident | QuotedStr | Literal["epsilon"]]
AXIOM_INTO_T = tuple[str | None, Position | None] | None


@dataclass
class ProductionInfo:
    lhs: Ident
    rhs: list[RULE_T]
    is_axiom: bool


class SemanticsAnalyzer:
    def __init__(self):
        self.errors: list[str] = []

    def store_error(self, mes: str, pos: Position | None):
        self.errors.append(f"[{pos if pos is not None else '???'}] {mes}")

    def collect_axiom(self, node: AxiomNode) -> bool:
        return node.value is not None

    def collect_nonterm(self, node: NonTermNode) -> Optional[Ident]:

        if node.value is None:
            self.store_error(f"expected {node.node_label} not to be None", node.pos)
            return None
        return node.value

    def collect_term(self, node: TermNode) -> Optional[QuotedStr]:
        if node.value is None:
            self.store_error(f"expected {node.node_label} not to be None", node.pos)
            return None
        return node.value

    def collect_rule_tail(self, node: RuleTailNode) -> RULE_T:
        match node.value:
            case None:
                return []
            case KeywordNode(kind="epsilon"):
                return ["epsilon"]
            case KeywordNode(kind=unknown):
                self.store_error(f"unexpected keyword: {unknown}", node.pos)
                return []
            case RuleNode() as rule:
                return self.collect_rule(rule)

    def collect_rule(self, node: RuleNode) -> RULE_T:
        match node.value:
            case None:
                self.store_error(f"expected a rule {node.pos}", node.pos)
                return []
            case (TermNode() as term, RuleTailNode() as tail):
                term = self.collect_term(term)
                if term is None:
                    return self.collect_rule_tail(tail)
                return [term] + self.collect_rule_tail(tail)
            case (NonTermNode() as non_term, RuleTailNode() as tail):
                non_term = self.collect_nonterm(non_term)
                if non_term is None:
                    return self.collect_rule_tail(tail)
                return [non_term] + self.collect_rule_tail(tail)
            case KeywordNode(kind="epsilon"):
                return ["epsilon"]
            case KeywordNode(kind=unknown):
                self.store_error(f"unexpected keyword: {unknown}", node.pos)
                return []

    def collect_alt_rules(self, node: RuleAltNode) -> list[RULE_T]:
        match node.value:
            case None:
                return []
            case (
                KeywordNode() as kw_or,
                RuleNode() as rule,
                RuleAltNode() as alt_rules,
            ):
                if kw_or.kind != "or":
                    self.store_error(
                        f'expected "or" keyword, but "{kw_or.kind}" found', kw_or.pos
                    )
                if kw_or.value is None:
                    self.store_error(
                        f"expected {kw_or.node_label} not to be None", kw_or.pos
                    )
                return [self.collect_rule(rule)] + self.collect_alt_rules(alt_rules)

    def collect_init_node(self, node: InitNode) -> ProductionNode | None:
        if node.value is None:
            self.store_error(f"expected {node.node_label} not to be None", node.pos)
            return None
        return node.value[0]

    def process_productions(
        self, node: InitNode
    ) -> tuple[AXIOM_INTO_T, dict[str, ProductionInfo]] | list[str]:
        cur_opt = self.collect_init_node(node)
        if cur_opt is None:
            errs = self.errors
            self.errors = []
            return errs
        cur = cur_opt

        axiom_info: AXIOM_INTO_T = None
        res: dict[str, ProductionInfo] = {}
        while True:
            if cur.value is None:
                break

            (kw_axiom, nonterm, kw_is, rhs, alt_rules, kw_end, next_prod) = cur.value

            is_axiom = self.collect_axiom(kw_axiom)
            lhs = self.collect_nonterm(nonterm)
            if kw_is.value is None:
                self.store_error(
                    f"expected {kw_is.node_label} not to be None", kw_is.pos
                )

            rhs = [self.collect_rule(rhs)] + self.collect_alt_rules(alt_rules)

            if kw_end.value is None:
                self.store_error(
                    f"expected {kw_end.node_label} not to be None", kw_end.pos
                )

            if is_axiom:
                if axiom_info is not None:
                    self.store_error(
                        f"found another axiom. prev definition: {axiom_info}",
                        kw_axiom.pos,
                    )
                else:
                    axiom_info = (lhs.value if lhs is not None else None, kw_axiom.pos)

            if lhs is not None:
                if (prev_def := res.get(lhs.value)) is None:
                    res[lhs.value] = ProductionInfo(lhs, rhs, is_axiom)
                else:
                    self.store_error(
                        f"found redefinition of {lhs.value}. Prev definition: {prev_def.lhs.start}",
                        lhs.start,
                    )
            cur = next_prod

        if len(self.errors) > 0:
            errs = self.errors
            self.errors = []
            return errs

        return (axiom_info, res)
