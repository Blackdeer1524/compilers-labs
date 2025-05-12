from scanning.scanner import Ident, QuotedStr
from src.table_synthesis.synthesizer import (
    DIRECTIVE_PREFIX,
    LL1_TABLE_T,
    INIT_NODE_NAME,
)
from table_synthesis.semantics import ProductionInfo
from table_synthesis.steam import Stream

IMPORT_SECTION = """\
from typing import Optional, Union
from dataclasses import dataclass, field

from src.common.abc import IGraphVizible
from src.scanning.scanner import wrap
from src.text.processors import Position

# every scanner has to provide them
from src.scanning.scanner import Keyword, EOF

# specific to a language
# from src.scanning.scanner import Ident, QuotedStr
{}
"""

NODES = """\
# ================== AST NODES ==================
# ================ Non-Terminals ================

@dataclass
class IASTNode(IGraphVizible):
    pos: Optional[Position] = field(init=False, default=None)

    @property
    def node_label(self) -> str:
        return super().node_label + wrap(f"({str(self.pos)}))")

"""


def generate_term_node(name: str, rules: list[list[str]]) -> str:
    types: list[str] = []
    for rule in rules:
        s = "tuple[{}]".format(", ".join(map(lambda name: f'"{name}Node"', rule)))
        types.append(s)

    node_name = f"{name}Node"
    value_type = "Optional[{}]".format("|".join(types))

    return """\
@dataclass
class {}(IASTNode):
    value: {} = None

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
""".format(
        node_name, value_type
    )


def codegen_nodes(ss: Stream, infos: dict[str, ProductionInfo]):
    node2rules: dict[str, list[list[str]]] = {}
    for nonterm, info in infos.items():
        for rule in info.rhs:
            match rule:
                case "epsilon":
                    continue
                case list():
                    s: list[str] = []
                    for item in rule:
                        match item:
                            case Ident(value=value):
                                s.append(value)
                            case QuotedStr(value=value):
                                if value.startswith(DIRECTIVE_PREFIX):
                                    s.append(value[len(DIRECTIVE_PREFIX) :])
                                else:
                                    s.append(value)
                    node2rules[nonterm].append(s)
        # print(generate_node(nonterm, node2rules[nonterm]))
    


def codegen_transitions(ss: Stream, table: LL1_TABLE_T):
    keywords: set[str] = set()
    token_types: set[str] = set()

    for item in table[INIT_NODE_NAME].keys():
        if item.startswith(DIRECTIVE_PREFIX):
            token_types.add(item[len(DIRECTIVE_PREFIX) :])
        else:
            keywords.add(item)
            


    ss.push_line("def transitions(")
    ss.adjust_indent_level(+1)
    ss.push_line("current: NON_TERMINAL | TERMINAL, token: Token:")
    ss.adjust_indent_level(-1)
    ss.push_line(") -> list[NON_TERMINAL | TERMINAL] | str | None:")
    ss.adjust_indent_level(+1)

    ss.push_line("match current")
    ss.adjust_indent_level(+1)
    for nonterm, transitions in table.items():
        ss.push_line(f"case {nonterm}Node():")
        ss.adjust_indent_level(+1)
        ss.push_line(f"match token:")
        ss.adjust_indent_level(+1)

        for symbol, rule in transitions.items():
            if symbol.startswith(DIRECTIVE_PREFIX):
                token_domain = symbol[len(DIRECTIVE_PREFIX):]
                ss.push_line(f"case {token_domain}Node():")
            else:
                ss.push_line(f"case Keyword(value={symbol}):")

            ss.adjust_indent_level(+1)
            match rule:
                case None:
                    ss.push_line("""return f"unexpected token: {token}" """)
                case list():
                    ss.push_line("res = (")
                    ss.adjust_indent_level(+1)
                    for item in rule:
                        ss.push_line(f"{item}Node(),")
                    ss.adjust_indent_level(-1)
                    ss.push_line(")").endl()
                    ss.push_line("current.value = res")
                    ss.push_line("current.pos = token.start")
                    ss.push_line("return list(res)")
            ss.adjust_indent_level(-1)
        ss.adjust_indent_level(-2)
    
    for token in token_types:
        ss.push_line(f"case {token}Node():")
        ss.adjust_indent_level(+1)

        ss.push_line("if type(token) != QuotedStr:")
        ss.adjust_indent_level(+1)
        ss.push_line("""return f"expected Term, but {type(token)} found""")
        ss.adjust_indent_level(-1)

        ss.push_line("current.value = token")
        ss.push_line("current.pos = token.start")
        ss.adjust_indent_level(-1)
    
    for keyword in keywords:
        ss.push_line(f"case Keyword{keyword}Node():")
        ss.adjust_indent_level(+1)
        
        ss.push_line("""if type(token) != Keyword or token.value != "axiom":""")
        ss.adjust_indent_level(+1)
        ss.push_line("""return f"expected `axiom, {token} found" """)
        ss.adjust_indent_level(+1)

        ss.push_line("current.value = token")
        ss.push_line("current.pos = token.start")
        ss.push_line("return None")

        ss.adjust_indent_level(-1)
    
    ss.adjust_indent_level(-1)