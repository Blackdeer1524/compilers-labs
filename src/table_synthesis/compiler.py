import itertools
from src.scanning.scanner import Ident, QuotedStr
from src.table_synthesis.synthesizer import (
    DIRECTIVE_PREFIX,
    LL1_TABLE_T,
    INIT_NODE_NAME,
)
from src.table_synthesis.semantics import ProductionInfo
from src.table_synthesis.stream import Stream

IMPORT_SECTION = """\
from typing import Optional
from dataclasses import dataclass, field

from src.common.abc import IGraphVizible
from src.common.pretty import wrap
from src.text.processors import Position

from src.scanning.task_scanner import Token

# every scanner has to provide
from src.scanning.task_scanner import Keyword

# Token types:
{}
"""


def name_transformer(s: str) -> str:
    """
    Replace each special character in the input string with its alphanumeric name.
    E.g. '(' → 'LeftParen', '$' → 'Dollar', etc.
    """
    SPECIAL_MAP = {
        "(": "LeftParen",
        ")": "RightParen",
        "$": "Dollar",
        "#": "Hash",
        "%": "Percent",
        "&": "Ampersand",
        "*": "Asterisk",
        "@": "At",
        "!": "Bang",
        "?": "Question",
        "-": "Minus",
        "+": "Plus",
        "=": "Equals",
        "/": "Slash",
        "\\": "Backslash",
        "<": "LessThan",
        ">": "GreaterThan",
        "^": "Caret",
        "~": "Tilde",
        "`": "Backtick",
        "{": "LeftBrace",
        "}": "RightBrace",
        "[": "LeftBracket",
        "]": "RightBracket",
        "|": "Pipe",
        ":": "Colon",
        ";": "Semicolon",
        '"': "Quote",
        "'": "Apostrophe",
        ",": "Comma",
        ".": "Dot",
    }

    result: list[str] = []
    for ch in s:
        if ch.isalnum() or ch == "_":
            result.append(ch)
        elif ch in SPECIAL_MAP:
            result.append(SPECIAL_MAP[ch])
        else:
            # if you’d rather drop unknown symbols entirely:
            # continue
            # or, to keep them as-is:
            result.append(ch)
    return "".join(result)


def generate_imports(ss: Stream, token_types: set[str]):
    if len(token_types) == 0:
        ss.push_line(IMPORT_SECTION.format(""))
        return

    ss.push_line(
        IMPORT_SECTION.format(
            "from src.scanning.task_scanner import {}".format(", ".join(token_types))
        )
    )


def generate_term_node(token_type: str) -> str:
    node_name = f"{token_type}Node"

    ss = Stream()
    ss.push_line("@dataclass")
    with ss.push_line(f"class {node_name}(IASTNode):").indent() as class_body:
        class_body.push_line(f"value: Optional[{token_type}] = None")
        class_body.push_line()
        with class_body.push_line(
            "def to_graphviz(self) -> str:"
        ).indent() as to_graphviz:
            to_graphviz.push_line("res = super().to_graphviz()")
            with to_graphviz.push_line("match self.value:").indent() as match_stmt:
                with match_stmt.push_line("case None:").indent() as case_none:
                    case_none.push_line("""epsilon_name = f"𝓔{id(self)}" """).push_line(
                        """res += f'\\t{epsilon_name} [label="𝓔"]\\n' """
                    ).push_line(
                        """res += f"{self.node_name} -> {epsilon_name}" """
                    ).push_line(
                        "return res"
                    )
                with match_stmt.push_line("case _:").indent() as case_other:
                    case_other.push_line(
                        """res += self.value.to_graphviz()"""
                    ).push_line(
                        """res += f"\\t{self.node_name} -> {self.value.node_name}\\n" """
                    )
                    case_other.push_line("return res")

    return ss.emit()


def generate_keyword_node(name: str) -> str:
    node_name = f"Keyword{name}Node"

    return (
        """\
@dataclass
class {}(IASTNode):
""".format(
            node_name
        )
        + """\
    value: Optional["Keyword"] = None

    def to_graphviz(self) -> str:
        res = super().to_graphviz()
        match self.value:
            case None:
                epsilon_name = f"𝓔{id(self)}"
                res += f'\\t{epsilon_name} [label="𝓔"]\\n'
                res += f"{self.node_name} -> {epsilon_name}"
                return res
            case _:
                res += self.value.to_graphviz()
                res += f"\\t{self.node_name} -> {self.value.node_name}\\n"
        return res
"""
    )


