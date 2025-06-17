import abc
from collections import deque
from typing import (
    Deque,
    Generator,
    Optional,
    TextIO,
    Union,
)
from dataclasses import dataclass


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


def wrap(s: str, lim: int = 20) -> str:
    # res = pformat(s, width=20)
    # return res.replace("\n", "\\n")
    """
    Wrap the input string s so that no line is longer than lim.
    Breaks at whitespace where possible; words longer than lim are split.
    """
    words = s.split(sep=" ")
    lines: list[str] = []
    current: str = ""

    for word in words:
        # If adding the next word would exceed the limit...
        if current:
            sep = " "
            projected_length = len(current) + 1 + len(word)
        else:
            sep = ""
            projected_length = len(word)

        if projected_length <= lim:
            # Safe to add the word to current line
            current += sep + word
        else:
            # Current line is full—push it
            if current:
                lines.append(current)
            # If the word itself is too long, split it
            while len(word) > lim:
                lines.append(word[:lim])
                word = word[lim:]
            current = word

    # Don't forget the last line
    if current:
        lines.append(current)

    return "\r".join(lines)


class IGraphVizible(abc.ABC):
    @property
    def node_name(self) -> str:
        return f"{self.__class__.__name__}{id(self)}"

    @abc.abstractmethod
    def to_graphviz(self) -> str:
        return f'\t{self.node_name} [label="{self.__class__.__name__}"]\n'


# ==============================================


@dataclass(frozen=True)
class QuotedStr(Segment, IGraphVizible):
    value: str

    def to_graphviz(self) -> str:
        return '\t{} [label="{}"]\n'.format(
            self.node_name, wrap(str(self)).replace('"', "'")
        )


@dataclass(frozen=True)
class Ident(Segment, IGraphVizible):
    value: str

    def to_graphviz(self) -> str:
        return '\t{} [label="{}"]\n'.format(
            self.node_name, wrap(str(self)).replace('"', "'")
        )


@dataclass(frozen=True)
class Keyword(Segment, IGraphVizible):
    value: str

    def to_graphviz(self) -> str:
        return '\t{} [label="{}"]\n'.format(
            self.node_name, wrap(str(self)).replace('"', "'")
        )


@dataclass(frozen=True)
class EOF(Segment, IGraphVizible):
    def to_graphviz(self) -> str:
        return '\t{} [label="{}"]\n'.format(
            self.node_name, wrap(str(self)).replace('"', "'")
        )


@dataclass(frozen=True)
class ScanError:
    message: str
    pos: Position


Token = QuotedStr | Ident | Keyword | EOF


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
                yield EOF(self._text.position(), self._text.position())
                return
            elif cur == "`":
                start_p = self._text.position()
                errored = False
                self._text.advance()
                value = ""
                while True:
                    cur = self._text.peek()
                    if cur is None or cur.isspace():
                        break
                    value += cur
                    self._text.advance()
                end_p = self._text.position()
                yield Keyword(start_p, end_p, value)
            elif cur == '"':
                start_p = self._text.position()
                value = ""
                self._text.advance()
                allow_special = False
                while True:
                    cur = self._text.peek()
                    if cur is None or cur == "\n":
                        break

                    if allow_special:
                        if cur == '"':
                            value += '"'
                        elif cur == "\\":
                            value += "\\"
                        else:
                            value += f"\\{cur}"
                            yield ScanError(
                                f"unknown special symbol: \\{cur}",
                                self._text.position(),
                            )
                        allow_special = False
                    else:
                        if cur == '"':
                            break

                        if cur == "\\":
                            allow_special = True
                        else:
                            value += cur

                    self._text.advance()
                if cur is None or cur == "\n":
                    yield ScanError(
                        'expected a closing quote (")', self._text.position()
                    )
                    continue
                end_p = self._text.position()
                self._text.advance()
                yield QuotedStr(start_p, end_p, value)
                errored = False
                continue
            elif cur.isalpha():
                start_p = self._text.position()
                value = cur
                self._text.advance()
                while True:
                    cur = self._text.peek()
                    if cur is None or (not cur.isalnum() and cur not in ("_", "'")):
                        break
                    value += cur
                    self._text.advance()
                end_p = self._text.position()
                yield Ident(start_p, end_p, value)
            else:
                if errored:
                    self._text.advance()
                    continue
                errored = True
                yield ScanError(f"unexpected symbol: {cur}", self._text.position())
                self._text.advance()


