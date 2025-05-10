from typing import Optional, Union
from dataclasses import dataclass

from src.common.abc import IGraphVizible
from src.scanning.scanner import Keyword, Ident, EOF, QuotedStr

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