def generate_node_name(name: str):
    return f'{name}Node'

def generate_nonterm_node(name: str, rules: list[list[str]]) -> str:
    types: list[str] = []
    has_long_rule = False
    has_short_rule = False
    for rule in rules:
        has_long_rule = has_long_rule or len(rule) > 1
        has_short_rule = has_short_rule or len(rule) == 1 
        s = "tuple[{}]".format(", ".join(map(generate_node_name, rule))) if len(rule) > 1 else generate_node_name(rule[0])
        types.append(s)

    node_name = f"{name}Node"
    value_type = 'Optional["{}"]'.format("|".join(types))

    ss = Stream()
    ss.push_line("@dataclass")
    ss.push_line(f"class {node_name}(IASTNode):")
    with ss.indent() as class_body:
        class_body.push_line(f"value: {value_type} = None")
        class_body.push_line()

        with class_body.push_line( "def to_graphviz(self) -> str:").indent() as to_graphviz_body:
            to_graphviz_body.push_line("res = super().to_graphviz()")
            with to_graphviz_body.push_line("match self.value:").indent() as match_stmt:
                with match_stmt.push_line("case None:").indent() as none_case:
                    none_case.push_line("""epsilon_name = f"𝓔{id(self)}" """)
                    none_case.push_line( """res += f'\\t{epsilon_name} [label="𝓔"]\\n' """)
                    none_case.push_line( """res += f"\\t{self.node_name} -> {epsilon_name}\\n" """)
                if has_long_rule:
                    with match_stmt.push_line("case tuple():").indent() as tuple_case:
                        tuple_case.push_line( """res += "".join(child.to_graphviz() for child in self.value) """)
                        tuple_case.push_line("""res += "".join( """)
                        with tuple_case.indent():
                            tuple_case.push_line( """f"\\t{self.node_name} -> {child.node_name}\\n" for child in self.value """)
                        tuple_case.push_line(")")

                        tuple_case.push_line("assert len(self.value) > 1")
                        tuple_case.push_line( """res += "\\t{{rank=same; {} [style=invis]}}\\n".format(""")
                        with tuple_case.indent():
                            tuple_case.push_line( """" -> ".join(child.node_name for child in self.value)""")
                        tuple_case.push_line(")")
                if has_short_rule:
                    with match_stmt.push_line("case _:").indent() as other_case:
                        other_case.push_line( """res += self.value.to_graphviz()""")
                        other_case.push_line( """res += f"\\t{self.node_name} -> {self.value.node_name}\\n" """)
            to_graphviz_body.push_line("return res")
    return ss.emit()


IAST_DECL = """\
@dataclass
class IASTNode(IGraphVizible):
    pos: Optional[Position] = field(init=False, default=None)

    @property
    def node_label(self) -> str:
        return super().node_label + wrap(f"({str(self.pos)}))")

"""


def generate_nodes(
    ss: Stream,
    infos: dict[str, ProductionInfo],
    token_types: set[str],
    keywords: set[str],
):
    ss.push_line(IAST_DECL)

    ss.push_line("# ============== NONTERM NODES =============")
    for nonterm, info in infos.items():
        nonterm_rules: list[list[str]] = []
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
                                    s.append(
                                        name_transformer(value[len(DIRECTIVE_PREFIX) :])
                                    )
                                else:
                                    s.append(
                                        "Keyword{}".format(name_transformer(value))
                                    )
                    nonterm_rules.append(s)
        ss.push_line(generate_nonterm_node(nonterm, nonterm_rules))

    ss.push_line(
        "NON_TERMINAL = {}".format(
            " | ".join((f"{nonterm}Node" for nonterm in infos.keys()))
        )
    )

    ss.push_line("# ============== TERM NODES =============")
    for token_type in token_types:
        ss.push_line(generate_term_node(token_type))

    ss.push_line("# ============== KEYWORD NODES =============")
    for keyword in keywords:
        ss.push_line(generate_keyword_node(name_transformer(keyword)))

    ss.push_line(
        "TERMINAL = {}".format(
            " | ".join(
                itertools.chain(
                    (f"{token}Node" for token in token_types),
                    (f"Keyword{name_transformer(kw)}Node" for kw in keywords),
                )
            )
        )
    )


