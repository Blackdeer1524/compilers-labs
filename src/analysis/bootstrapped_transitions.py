# ====================
# |   |#Ident|#EOF|`end|`axiom|`epsilon|`is|`or|#QuotedStr|
# |---|---|---|---|---|---|---|---|---|
# |Production|Axiom NonTerm `is Rule RuleAlt `end Production|𝓔|---|Axiom NonTerm `is Rule RuleAlt `end Production|---|---|---|---|
# |Rule|NonTerm RuleTail|---|---|---|`epsilon|---|---|Term RuleTail|
# |RuleTail|NonTerm RuleTail|---|𝓔|---|---|---|𝓔|Term RuleTail|
# |RuleAlt|---|---|𝓔|---|---|---|`or Rule RuleAlt|---|
# |Axiom|𝓔|---|---|`axiom|---|---|---|---|
# |NonTerm|#Ident|---|---|---|---|---|---|---|
# |Term|---|---|---|---|---|---|---|#QuotedStr|
# |Init|Production #EOF|Production #EOF|---|Production #EOF|---|---|---|---|
# ====================
from typing import Optional
from dataclasses import dataclass, field

from src.common.abc import IGraphVizible
from src.common.pretty import wrap
from src.text.processors import Position

from src.scanning.scanner import Token

# every scanner has to provide
from src.scanning.scanner import Keyword

# Token types:
from src.scanning.scanner import EOF, Ident, QuotedStr

@dataclass
class IASTNode(IGraphVizible):
    pos: Optional[Position] = field(init=False, default=None)

    @property
    def node_label(self) -> str:
        return super().node_label + wrap(f"({str(self.pos)}))")


# ============== NONTERM NODES =============
@dataclass
class ProductionNode(IASTNode):
    value: Optional[tuple["AxiomNode", "NonTermNode", "KeywordBacktickisNode", "RuleNode", "RuleAltNode", "KeywordBacktickendNode", "ProductionNode"]] = None

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
class RuleNode(IASTNode):
    value: Optional[tuple["TermNode", "RuleTailNode"]|tuple["NonTermNode", "RuleTailNode"]|tuple["KeywordBacktickepsilonNode"]] = None

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
class RuleTailNode(IASTNode):
    value: Optional[tuple["TermNode", "RuleTailNode"]|tuple["NonTermNode", "RuleTailNode"]] = None

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
class RuleAltNode(IASTNode):
    value: Optional[tuple["KeywordBacktickorNode", "RuleNode", "RuleAltNode"]] = None

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
class AxiomNode(IASTNode):
    value: Optional[tuple["KeywordBacktickaxiomNode"]] = None

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
class NonTermNode(IASTNode):
    value: Optional[tuple["IdentNode"]] = None

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
class TermNode(IASTNode):
    value: Optional[tuple["QuotedStrNode"]] = None

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
    value: Optional[tuple["ProductionNode", "EOFNode"]] = None

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

NON_TERMINAL = ProductionNode | RuleNode | RuleTailNode | RuleAltNode | AxiomNode | NonTermNode | TermNode | InitNode
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
class IdentNode(IASTNode):
    value: Optional[Ident] = None


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
class QuotedStrNode(IASTNode):
    value: Optional[QuotedStr] = None


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
class KeywordBacktickendNode(IASTNode):

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
class KeywordBacktickaxiomNode(IASTNode):

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
class KeywordBacktickepsilonNode(IASTNode):

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
class KeywordBacktickisNode(IASTNode):

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
class KeywordBacktickorNode(IASTNode):

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

