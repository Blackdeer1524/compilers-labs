import abc
from collections import deque
from typing import (
    Deque,
    Generator,
    Optional,
    Sequence,
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


class IGraphVizible(abc.ABC):
    @property
    def node_name(self) -> str:
        return f"{self.__class__.__name__}{id(self)}"

    @abc.abstractmethod
    def to_graphviz(self) -> str:
        return f'\t{self.node_name} [label="{self.__class__.__name__}"]\n'


# ==============================================


@dataclass(frozen=True)
class Term(Segment, IGraphVizible):
    value: str

    def to_graphviz(self) -> str:
        return '\t{} [label="{}"]\n'.format(self.node_name, str(self).replace('"', "'"))


@dataclass(frozen=True)
class NonTerm(Segment, IGraphVizible):
    value: str

    def to_graphviz(self) -> str:
        return '\t{} [label="{}"]\n'.format(self.node_name, str(self).replace('"', "'"))


# ================= Keywords ===================


@dataclass(frozen=True)
class Axiom(Segment, IGraphVizible):
    def to_graphviz(self) -> str:
        return '\t{} [label="{}"]\n'.format(self.node_name, str(self).replace('"', "'"))


@dataclass(frozen=True)
class Is(Segment, IGraphVizible):
    def to_graphviz(self) -> str:
        return '\t{} [label="{}"]\n'.format(self.node_name, str(self).replace('"', "'"))


@dataclass(frozen=True)
class Or(Segment, IGraphVizible):
    def to_graphviz(self) -> str:
        return '\t{} [label="{}"]\n'.format(self.node_name, str(self).replace('"', "'"))


@dataclass(frozen=True)
class End(Segment, IGraphVizible):
    def to_graphviz(self) -> str:
        return '\t{} [label="{}"]\n'.format(self.node_name, str(self).replace('"', "'"))


@dataclass(frozen=True)
class Epsilon(Segment, IGraphVizible):
    def to_graphviz(self) -> str:
        return '\t{} [label="{}"]\n'.format(self.node_name, str(self).replace('"', "'"))


# ============================================


@dataclass(frozen=True)
class EOF(Segment, IGraphVizible):
    def to_graphviz(self) -> str:
        return '\t{} [label="{}"]\n'.format(self.node_name, str(self).replace('"', "'"))


@dataclass(frozen=True)
class ScanError:
    message: str
    pos: Position


Keyword = Axiom | End | Is | Or | Epsilon
Token = Term | NonTerm | Keyword | EOF


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
                errored = False  # NOTE: В случае ошибки мы всё равно восстановимся
                start_p = self._text.position()
                self._text.advance()
                cur = self._text.peek()
                match cur:
                    case "a":
                        if not self.assert_string("axiom"):
                            err = ScanError(
                                "expected `axiom keyword", self._text.position()
                            )
                            self.find_whitespace()
                            yield err
                        end_p = self._text.position()
                        yield Axiom(start_p, end_p)
                    case "e":
                        self._text.advance()
                        cur = self._text.peek()
                        if cur == "n":
                            if not self.assert_string("nd"):
                                err = ScanError(
                                    "expected `end keyword", self._text.position()
                                )
                                self.find_whitespace()
                                yield err
                            end_p = self._text.position()
                            yield End(start_p, end_p)
                        elif cur == "p":
                            if not self.assert_string("psilon"):
                                err = ScanError(
                                    "expected `epsilon keyword", self._text.position()
                                )
                                self.find_whitespace()
                                yield err
                            end_p = self._text.position()
                            yield Epsilon(start_p, end_p)
                        else:
                            err = ScanError(
                                "expected either `end or `epsilon",
                                self._text.position(),
                            )
                            self.find_whitespace()
                            yield err
                    case "i":
                        if not self.assert_string("is"):
                            err = ScanError(
                                "expected `is keyword", self._text.position()
                            )
                            self.find_whitespace()
                            yield err
                        end_p = self._text.position()
                        yield Is(start_p, end_p)
                    case "o":
                        if not self.assert_string("or"):
                            err = ScanError(
                                "expected `or keyword", self._text.position()
                            )
                            self.find_whitespace()
                            yield err
                        end_p = self._text.position()
                        yield Or(start_p, end_p)
                    case _:
                        err = ScanError("expected a keyword", self._text.position())
                        self.find_whitespace()
                        yield err
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
                yield Term(start_p, end_p, value)
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
                yield NonTerm(start_p, end_p, value)
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
        if self.value is None:
            epsilon_name = f"𝓔{id(self)}"
            res += f'\t{epsilon_name} [label="𝓔"]\n'
            res += f"{self.node_name} -> {epsilon_name}"
            return res

        res += self.value[0].to_graphviz()
        res += self.value[1].to_graphviz()

        res += f"\t{self.node_name} -> {self.value[0].node_name}"
        res += f"\t{self.node_name} -> {self.value[1].node_name}"
        return res


@dataclass
class ProductionNode(IGraphVizible):
    value: Optional[
        tuple[
            "AxiomNode",
            "NonTermNode",
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
                return res
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
        Union[tuple["TermNode | NonTermNode", "RuleTailNode"], "KWEpsilonNode"]
    ] = None

    def to_graphviz(self) -> str:
        res = super().to_graphviz()
        match self.value:
            case None:
                epsilon_name = f"𝓔{id(self)}"
                res += f'\t{epsilon_name} [label="𝓔"]\n'
                res += f"{self.node_name} -> {epsilon_name}"
                return res
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
                return res
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
                return res
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
                return res
            case _:
                res += self.value.to_graphviz()
                res += f"\t{self.node_name} -> {self.value.node_name}\n"
        return res


NON_TERMINAL = (
    InitNode | ProductionNode | RuleNode | RuleTailNode | RuleAltNode | AxiomNode
)

# ================== KEYWORDS ==============


@dataclass
class KWAxiomNode(IGraphVizible):
    value: Optional[Axiom] = None

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


@dataclass
class KWOrNode(IGraphVizible):
    value: Optional[Or] = None

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


@dataclass
class KWIsNode(IGraphVizible):
    value: Optional[Is] = None

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


@dataclass
class KWEpsilonNode(IGraphVizible):
    value: Optional[Epsilon] = None

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


@dataclass
class KWEndNode(IGraphVizible):
    value: Optional[End] = None

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


KEYWORDS = KWAxiomNode | KWOrNode | KWIsNode | KWEpsilonNode | KWEndNode

# =============== TERMINALS =================


@dataclass
class NonTermNode(IGraphVizible):
    value: Optional[NonTerm] = None

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


@dataclass
class TermNode(IGraphVizible):
    value: Optional[Term] = None

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


TERMINAL = KEYWORDS | NonTermNode | TermNode | EOFNode

# ===============================================


class Analyzer:
    def __init__(self, s: Scanner):
        self.scanner = s

    @staticmethod
    def transitions(
        current: NON_TERMINAL, token: Token
    ) -> Sequence[NON_TERMINAL | TERMINAL] | None:
        match current:
            case InitNode():
                match token:
                    case Axiom():
                        (prod, eof) = (ProductionNode(), EOFNode())
                        current.value = (prod, eof)
                        return [prod, eof]
                    case NonTerm():
                        (prod, eof) = (ProductionNode(), EOFNode())
                        current.value = (prod, eof)
                        return [prod, eof]
                    case Term():
                        return None
                    case Or():
                        return None
                    case Is():
                        return None
                    case Epsilon():
                        return None
                    case End():
                        return None
                    case EOF():
                        (prod, eof) = (ProductionNode(), EOFNode())
                        current.value = (prod, eof)
                        return [prod, eof]
            case ProductionNode():
                match token:
                    case Axiom():
                        res = (
                            AxiomNode(),
                            NonTermNode(),
                            KWIsNode(),
                            RuleNode(),
                            RuleAltNode(),
                            KWEndNode(),
                            ProductionNode(),
                        )
                        current.value = res
                        return res
                    case NonTerm():
                        res = (
                            AxiomNode(),
                            NonTermNode(),
                            KWIsNode(),
                            RuleNode(),
                            RuleAltNode(),
                            KWEndNode(),
                            ProductionNode(),
                        )
                        current.value = res
                        return res
                    case Term():
                        return None
                    case Or():
                        return None
                    case Is():
                        return None
                    case Epsilon():
                        return None
                    case End():
                        return None
                    case EOF():
                        return []
            case RuleNode():
                match token:
                    case Axiom():
                        return None
                    case NonTerm():
                        nt = NonTermNode()
                        tail = RuleTailNode()
                        current.value = (nt, tail)
                        return [nt, tail]
                    case Term():
                        t = TermNode()
                        tail = RuleTailNode()
                        current.value = (t, tail)
                        return [t, tail]
                    case Or():
                        return None
                    case Is():
                        return None
                    case Epsilon():
                        current.value = KWEpsilonNode()
                        return [current.value]
                    case End():
                        return None
                    case EOF():
                        return None
            case RuleTailNode():
                match token:
                    case Axiom():
                        return None
                    case NonTerm():
                        current.value = RuleNode()
                        return [current.value]
                    case Term():
                        current.value = RuleNode()
                        return [current.value]
                    case Or():
                        return []
                    case Is():
                        return None
                    case Epsilon():
                        current.value = KWEpsilonNode()
                        return [current.value]
                    case End():
                        return []
                    case EOF():
                        return None
            case RuleAltNode():
                match token:
                    case Axiom():
                        return None
                    case NonTerm():
                        return None
                    case Term():
                        return None
                    case Or():
                        current.value = (KWOrNode(), RuleNode(), RuleAltNode())
                        return [current.value[0], current.value[1], current.value[2]]
                    case Is():
                        return None
                    case Epsilon():
                        return None
                    case End():
                        return []
                    case EOF():
                        return None
            case AxiomNode():
                match token:
                    case Axiom():
                        current.value = KWAxiomNode()
                        return [current.value]
                    case NonTerm():
                        return []
                    case Term():
                        return None
                    case Or():
                        return None
                    case Is():
                        return None
                    case Epsilon():
                        return None
                    case End():
                        return None
                    case EOF():
                        return None

    @dataclass
    class Node:
        name: NON_TERMINAL | TERMINAL
        index: int
        children: list["Analyzer.Node"]
        token: Token | None

        def full_name(self) -> str:
            res = f'"{self.name}[{self.index}]"'
            if self.token is not None:
                res += str(self.token)
            return res

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
                match cur_node:
                    case KWAxiomNode():
                        if type(token) != Axiom:
                            raise RuntimeError(
                                f"expected Axiom, but {type(token)} found"
                            )
                        cur_node.value = token
                        break
                    case KWOrNode():
                        if type(token) != Or:
                            raise RuntimeError(f"expected Or, but {type(token)} found")
                        cur_node.value = token
                        break
                    case KWIsNode():
                        if type(token) != Is:
                            raise RuntimeError(f"expected Is, but {type(token)} found")
                        cur_node.value = token
                        break
                    case KWEpsilonNode():
                        if type(token) != Epsilon:
                            raise RuntimeError(
                                f"expected Epsilon, but {type(token)} found"
                            )
                        cur_node.value = token
                        break
                    case KWEndNode():
                        if type(token) != End:
                            raise RuntimeError(
                                f"expected RightParen, but {type(token)} found"
                            )
                        cur_node.value = token
                        break
                    case NonTermNode():
                        if type(token) != NonTerm:
                            raise RuntimeError(
                                f"expected NonTerm, but {type(token)} found"
                            )
                        cur_node.value = token
                        break
                    case TermNode():
                        if type(token) != Term:
                            raise RuntimeError(
                                f"expected Term, but {type(token)} found"
                            )
                        cur_node.value = token
                        break
                    case EOFNode():
                        if type(token) != EOF:
                            raise RuntimeError(f"expected EOF, but {type(token)} found")
                        cur_node.value = token
                        break
                    case non_terminal:
                        match token:
                            case ScanError():
                                raise RuntimeError(f"scanner error: {token}")
                            case _:
                                rule = Analyzer.transitions(non_terminal, token)
                                if rule is None:
                                    raise RuntimeError(f"unexpected token: {token}")

                                for v in reversed(rule):
                                    d.appendleft((v, depth + 1))
        return init


def main():
    s = Scanner(open("./test.txt"))
    a = Analyzer(s)
    res = a.parse()
    print("digraph {")
    print(res.to_graphviz())
    print("}")


if __name__ == "__main__":
    main()