# NON_TERMINAL = Literal["S'", "Production", "Axiom", "Rule", "RuleTail", "RuleAlt"]
# KEYWORD = Literal["KW_Axiom", "KW_Or", "KW_Is", "KW_Epsilon", "KW_End"]
# TERMINAL = KEYWORD | Literal["NT", "T", "$"]

# ================== AST NODES ==================

# ================ Non-Terminals ================


@dataclass
class InitNode(IGraphVizible):
    value: Optional[tuple["ProductionNode", "EOFNode"]] = None

    def to_graphviz(self) -> str:
        res = super().to_graphviz()
        match self.value:
            case None:
                epsilon_name = f"𝓔{id(self)}"
                res += f'\t{epsilon_name} [label="𝓔"]\n'
                res += f"{self.node_name} -> {epsilon_name}"
            case tuple():
                res += "".join(child.to_graphviz() for child in self.value)
                res += "".join(
                    f"\t{self.node_name} -> {child.node_name}\n" for child in self.value
                )
                res += "\t{{rank=same; {} [style=invis]}}\n".format(
                    " -> ".join(child.node_name for child in self.value)
                )
        return res


@dataclass
class ProductionNode(IGraphVizible):
    value: Optional[
        tuple[
            "AxiomNode",
            "IdentNode",
            "KWIsNode",
            "RuleNode",
            "RuleAltNode",
            "KWEndNode",
            "ProductionNode",
        ]
    ] = None

    def to_graphviz(self) -> str:
        res = super().to_graphviz()
        match self.value:
            case None:
                epsilon_name = f"𝓔{id(self)}"
                res += f'\t{epsilon_name} [label="𝓔"]\n'
                res += f"{self.node_name} -> {epsilon_name}"
            case tuple():
                res += "".join(child.to_graphviz() for child in self.value)
                res += "".join(
                    f"\t{self.node_name} -> {child.node_name}\n" for child in self.value
                )
                res += "\t{{rank=same; {} [style=invis]}}\n".format(
                    " -> ".join(child.node_name for child in self.value)
                )
        return res


@dataclass
class RuleNode(IGraphVizible):
    value: Optional[
        Union[tuple["QStrNode | IdentNode", "RuleTailNode"], "KWEpsilonNode"]
    ] = None

    def to_graphviz(self) -> str:
        res = super().to_graphviz()
        match self.value:
            case None:
                epsilon_name = f"𝓔{id(self)}"
                res += f'\t{epsilon_name} [label="𝓔"]\n'
                res += f"{self.node_name} -> {epsilon_name}"
            case tuple():
                res += "".join(child.to_graphviz() for child in self.value)
                res += "".join(
                    f"\t{self.node_name} -> {child.node_name}\n" for child in self.value
                )
                res += "\t{{rank=same; {} [style=invis]}}\n".format(
                    " -> ".join(child.node_name for child in self.value)
                )
            case _:
                res += self.value.to_graphviz()
                res += f"\t{self.node_name} -> {self.value.node_name}\n"
        return res


@dataclass
class RuleTailNode(IGraphVizible):
    value: Optional[Union[RuleNode, "KWEpsilonNode"]] = None

    def to_graphviz(self) -> str:
        res = super().to_graphviz()
        match self.value:
            case None:
                epsilon_name = f"𝓔{id(self)}"
                res += f'\t{epsilon_name} [label="𝓔"]\n'
                res += f"{self.node_name} -> {epsilon_name}"
            case _:
                res += self.value.to_graphviz()
                res += f"\t{self.node_name} -> {self.value.node_name}\n"
        return res


@dataclass
class RuleAltNode(IGraphVizible):
    value: Optional[tuple["KWOrNode", "RuleNode", "RuleAltNode"]] = None

    def to_graphviz(self) -> str:
        res = super().to_graphviz()
        match self.value:
            case None:
                epsilon_name = f"𝓔{id(self)}"
                res += f'\t{epsilon_name} [label="𝓔"]\n'
                res += f"{self.node_name} -> {epsilon_name}"
            case tuple():
                res += "".join(child.to_graphviz() for child in self.value)
                res += "".join(
                    f"\t{self.node_name} -> {child.node_name}\n" for child in self.value
                )
                res += "\t{{rank=same; {} [style=invis]}}\n".format(
                    " -> ".join(child.node_name for child in self.value)
                )
        return res