def generate_transitions(
    ss: Stream, table: LL1_TABLE_T, infos: dict[str, ProductionInfo]
):
    keywords: set[str] = set()
    token_types: set[str] = set()

    for item in table[INIT_NODE_NAME].keys():
        if item.startswith(DIRECTIVE_PREFIX):
            token_types.add(name_transformer(item[len(DIRECTIVE_PREFIX) :]))
        else:
            keywords.add(item)

    generate_imports(ss, token_types)
    generate_nodes(ss, infos, token_types, keywords)

    with ss.push_line("def transitions(").indent() as transitions_decl:
        transitions_decl.push_line("current: NON_TERMINAL | TERMINAL, token: Token")
    ss.push_line(") -> list[NON_TERMINAL | TERMINAL] | str | None:")
    
    with ss.indent() as func_body:
        with func_body.push_line("match current:").indent() as symbol_match:
            for nonterm, transitions in table.items():
                with symbol_match.push_line(f"case {generate_node_name(nonterm)}():").indent() as case_nonterm:
                    with case_nonterm.push_line(f"match token:").indent() as token_match:
                        for symbol, rule in transitions.items():
                            if symbol.startswith(DIRECTIVE_PREFIX):
                                token_domain = symbol[len(DIRECTIVE_PREFIX) :]
                                token_match.push_line(f"case {token_domain}():")
                            else:
                                token_match.push_line(f'case Keyword(value="{symbol}"):')

                            with token_match.indent() as case_body:
                                match rule:
                                    case None:
                                        case_body.push_line("""return f"unexpected token: {token}" """)
                                    case list([]):
                                        case_body.push_line("current.pos = token.start")
                                        case_body.push_line("return []")
                                    case list() if len(rule) > 1:
                                        with case_body.push_line("res = (").indent() as res_indent:
                                            for item in rule:
                                                match item:
                                                    case Ident(value=value):
                                                        res_indent.push_line(f"{generate_node_name(value)}(),")
                                                    case QuotedStr(value=value):
                                                        if value.startswith(DIRECTIVE_PREFIX):
                                                            res_indent.push_line(
                                                                f"{generate_node_name(name_transformer( value[len(DIRECTIVE_PREFIX):]))}(),"
                                                            )
                                                        else:
                                                            res_indent.push_line(
                                                                f"Keyword{generate_node_name(name_transformer( value))}(),"
                                                            )
                                        case_body.push_line(")").endl()
                                        case_body.push_line("current.value = res")
                                        case_body.push_line("current.pos = token.start")
                                        case_body.push_line("return list(res)")
                                    case list():
                                        item = rule[0]
                                        match item:
                                            case Ident(value=value):
                                                case_body.push_line(f"res = {generate_node_name(value)}()")
                                            case QuotedStr(value=value):
                                                if value.startswith(DIRECTIVE_PREFIX):
                                                    case_body.push_line(
                                                        f"res = {generate_node_name(name_transformer( value[len(DIRECTIVE_PREFIX):]))}()"
                                                    )
                                                else:
                                                    case_body.push_line(
                                                        f"res = Keyword{generate_node_name(name_transformer( value))}()"
                                                    )
                                        
                                        case_body.push_line("current.value = res")
                                        case_body.push_line("current.pos = token.start")
                                        case_body.push_line("return [res]")

                        with token_match.push_line(f"case Keyword(value=unexpected):").indent() as case_body:
                            case_body.push_line("""return f"unknown keyword: {unexpected}" """)

            for token_type in token_types:
                with ss.push_line(f"case {generate_node_name(token_type)}():").indent() as case_term:
                    with case_term.push_line("if type(token) != {}:".format(token_type)).indent() as token_type_assertion:
                        token_type_assertion.push_line(
                            """return f"expected {}""".format(token_type)
                            + """, but {type(token)} found" """
                        )

                    case_term.push_line("current.value = token")
                    case_term.push_line("current.pos = token.start")
                    case_term.push_line("return None")

            for keyword in keywords:
                with ss.push_line(f"case Keyword{generate_node_name( name_transformer(keyword))}():").indent() as case_keyword:
                    with case_keyword.push_line(f"""if type(token) != Keyword or token.value != "{keyword}":""").indent() as token_type_assertion:
                        token_type_assertion.push_line(
                            """return "expected {}""".format(keyword) + """, {} found".format(token) """
                        )

                    case_keyword.push_line("current.value = token")
                    case_keyword.push_line("current.pos = token.start")
                    case_keyword.push_line("return None")
