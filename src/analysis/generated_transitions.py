# ====================
# |   |(|*|#EOF|)|#Number|+|
# |---|---|---|---|---|---|---|
# |F|( E )|---|---|---|#Number|---|
# |T|F T1|---|---|---|F T1|---|
# |T1|---|* F T1|𝓔|𝓔|---|𝓔|
# |E|T E1|---|---|---|T E1|---|
# |E1|---|---|𝓔|𝓔|---|+ T E1|
# |Init|E #EOF|---|---|---|E #EOF|---|
# 
# ====================
from typing import Optional
from dataclasses import dataclass, field

from src.common.abc import IGraphVizible
from src.common.pretty import wrap
from src.text.processors import Position

from src.scanning.custom_scanner import Token

# every scanner has to provide
from src.scanning.custom_scanner import Keyword

# Token types:
from src.scanning.custom_scanner import EOF, Number

@dataclass
class IASTNode(IGraphVizible):
    pos: Optional[Position] = field(init=False, default=None)

    @property
    def node_label(self) -> str:
        return super().node_label + wrap(f"({str(self.pos)}))")


# ============== NONTERM NODES =============
@dataclass
class FNode(IASTNode):
    value: Optional[tuple["NumberNode"]|tuple["KeywordLeftParenNode", "ENode", "KeywordRightParenNode"]] = None

    def to_graphviz(self) -> str:
        res = super().to_graphviz()
        match self.value:
            case None:
                epsilon_name = f"𝓔{id(self)}"
                res += f'\t{epsilon_name} [label="𝓔"]\n'
                res += f"\t{self.node_name} -> {epsilon_name}\n"
            case tuple():
                res += "".join(child.to_graphviz() for child in self.value)
                res += "".join(
                    f"\t{self.node_name} -> {child.node_name}\n" for child in self.value
                )
                if len(self.value) > 1:
                    res += "\t{{rank=same; {} [style=invis]}}\n".format(
                        " -> ".join(child.node_name for child in self.value)
                    )
        return res

@dataclass
class TNode(IASTNode):
    value: Optional[tuple["FNode", "T1Node"]] = None

    def to_graphviz(self) -> str:
        res = super().to_graphviz()
        match self.value:
            case None:
                epsilon_name = f"𝓔{id(self)}"
                res += f'\t{epsilon_name} [label="𝓔"]\n'
                res += f"\t{self.node_name} -> {epsilon_name}\n"
            case tuple():
                res += "".join(child.to_graphviz() for child in self.value)
                res += "".join(
                    f"\t{self.node_name} -> {child.node_name}\n" for child in self.value
                )
                if len(self.value) > 1:
                    res += "\t{{rank=same; {} [style=invis]}}\n".format(
                        " -> ".join(child.node_name for child in self.value)
                    )
        return res

@dataclass
class T1Node(IASTNode):
    value: Optional[tuple["KeywordAsteriskNode", "FNode", "T1Node"]] = None

    def to_graphviz(self) -> str:
        res = super().to_graphviz()
        match self.value:
            case None:
                epsilon_name = f"𝓔{id(self)}"
                res += f'\t{epsilon_name} [label="𝓔"]\n'
                res += f"\t{self.node_name} -> {epsilon_name}\n"
            case tuple():
                res += "".join(child.to_graphviz() for child in self.value)
                res += "".join(
                    f"\t{self.node_name} -> {child.node_name}\n" for child in self.value
                )
                if len(self.value) > 1:
                    res += "\t{{rank=same; {} [style=invis]}}\n".format(
                        " -> ".join(child.node_name for child in self.value)
                    )
        return res

@dataclass
class ENode(IASTNode):
    value: Optional[tuple["TNode", "E1Node"]] = None

    def to_graphviz(self) -> str:
        res = super().to_graphviz()
        match self.value:
            case None:
                epsilon_name = f"𝓔{id(self)}"
                res += f'\t{epsilon_name} [label="𝓔"]\n'
                res += f"\t{self.node_name} -> {epsilon_name}\n"
            case tuple():
                res += "".join(child.to_graphviz() for child in self.value)
                res += "".join(
                    f"\t{self.node_name} -> {child.node_name}\n" for child in self.value
                )
                if len(self.value) > 1:
                    res += "\t{{rank=same; {} [style=invis]}}\n".format(
                        " -> ".join(child.node_name for child in self.value)
                    )
        return res

