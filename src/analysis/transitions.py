from typing import Optional, Union
from dataclasses import dataclass

from src.common.abc import IGraphVizible
from src.scanning.scanner import Token, Keyword, Ident, EOF, QuotedStr

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
            # Is
            "KeywordNode",
            "RuleNode",
            "RuleAltNode",
            # End
            "KeywordNode",
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
        Union[
            tuple["QStrNode | IdentNode", "RuleTailNode"],
            # Epsilon
            "KeywordNode",
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
            case _:
                res += self.value.to_graphviz()
                res += f"\t{self.node_name} -> {self.value.node_name}\n"
        return res


@dataclass
class RuleTailNode(IGraphVizible):
    value: Optional[
        Union[
            RuleNode,
            # epsilon
            "KeywordNode",
        ]
    ] = None

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
    value: Optional[
        tuple[
            # Or
            "KeywordNode",
            "RuleNode",
            "RuleAltNode",
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
class AxiomNode(IGraphVizible):
    value: Optional[
        # Axiom
        "KeywordNode"
    ] = None

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


@dataclass
class KeywordNode(IGraphVizible):
    kind: str
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


TERMINAL = KeywordNode | IdentNode | QStrNode | EOFNode

# ===============================================


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
                        KeywordNode(kind="is"),
                        RuleNode(),
                        RuleAltNode(),
                        KeywordNode(kind="end"),
                        ProductionNode(),
                    )
                    current.value = res
                    return list(res)
                case Ident():
                    res = (
                        AxiomNode(),
                        IdentNode(),
                        KeywordNode(kind="is"),
                        RuleNode(),
                        RuleAltNode(),
                        KeywordNode(kind="end"),
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
                    current.value = KeywordNode(kind="epsilon")
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
                    current.value = KeywordNode(kind="epsilon")
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
                    current.value = (KeywordNode(kind="or"), RuleNode(), RuleAltNode())
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
                    current.value = KeywordNode(kind="axiom")
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
        case KeywordNode(kind="axiom"):
            if type(token) != Keyword or token.value != "axiom":
                return f"expected `axiom, {token} found"
            current.value = token
            return None
        case KeywordNode(kind="or"):
            if type(token) != Keyword or token.value != "or":
                return f"expected `or, {token} found"
            current.value = token
            return None
        case KeywordNode(kind="is"):
            if type(token) != Keyword or token.value != "is":
                return f"expected `is, {token} found"
            current.value = token
            return None
        case KeywordNode(kind="epsilon"):
            if type(token) != Keyword or token.value != "epsilon":
                return f"expected `epsilon, {token} found"
            current.value = token
            return None
        case KeywordNode(kind="end"):
            if type(token) != Keyword or token.value != "end":
                return f"expected `end, {token} found"
            current.value = token
            return None
        case KeywordNode(kind=unknown):
            return f"unknown keyword: {unknown}"
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
