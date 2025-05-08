from collections import defaultdict, deque
from pprint import pprint
from typing import DefaultDict, Deque, Generator, Literal, Optional, TextIO
from dataclasses import dataclass

"""
S         ::= "`asiom"? NT "`is" RULE_OPT ("`or" RULE_OPT)* "`end" S | 𝓔
RULE_OPT  ::= RULE | "`epsilon" 
RULE      ::= "(" RULE ")" | RULE_ITEM RULE_TAIL
RULE_TAIL ::= RULE | 𝓔
RULE_ITEM ::= T | NT
NT        ::= [a-zA-Z_] [a-zA-Z0-9_]*
T         ::= "\"" (.+)? "\""
"""


@dataclass(frozen=True)
class Position:
    row: int
    col: int


class Text:
    def __init__(self, f: TextIO):
        self._f = f
        self._cur: Optional[str] = None

    def peek(self) -> Optional[str]:
        if self._cur is not None:
            return self._cur

        next = self._f.read(1)
        if len(next) == 0:
            self._cur = None
            return self._cur

        self._cur = next
        return self._cur

    def advance(self):
        self._cur = None


class TextWithPosition(Text):
    def __init__(self, f: TextIO):
        super().__init__(f)
        self._row = 1
        self._col = 1

    def position(self) -> Position:
        return Position(self._row, self._col)

    def peek(self):
        r = super().peek()
        if r == "\r":
            return "\n"
        return r

    def advance(self):
        cur = self.peek()
        if cur is None:
            return

        if cur == "\r":
            super().advance()
            next = self.peek()
            if next == "\n":
                super().advance()
            self._row += 1
            self._col = 1
        elif cur == "\n":
            super().advance()
            self._row += 1
            self._col = 1
        else:
            self._col += 1
            super().advance()


@dataclass(frozen=True)
class Segment:
    start: Position
    end: Position


# ==============================================


@dataclass(frozen=True)
class QuotedString(Segment):
    value: str


@dataclass(frozen=True)
class Identifier(Segment):
    value: str


# ================= Keywords ===================


@dataclass(frozen=True)
class Axiom(Segment): ...


@dataclass(frozen=True)
class Is(Segment): ...


@dataclass(frozen=True)
class Or(Segment): ...


@dataclass(frozen=True)
class End(Segment): ...


@dataclass(frozen=True)
class Epsilon(Segment): ...


# ============================================


@dataclass
class EOF: ...


@dataclass(frozen=True)
class ScanError:
    message: str
    pos: Position


Keyword = Axiom | End | Is | Or | Epsilon

Token = QuotedString | Identifier | Keyword | EOF


class Scanner:
    def __init__(self, f: TextIO):
        self._text = TextWithPosition(f)

    def skip_spaces(self):
        while True:
            cur = self._text.peek()
            if cur is None or not cur.isspace():
                return
            self._text.advance()

    def parse_keyword(self):
        cur = self._text.peek()
        assert cur == "`"
        self._text.advance()

    def find_whitespace(self):
        while True:
            cur = self._text.peek()
            if cur is None or cur.isspace():
                break
            self._text.advance()

    def assert_string(self, target: str):
        for i in range(len(target)):
            cur = self._text.peek()
            if cur != target[i]:
                return False
            self._text.advance()
        next = self._text.peek()
        if next is not None and not next.isspace():
            return False
        return True

    def __iter__(self) -> Generator[Token | ScanError, None, None]:
        errored = False
        while True:
            self.skip_spaces()
            cur = self._text.peek()
            if cur is None:
                yield EOF()
                return
            elif cur == "`":
                errored = False  # NOTE: В случае ошибки мы всё равно восстановимся
                start_p = self._text.position()
                self._text.advance()
                cur = self._text.peek()
                if cur == "a":
                    if not self.assert_string("axiom"):
                        err = ScanError(
                            "expected `axiom keyword", self._text.position()
                        )
                        self.find_whitespace()
                        yield err
                    end_p = self._text.position()
                    yield Axiom(start_p, end_p)
                elif cur == "e":
                    if not self.assert_string("end"):
                        err = ScanError("expected `end keyword", self._text.position())
                        self.find_whitespace()
                        yield err
                    end_p = self._text.position()
                    yield End(start_p, end_p)
                elif cur == "i":
                    if not self.assert_string("is"):
                        err = ScanError("expected `is keyword", self._text.position())
                        self.find_whitespace()
                        yield err
                    end_p = self._text.position()
                    yield Is(start_p, end_p)
                elif cur == "o":
                    if not self.assert_string("or"):
                        err = ScanError("expected `or keyword", self._text.position())
                        self.find_whitespace()
                        yield err
                    end_p = self._text.position()
                    yield Or(start_p, end_p)
                elif cur == "e":
                    if not self.assert_string("epsilon"):
                        err = ScanError(
                            "expected `epsilon keyword", self._text.position()
                        )
                        self.find_whitespace()
                        yield err
                    end_p = self._text.position()
                    yield Epsilon(start_p, end_p)
                else:
                    err = ScanError("expected a keyword", self._text.position())
                    self.find_whitespace()
                    yield err
            elif cur == '"':
                start_p = self._text.position()
                value = ""
                self._text.advance()
                while True:
                    cur = self._text.peek()
                    if cur is None or cur in ('"', "\n"):
                        break
                    value += cur
                if cur is None or cur == "\n":
                    yield ScanError(
                        'expected a closing quote (")', self._text.position()
                    )
                    continue
                end_p = self._text.position()
                self._text.advance()
                yield QuotedString(start_p, end_p, value)
                errored = False
                continue
            elif cur.isalpha():
                start_p = self._text.position()
                value = cur
                self._text.advance()
                while True:
                    cur = self._text.peek()
                    if cur is None or not cur.isalnum() or cur not in ("_", "'"):
                        break
                    value += cur
                end_p = self._text.position()
                yield Identifier(start_p, end_p, value)
            else:
                if errored:
                    self._text.advance()
                    continue
                errored = True
                yield ScanError(f"unexpected symbol: {cur}", self._text.position())
                self._text.advance()