@dataclass
class E1Node(IASTNode):
    value: Optional[tuple["KeywordPlusNode", "TNode", "E1Node"]] = None

    def to_graphviz(self) -> str:
        res = super().to_graphviz()
        match self.value:
            case None:
                epsilon_name = f"𝓔{id(self)}"
                res += f'\t{epsilon_name} [label="𝓔"]\n'
                res += f"\t{self.node_name} -> {epsilon_name}\n"
            case tuple():
                res += "".join(child.to_graphviz() for child in self.value)
                res += "".join(
                    f"\t{self.node_name} -> {child.node_name}\n" for child in self.value
                )
                if len(self.value) > 1:
                    res += "\t{{rank=same; {} [style=invis]}}\n".format(
                        " -> ".join(child.node_name for child in self.value)
                    )
        return res

@dataclass
class InitNode(IASTNode):
    value: Optional[tuple["ENode", "EOFNode"]] = None

    def to_graphviz(self) -> str:
        res = super().to_graphviz()
        match self.value:
            case None:
                epsilon_name = f"𝓔{id(self)}"
                res += f'\t{epsilon_name} [label="𝓔"]\n'
                res += f"\t{self.node_name} -> {epsilon_name}\n"
            case tuple():
                res += "".join(child.to_graphviz() for child in self.value)
                res += "".join(
                    f"\t{self.node_name} -> {child.node_name}\n" for child in self.value
                )
                if len(self.value) > 1:
                    res += "\t{{rank=same; {} [style=invis]}}\n".format(
                        " -> ".join(child.node_name for child in self.value)
                    )
        return res

NON_TERMINAL = FNode | TNode | T1Node | ENode | E1Node | InitNode
# ============== TERM NODES =============
@dataclass
class EOFNode(IASTNode):
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

@dataclass
class NumberNode(IASTNode):
    value: Optional[Number] = None


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

# ============== KEYWORD NODES =============
@dataclass
class KeywordRightParenNode(IASTNode):

    value: Optional["Keyword"] = None

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
class KeywordLeftParenNode(IASTNode):

    value: Optional["Keyword"] = None

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
class KeywordPlusNode(IASTNode):

    value: Optional["Keyword"] = None

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
class KeywordAsteriskNode(IASTNode):

    value: Optional["Keyword"] = None

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