@dataclass
class AxiomNode(IGraphVizible):
    value: Optional["KWAxiomNode"] = None

    def to_graphviz(self) -> str:
        res = super().to_graphviz()
        match self.value:
            case None:
                epsilon_name = f"𝓔{id(self)}"
                res += f'\t{epsilon_name} [label="𝓔"]\n'
                res += f"{self.node_name} -> {epsilon_name}"
            case _:
                res += self.value.to_graphviz()
                res += f"\t{self.node_name} -> {self.value.node_name}\n"
        return res


NON_TERMINAL = (
    InitNode | ProductionNode | RuleNode | RuleTailNode | RuleAltNode | AxiomNode
)

# ================== KEYWORDS ==============


class KWAxiomNode(IGraphVizible):
    value: Optional[Keyword] = None

    def to_graphviz(self) -> str:
        res = super().to_graphviz()
        match self.value:
            case None:
                epsilon_name = f"𝓔{id(self)}"
                res += f'\t{epsilon_name} [label="𝓔"]\n'
                res += f"{self.node_name} -> {epsilon_name}"
            case _:
                res += self.value.to_graphviz()
                res += f"\t{self.node_name} -> {self.value.node_name}\n"
        return res


@dataclass
class KWOrNode(IGraphVizible):
    value: Optional[Keyword] = None

    def to_graphviz(self) -> str:
        res = super().to_graphviz()
        match self.value:
            case None:
                epsilon_name = f"𝓔{id(self)}"
                res += f'\t{epsilon_name} [label="𝓔"]\n'
                res += f"{self.node_name} -> {epsilon_name}"
            case _:
                res += self.value.to_graphviz()
                res += f"\t{self.node_name} -> {self.value.node_name}\n"
        return res


@dataclass
class KWIsNode(IGraphVizible):
    value: Optional[Keyword] = None

    def to_graphviz(self) -> str:
        res = super().to_graphviz()
        match self.value:
            case None:
                epsilon_name = f"𝓔{id(self)}"
                res += f'\t{epsilon_name} [label="𝓔"]\n'
                res += f"{self.node_name} -> {epsilon_name}"
            case _:
                res += self.value.to_graphviz()
                res += f"\t{self.node_name} -> {self.value.node_name}\n"
        return res


@dataclass
class KWEpsilonNode(IGraphVizible):
    value: Optional[Keyword] = None

    def to_graphviz(self) -> str:
        res = super().to_graphviz()
        match self.value:
            case None:
                epsilon_name = f"𝓔{id(self)}"
                res += f'\t{epsilon_name} [label="𝓔"]\n'
                res += f"{self.node_name} -> {epsilon_name}"
            case _:
                res += self.value.to_graphviz()
                res += f"\t{self.node_name} -> {self.value.node_name}\n"
        return res


@dataclass
class KWEndNode(IGraphVizible):
    value: Optional[Keyword] = None

    def to_graphviz(self) -> str:
        res = super().to_graphviz()
        match self.value:
            case None:
                epsilon_name = f"𝓔{id(self)}"
                res += f'\t{epsilon_name} [label="𝓔"]\n'
                res += f"{self.node_name} -> {epsilon_name}"
            case _:
                res += self.value.to_graphviz()
                res += f"\t{self.node_name} -> {self.value.node_name}\n"
        return res


KEYWORDS = KWAxiomNode | KWOrNode | KWIsNode | KWEpsilonNode | KWEndNode


# =============== TERMINALS =================


@dataclass
class IdentNode(IGraphVizible):
    value: Optional[Ident] = None

    def to_graphviz(self) -> str:
        res = super().to_graphviz()
        match self.value:
            case None:
                epsilon_name = f"𝓔{id(self)}"
                res += f'\t{epsilon_name} [label="𝓔"]\n'
                res += f"{self.node_name} -> {epsilon_name}"
            case _:
                res += self.value.to_graphviz()
                res += f"\t{self.node_name} -> {self.value.node_name}\n"
        return res