TERMINAL = EOFNode | IdentNode | QuotedStrNode | KeywordBacktickendNode | KeywordBacktickaxiomNode | KeywordBacktickepsilonNode | KeywordBacktickisNode | KeywordBacktickorNode
def transitions(
    current: NON_TERMINAL | TERMINAL, token: Token
) -> list[NON_TERMINAL | TERMINAL] | str | None:
    match current:
        case ProductionNode():
            match token:
                case Ident():
                    res = (
                        AxiomNode(),
                        NonTermNode(),
                        KeywordBacktickisNode(),
                        RuleNode(),
                        RuleAltNode(),
                        KeywordBacktickendNode(),
                        ProductionNode(),
                    )

                    current.value = res
                    current.pos = token.start
                    return list(res)
                case EOF():
                    current.pos = token.start
                    return []
                case Keyword(value="`end"):
                    return f"unexpected token: {token}" 
                case Keyword(value="`axiom"):
                    res = (
                        AxiomNode(),
                        NonTermNode(),
                        KeywordBacktickisNode(),
                        RuleNode(),
                        RuleAltNode(),
                        KeywordBacktickendNode(),
                        ProductionNode(),
                    )

                    current.value = res
                    current.pos = token.start
                    return list(res)
                case Keyword(value="`epsilon"):
                    return f"unexpected token: {token}" 
                case Keyword(value="`is"):
                    return f"unexpected token: {token}" 
                case Keyword(value="`or"):
                    return f"unexpected token: {token}" 
                case QuotedStr():
                    return f"unexpected token: {token}" 
                case Keyword(value=unexpected):
                    return f"unknown keyword: {unexpected}" 
        case RuleNode():
            match token:
                case Ident():
                    res = (
                        NonTermNode(),
                        RuleTailNode(),
                    )

                    current.value = res
                    current.pos = token.start
                    return list(res)
                case EOF():
                    return f"unexpected token: {token}" 
                case Keyword(value="`end"):
                    return f"unexpected token: {token}" 
                case Keyword(value="`axiom"):
                    return f"unexpected token: {token}" 
                case Keyword(value="`epsilon"):
                    res = (
                        KeywordBacktickepsilonNode(),
                    )

                    current.value = res
                    current.pos = token.start
                    return list(res)
                case Keyword(value="`is"):
                    return f"unexpected token: {token}" 
                case Keyword(value="`or"):
                    return f"unexpected token: {token}" 
                case QuotedStr():
                    res = (
                        TermNode(),
                        RuleTailNode(),
                    )

                    current.value = res
                    current.pos = token.start
                    return list(res)
                case Keyword(value=unexpected):
                    return f"unknown keyword: {unexpected}" 
        case RuleTailNode():
            match token:
                case Ident():
                    res = (
                        NonTermNode(),
                        RuleTailNode(),
                    )

                    current.value = res
                    current.pos = token.start
                    return list(res)
                case EOF():
                    return f"unexpected token: {token}" 
                case Keyword(value="`end"):
                    current.pos = token.start
                    return []
                case Keyword(value="`axiom"):
                    return f"unexpected token: {token}" 
                case Keyword(value="`epsilon"):
                    return f"unexpected token: {token}" 
                case Keyword(value="`is"):
                    return f"unexpected token: {token}" 
                case Keyword(value="`or"):
                    current.pos = token.start
                    return []
                case QuotedStr():
                    res = (
                        TermNode(),
                        RuleTailNode(),
                    )

                    current.value = res
                    current.pos = token.start
                    return list(res)
                case Keyword(value=unexpected):
                    return f"unknown keyword: {unexpected}" 
        case RuleAltNode():
            match token:
                case Ident():
                    return f"unexpected token: {token}" 
                case EOF():
                    return f"unexpected token: {token}" 
                case Keyword(value="`end"):
                    current.pos = token.start
                    return []
                case Keyword(value="`axiom"):
                    return f"unexpected token: {token}" 
                case Keyword(value="`epsilon"):
                    return f"unexpected token: {token}" 
                case Keyword(value="`is"):
                    return f"unexpected token: {token}" 
                case Keyword(value="`or"):
                    res = (
                        KeywordBacktickorNode(),
                        RuleNode(),
                        RuleAltNode(),
                    )

                    current.value = res
                    current.pos = token.start
                    return list(res)
                case QuotedStr():
                    return f"unexpected token: {token}" 
                case Keyword(value=unexpected):
                    return f"unknown keyword: {unexpected}" 
        case AxiomNode():
            match token:
                case Ident():
                    current.pos = token.start
                    return []
                case EOF():
                    return f"unexpected token: {token}" 
                case Keyword(value="`end"):
                    return f"unexpected token: {token}" 
                case Keyword(value="`axiom"):
                    res = (
                        KeywordBacktickaxiomNode(),
                    )

                    current.value = res
                    current.pos = token.start
                    return list(res)
                case Keyword(value="`epsilon"):
                    return f"unexpected token: {token}" 
                case Keyword(value="`is"):
                    return f"unexpected token: {token}" 
                case Keyword(value="`or"):
                    return f"unexpected token: {token}" 
                case QuotedStr():
                    return f"unexpected token: {token}" 
                case Keyword(value=unexpected):
                    return f"unknown keyword: {unexpected}" 
        case NonTermNode():
            match token:
                case Ident():
                    res = (
                        IdentNode(),
                    )

                    current.value = res
                    current.pos = token.start
                    return list(res)
                case EOF():
                    return f"unexpected token: {token}" 
                case Keyword(value="`end"):
                    return f"unexpected token: {token}" 
                case Keyword(value="`axiom"):
                    return f"unexpected token: {token}" 
                case Keyword(value="`epsilon"):
                    return f"unexpected token: {token}" 
                case Keyword(value="`is"):
                    return f"unexpected token: {token}" 
                case Keyword(value="`or"):
                    return f"unexpected token: {token}" 
                case QuotedStr():
                    return f"unexpected token: {token}" 
                case Keyword(value=unexpected):
                    return f"unknown keyword: {unexpected}" 
        case TermNode():
            match token:
                case Ident():
                    return f"unexpected token: {token}" 
                case EOF():
                    return f"unexpected token: {token}" 
                case Keyword(value="`end"):
                    return f"unexpected token: {token}" 
                case Keyword(value="`axiom"):
                    return f"unexpected token: {token}" 
                case Keyword(value="`epsilon"):
                    return f"unexpected token: {token}" 
                case Keyword(value="`is"):
                    return f"unexpected token: {token}" 
                case Keyword(value="`or"):
                    return f"unexpected token: {token}" 
                case QuotedStr():
                    res = (
                        QuotedStrNode(),
                    )

                    current.value = res
                    current.pos = token.start
                    return list(res)
                case Keyword(value=unexpected):
                    return f"unknown keyword: {unexpected}" 
        case InitNode():
            match token:
                case Ident():
                    res = (
                        ProductionNode(),
                        EOFNode(),
                    )

                    current.value = res
                    current.pos = token.start
                    return list(res)
                case EOF():
                    res = (
                        ProductionNode(),
                        EOFNode(),
                    )

                    current.value = res
                    current.pos = token.start
                    return list(res)
                case Keyword(value="`end"):
                    return f"unexpected token: {token}" 
                case Keyword(value="`axiom"):
                    res = (
                        ProductionNode(),
                        EOFNode(),
                    )

                    current.value = res
                    current.pos = token.start
                    return list(res)
                case Keyword(value="`epsilon"):
                    return f"unexpected token: {token}" 
                case Keyword(value="`is"):
                    return f"unexpected token: {token}" 
                case Keyword(value="`or"):
                    return f"unexpected token: {token}" 
                case QuotedStr():
                    return f"unexpected token: {token}" 
                case Keyword(value=unexpected):
                    return f"unknown keyword: {unexpected}" 
        case EOFNode():
            if type(token) != EOF:
                return f"expected EOF, but {type(token)} found" 
            current.value = token
            current.pos = token.start
            return None
        case IdentNode():
            if type(token) != Ident:
                return f"expected Ident, but {type(token)} found" 
            current.value = token
            current.pos = token.start
            return None
        case QuotedStrNode():
            if type(token) != QuotedStr:
                return f"expected QuotedStr, but {type(token)} found" 
            current.value = token
            current.pos = token.start
            return None
        case KeywordBacktickendNode():
            if type(token) != Keyword or token.value != "`end":
                return f"expected `end, {token} found" 
            current.value = token
            current.pos = token.start
            return None
        case KeywordBacktickaxiomNode():
            if type(token) != Keyword or token.value != "`axiom":
                return f"expected `axiom, {token} found" 
            current.value = token
            current.pos = token.start
            return None
        case KeywordBacktickepsilonNode():
            if type(token) != Keyword or token.value != "`epsilon":
                return f"expected `epsilon, {token} found" 
            current.value = token
            current.pos = token.start
            return None
        case KeywordBacktickisNode():
            if type(token) != Keyword or token.value != "`is":
                return f"expected `is, {token} found" 
            current.value = token
            current.pos = token.start
            return None
        case KeywordBacktickorNode():
            if type(token) != Keyword or token.value != "`or":
                return f"expected `or, {token} found" 
            current.value = token
            current.pos = token.start
            return None