TERMINAL = EOFNode | NumberNode | KeywordRightParenNode | KeywordLeftParenNode | KeywordPlusNode | KeywordAsteriskNode
def transitions(
    current: NON_TERMINAL | TERMINAL, token: Token
) -> list[NON_TERMINAL | TERMINAL] | str | None:
    match current:
        case FNode():
            match token:
                case Keyword(value="("):
                    res = (
                        KeywordLeftParenNode(),
                        ENode(),
                        KeywordRightParenNode(),
                    )

                    current.value = res
                    current.pos = token.start
                    return list(res)
                case Keyword(value="*"):
                    return f"unexpected token: {token}" 
                case EOF():
                    return f"unexpected token: {token}" 
                case Keyword(value=")"):
                    return f"unexpected token: {token}" 
                case Number():
                    res = (
                        NumberNode(),
                    )

                    current.value = res
                    current.pos = token.start
                    return list(res)
                case Keyword(value="+"):
                    return f"unexpected token: {token}" 
                case Keyword(value=unexpected):
                    return f"unknown keyword: {unexpected}" 
        case TNode():
            match token:
                case Keyword(value="("):
                    res = (
                        FNode(),
                        T1Node(),
                    )

                    current.value = res
                    current.pos = token.start
                    return list(res)
                case Keyword(value="*"):
                    return f"unexpected token: {token}" 
                case EOF():
                    return f"unexpected token: {token}" 
                case Keyword(value=")"):
                    return f"unexpected token: {token}" 
                case Number():
                    res = (
                        FNode(),
                        T1Node(),
                    )

                    current.value = res
                    current.pos = token.start
                    return list(res)
                case Keyword(value="+"):
                    return f"unexpected token: {token}" 
                case Keyword(value=unexpected):
                    return f"unknown keyword: {unexpected}" 
        case T1Node():
            match token:
                case Keyword(value="("):
                    return f"unexpected token: {token}" 
                case Keyword(value="*"):
                    res = (
                        KeywordAsteriskNode(),
                        FNode(),
                        T1Node(),
                    )

                    current.value = res
                    current.pos = token.start
                    return list(res)
                case EOF():
                    current.pos = token.start
                    return []
                case Keyword(value=")"):
                    current.pos = token.start
                    return []
                case Number():
                    return f"unexpected token: {token}" 
                case Keyword(value="+"):
                    current.pos = token.start
                    return []
                case Keyword(value=unexpected):
                    return f"unknown keyword: {unexpected}" 
        case ENode():
            match token:
                case Keyword(value="("):
                    res = (
                        TNode(),
                        E1Node(),
                    )

                    current.value = res
                    current.pos = token.start
                    return list(res)
                case Keyword(value="*"):
                    return f"unexpected token: {token}" 
                case EOF():
                    return f"unexpected token: {token}" 
                case Keyword(value=")"):
                    return f"unexpected token: {token}" 
                case Number():
                    res = (
                        TNode(),
                        E1Node(),
                    )

                    current.value = res
                    current.pos = token.start
                    return list(res)
                case Keyword(value="+"):
                    return f"unexpected token: {token}" 
                case Keyword(value=unexpected):
                    return f"unknown keyword: {unexpected}" 
        case E1Node():
            match token:
                case Keyword(value="("):
                    return f"unexpected token: {token}" 
                case Keyword(value="*"):
                    return f"unexpected token: {token}" 
                case EOF():
                    current.pos = token.start
                    return []
                case Keyword(value=")"):
                    current.pos = token.start
                    return []
                case Number():
                    return f"unexpected token: {token}" 
                case Keyword(value="+"):
                    res = (
                        KeywordPlusNode(),
                        TNode(),
                        E1Node(),
                    )

                    current.value = res
                    current.pos = token.start
                    return list(res)
                case Keyword(value=unexpected):
                    return f"unknown keyword: {unexpected}" 
        case InitNode():
            match token:
                case Keyword(value="("):
                    res = (
                        ENode(),
                        EOFNode(),
                    )

                    current.value = res
                    current.pos = token.start
                    return list(res)
                case Keyword(value="*"):
                    return f"unexpected token: {token}" 
                case EOF():
                    return f"unexpected token: {token}" 
                case Keyword(value=")"):
                    return f"unexpected token: {token}" 
                case Number():
                    res = (
                        ENode(),
                        EOFNode(),
                    )

                    current.value = res
                    current.pos = token.start
                    return list(res)
                case Keyword(value="+"):
                    return f"unexpected token: {token}" 
                case Keyword(value=unexpected):
                    return f"unknown keyword: {unexpected}" 
        case EOFNode():
            if type(token) != EOF:
                return f"expected EOF, but {type(token)} found" 
            current.value = token
            current.pos = token.start
            return None
        case NumberNode():
            if type(token) != Number:
                return f"expected Number, but {type(token)} found" 
            current.value = token
            current.pos = token.start
            return None
        case KeywordRightParenNode():
            if type(token) != Keyword or token.value != ")":
                return f"expected ), {token} found" 
            current.value = token
            current.pos = token.start
            return None
        case KeywordLeftParenNode():
            if type(token) != Keyword or token.value != "(":
                return f"expected (, {token} found" 
            current.value = token
            current.pos = token.start
            return None
        case KeywordPlusNode():
            if type(token) != Keyword or token.value != "+":
                return f"expected +, {token} found" 
            current.value = token
            current.pos = token.start
            return None
        case KeywordAsteriskNode():
            if type(token) != Keyword or token.value != "*":
                return f"expected *, {token} found" 
            current.value = token
            current.pos = token.start
            return None