@dataclass
class QStrNode(IGraphVizible):
    value: Optional[QuotedStr] = None

    def to_graphviz(self) -> str:
        res = super().to_graphviz()
        match self.value:
            case None:
                epsilon_name = f"𝓔{id(self)}"
                res += f'\t{epsilon_name} [label="𝓔"]\n'
                res += f"{self.node_name} -> {epsilon_name}"
            case _:
                res += self.value.to_graphviz()
                res += f"\t{self.node_name} -> {self.value.node_name}\n"
        return res


@dataclass
class EOFNode(IGraphVizible):
    value: Optional[EOF] = None

    def to_graphviz(self) -> str:
        res = super().to_graphviz()
        match self.value:
            case None:
                epsilon_name = f"𝓔{id(self)}"
                res += f'\t{epsilon_name} [label="𝓔"]\n'
                res += f"{self.node_name} -> {epsilon_name}"
                return res
            case _:
                res += self.value.to_graphviz()
                res += f"\t{self.node_name} -> {self.value.node_name}\n"
        return res


TERMINAL = KEYWORDS | IdentNode | QStrNode | EOFNode

# ===============================================


class Analyzer:
    def __init__(self, s: Scanner):
        self.scanner = s

    @staticmethod
    def transitions(
        current: NON_TERMINAL | TERMINAL, token: Token
    ) -> list[NON_TERMINAL | TERMINAL] | str | None:
        match current:
            case InitNode():
                match token:
                    case Keyword(value="axiom"):
                        (prod, eof) = (ProductionNode(), EOFNode())
                        current.value = (prod, eof)
                        return [prod, eof]
                    case Ident():
                        (prod, eof) = (ProductionNode(), EOFNode())
                        current.value = (prod, eof)
                        return [prod, eof]
                    case QuotedStr():
                        return f"unexpected token: {token}"
                    case Keyword(value="or"):
                        return f"unexpected token: {token}"
                    case Keyword(value="is"):
                        return f"unexpected token: {token}"
                    case Keyword(value="epsilon"):
                        return f"unexpected token: {token}"
                    case Keyword(value="end"):
                        return f"unexpected token: {token}"
                    case Keyword(value=other):
                        return f"unknown keyword: {other}"
                    case EOF():
                        (prod, eof) = (ProductionNode(), EOFNode())
                        current.value = (prod, eof)
                        return [prod, eof]
            case ProductionNode():
                match token:
                    case Keyword(value="axiom"):
                        res = (
                            AxiomNode(),
                            IdentNode(),
                            KWIsNode(),
                            RuleNode(),
                            RuleAltNode(),
                            KWEndNode(),
                            ProductionNode(),
                        )
                        current.value = res
                        return list(res)
                    case Ident():
                        res = (
                            AxiomNode(),
                            IdentNode(),
                            KWIsNode(),
                            RuleNode(),
                            RuleAltNode(),
                            KWEndNode(),
                            ProductionNode(),
                        )
                        current.value = res
                        return list(res)
                    case QuotedStr():
                        return f"unexpected token: {token}"
                    case Keyword(value="or"):
                        return f"unexpected token: {token}"
                    case Keyword(value="is"):
                        return f"unexpected token: {token}"
                    case Keyword(value="epsilon"):
                        return f"unexpected token: {token}"
                    case Keyword(value="end"):
                        return f"unexpected token: {token}"
                    case Keyword(value=other):
                        return f"unknown keyword: {other}"
                    case EOF():
                        return []
            case RuleNode():
                match token:
                    case Keyword(value="axiom"):
                        return f"unexpected token: {token}"
                    case Ident():
                        nt = IdentNode()
                        tail = RuleTailNode()
                        current.value = (nt, tail)
                        return [nt, tail]
                    case QuotedStr():
                        t = QStrNode()
                        tail = RuleTailNode()
                        current.value = (t, tail)
                        return [t, tail]
                    case Keyword(value="or"):
                        return f"unexpected token: {token}"
                    case Keyword(value="is"):
                        return f"unexpected token: {token}"
                    case Keyword(value="epsilon"):
                        current.value = KWEpsilonNode()
                        return [current.value]
                    case Keyword(value="end"):
                        return f"unexpected token: {token}"
                    case Keyword(value=other):
                        return f"unknown keyword: {other}"
                    case EOF():
                        return f"unexpected token: {token}"
            case RuleTailNode():
                match token:
                    case Keyword(value="axiom"):
                        return f"unexpected token: {token}"
                    case Ident():
                        current.value = RuleNode()
                        return [current.value]
                    case QuotedStr():
                        current.value = RuleNode()
                        return [current.value]
                    case Keyword(value="or"):
                        return []
                    case Keyword(value="is"):
                        return f"unexpected token: {token}"
                    case Keyword(value="epsilon"):
                        current.value = KWEpsilonNode()
                        return [current.value]
                    case Keyword(value="end"):
                        return []
                    case Keyword(value=other):
                        return f"unknown keyword: {other}"
                    case EOF():
                        return f"unexpected token: {token}"
            case RuleAltNode():
                match token:
                    case Keyword(value="axiom"):
                        return f"unexpected token: {token}"
                    case Ident():
                        return f"unexpected token: {token}"
                    case QuotedStr():
                        return f"unexpected token: {token}"
                    case Keyword(value="or"):
                        current.value = (KWOrNode(), RuleNode(), RuleAltNode())
                        return [current.value[0], current.value[1], current.value[2]]
                    case Keyword(value="is"):
                        return f"unexpected token: {token}"
                    case Keyword(value="epsilon"):
                        return f"unexpected token: {token}"
                    case Keyword(value="end"):
                        return []
                    case Keyword(value=other):
                        return f"unknown keyword: {other}"
                    case EOF():
                        return f"unexpected token: {token}"
            case AxiomNode():
                match token:
                    case Keyword(value="axiom"):
                        current.value = KWAxiomNode()
                        return [current.value]
                    case Ident():
                        return []
                    case QuotedStr():
                        return f"unexpected token: {token}"
                    case Keyword(value="or"):
                        return f"unexpected token: {token}"
                    case Keyword(value="is"):
                        return f"unexpected token: {token}"
                    case Keyword(value="epsilon"):
                        return f"unexpected token: {token}"
                    case Keyword(value="end"):
                        return f"unexpected token: {token}"
                    case Keyword(value=other):
                        return f"unknown keyword: {other}"
                    case EOF():
                        return f"unexpected token: {token}"
            case KWAxiomNode():
                if type(token) != Keyword or token.value != "axiom":
                    return f"expected `axiom, {token} found"
                current.value = token
                return None
            case KWOrNode():
                if type(token) != Keyword or token.value != "or":
                    return f"expected `or, {token} found"
                current.value = token
                return None
            case KWIsNode():
                if type(token) != Keyword or token.value != "is":
                    return f"expected `is, {token} found"
                current.value = token
                return None
            case KWEpsilonNode():
                if type(token) != Keyword or token.value != "epsilon":
                    return f"expected `epsilon, {token} found"
                current.value = token
                return None
            case KWEndNode():
                if type(token) != Keyword or token.value != "end":
                    return f"expected `end, {token} found"
                current.value = token
                return None
            case IdentNode():
                if type(token) != Ident:
                    return f"expected NonTerm, but {type(token)} found"
                current.value = token
                return None
            case QStrNode():
                if type(token) != QuotedStr:
                    return f"expected Term, but {type(token)} found"
                current.value = token
                return None
            case EOFNode():
                if type(token) != EOF:
                    return f"expected EOF, but {type(token)} found"
                current.value = token
                return None

    def parse(self):
        init = InitNode()
        d: Deque[tuple[TERMINAL | NON_TERMINAL, int]] = deque([(init, 0)])
        for token in self.scanner:
            if len(d) == 0:
                raise RuntimeError(
                    "stack is exhausted, but there are still tokens left!"
                )
            while len(d) > 0:
                cur_node, depth = d.popleft()
                match token:
                    case ScanError():
                        raise RuntimeError(f"scanner error: {token}")
                    case _:
                        rule = Analyzer.transitions(cur_node, token)
                        match rule:
                            case None:
                                break
                            case str():
                                raise RuntimeError(rule)
                            case list():
                                for v in reversed(rule):
                                    d.appendleft((v, depth + 1))
        return init


def main():
    s = Scanner(open("./test.txt"))
    a = Analyzer(s)
    res = a.parse()
    print("digraph {")
    print(res.to_graphviz().replace("\r", "\\n"))
    print("}")


if __name__ == "__main__":
    main()