NON_TERMINALS = Literal["S'", "S", "Rule", "RuleTail", "RuleAlt"]
# TERMINALS = Type[QuotedString] | Type[Identifier] | Axiom | End | Is
# EPSILON_T = Literal["EPSILON"]
# EPSILON: EPSILON_T = "EPSILON"


class Analyzer:
    def __init__(self, s: Scanner):
        self.scanner = s

    def transitions(self, t: Token):
        match t:
            case QuotedString():
                return {
                    "S'": [],
                    "S": [],
                    "Rule": [],
                    "RuleTail": [],
                    "RuleAlt": [],
                }
            case Identifier():
                ...
            case Axiom():
                ...
            case End():
                ...
            case Is():
                ...
            case Or():
                ...
            case Epsilon():
                ...
            case EOF():
                ...

    def parse(self):
        depth_siblings: DefaultDict[int, list[str]] = defaultdict(lambda: [])

        graph = "digraph {\n"
        c = 1

        init = Node("E", c, [])
        d: Deque[tuple[Node, int]] = deque([(init, 0)])
        for token in self.scanner:
            if len(d) == 0:
                raise RuntimeError(
                    "stack is exhausted, but there are still tokens left!"
                )
            while len(d) > 0:
                # (top, node_name, depth) = d.popleft()
                cur_node, depth = d.popleft()
                depth_siblings[depth].append(cur_node.full_name())
                match cur_node.name:
                    case "n":
                        if type(token) != QuotedString:
                            raise RuntimeError(
                                f"expected Identifier, but {type(token)} found"
                            )
                        break
                    case "(":
                        if type(token) != LeftParen:
                            raise RuntimeError(
                                f"expected LeftParen, but {type(token)} found"
                            )
                        break
                    case "*":
                        if type(token) != Mult:
                            raise RuntimeError(
                                f"expected Mult, but {type(token)} found"
                            )
                        break
                    case "+":
                        if type(token) != Plus:
                            raise RuntimeError(
                                f"expected Plus, but {type(token)} found"
                            )
                        break
                    case ")":
                        if type(token) != RightParen:
                            raise RuntimeError(
                                f"expected RightParen, but {type(token)} found"
                            )
                        break
                    case "$":
                        if type(token) != EOF:
                            raise RuntimeError(f"expected EOF, but {type(token)} found")
                        break
                    case "EPSILON":
                        continue
                    case non_terminal:
                        expected = Analyzer._table[non_terminal]
                        match token:
                            case (
                                Plus()
                                | Mult()
                                | LeftParen()
                                | RightParen()
                                | QuotedString()
                                | EOF()
                            ):
                                rule = expected[type(token)]
                                if len(rule) == 0:
                                    raise RuntimeError(f"unexpected token: {token}")

                                for i, v in enumerate(reversed(rule)):
                                    child = Node(v, c + len(rule) - i, [])
                                    graph += f"\t{cur_node.full_name()}->{child.full_name()}\n"
                                    d.appendleft((child, depth + 1))
                                    cur_node.children.append(child)
                                c += len(rule)
                            case ScanError():
                                raise RuntimeError(f"scanner error: {token}")

        for _, v in depth_siblings.items():
            if len(v) < 2:
                continue
            graph += "\t{ rank=same;"
            graph += f"{' -> '.join(v)}"
            graph += " [style=invis] }\n"

        graph += "}"
        print(graph)
        # return graph
        return init


def main():
    s = Scanner(open("./test.txt"))
    a = Analyzer(s)
    res = a.parse()
    print("==================")
    pprint(res)


if __name__ == "__main__":
    main()
