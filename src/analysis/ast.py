from typing import Literal, Optional, Union
from dataclasses import dataclass

from attr import field

from src.common.abc import IGraphVizible
from src.scanning.scanner import Keyword, Ident, EOF, QuotedStr, wrap
from src.text.processors import Position


# ================== AST NODES ==================
# ================ Non-Terminals ================


@dataclass(kw_only=True)
class IASTNode(IGraphVizible):
    start: Optional[Position] = field(init=False, default=None)

    @property
    def node_label(self) -> str:
        return super().node_label + f"{wrap(str(self.start))}"


@dataclass
class InitNode(IASTNode):
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
class ProductionNode(IASTNode):
    value: Optional[
        tuple[
            "AxiomNode",
            "NonTermNode",
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
class RuleNode(IASTNode):
    value: Optional[
        Union[
            tuple["TermNode | NonTermNode", "RuleTailNode"],
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
class RuleTailNode(IASTNode):
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
class RuleAltNode(IASTNode):
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
class AxiomNode(IASTNode):
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
class KeywordNode(IASTNode):
    kind: Literal["axiom", "is", "or", "end", "epsilon"]
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
class NonTermNode(IASTNode):
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
class TermNode(IASTNode):
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


TERMINAL = KeywordNode | NonTermNode | TermNode | EOFNode

# ===============================================

__all__ = [
    "InitNode",
    "ProductionNode",
    "RuleNode",
    "RuleTailNode",
    "RuleAltNode",
    "AxiomNode",
    "KeywordNode",
    "NonTermNode",
    "TermNode",
    "EOFNode",
    "TERMINAL",
    "NON_TERMINAL",
]
