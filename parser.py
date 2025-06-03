from collections import deque
from copy import copy
from dataclasses import dataclass
from typing import List, Literal, Never, Optional


TYPE = "TYPE"
FUN = "FUN"
IDENT = "IDENT"
NUMBER = "NUMBER"

PIPE = "PIPE"
DOT = "DOT"
ARROW = "ARROW"
COLON = "COLON"

LEFT_PAREN = "LEFT_PAREN"
RIGHT_PAREN = "RIGHT_PAREN"
LEFT_BRACE = "LEFT_BRACE"
RIGHT_BRACE = "RIGHT_BRACE"

EOF = "EOF"

TOKEN_TYPE = Literal[
    "TYPE",
    "FUN",
    "IDENT",
    "NUMBER",
    "PIPE",
    "DOT",
    "ARROW",
    "COLON",
    "LEFT_PAREN",
    "RIGHT_PAREN",
    "LEFT_BRACE",
    "RIGHT_BRACE",
    "EOF",
]

INT_TYPE = "Int"
PREAMBLE_TYPES = (INT_TYPE,)


class SemanticError(Exception):
    def __init__(self, msg: str, line: int, column: int, *args: object) -> None:
        super().__init__(*args)
        self.msg = msg
        self.line = line
        self.column = column

    @property
    def message(self):
        return f"[{self.line}:{self.column}] {self.msg}"


@dataclass
class Token:
    type: TOKEN_TYPE
    value: str
    line: int
    column: int


class LexerError(Exception):
    pass


class Lexer:
    def __init__(self, text: str) -> None:
        self.text = text
        self.pos = 0
        self.line = 1
        self.col = 1

    # — Helper primitives —
    def _peek(self) -> Optional[str]:
        return self.text[self.pos] if self.pos < len(self.text) else None

    def _advance(self) -> Optional[str]:
        ch = self._peek()
        if ch is None:
            return None
        self.pos += 1
        if ch == "\n":
            self.line += 1
            self.col = 1
        else:
            self.col += 1
        return ch

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []

        while (ch := self._peek()) is not None:
            start_line, start_col = self.line, self.col

            if ch.isspace():
                self._advance()
                continue

            if (
                ch == "-"
                and self.pos + 1 < len(self.text)
                and self.text[self.pos + 1] == ">"
            ):
                self._advance()
                self._advance()
                tokens.append(Token(ARROW, "->", start_line, start_col))
                continue

            # Single-character punctuation
            single_char_map: dict[str, TOKEN_TYPE] = {
                "|": PIPE,
                ".": DOT,
                ":": COLON,
                "(": LEFT_PAREN,
                ")": RIGHT_PAREN,
                "[": LEFT_BRACE,
                "]": RIGHT_BRACE,
            }
            if ch in single_char_map:
                self._advance()
                tokens.append(Token(single_char_map[ch], ch, start_line, start_col))
                continue

            if ch.isdigit():
                digits: list[str] = []
                while (c := self._peek()) is not None and c.isdigit():
                    digits.append(c)
                    self._advance()
                tokens.append(Token(NUMBER, "".join(digits), start_line, start_col))
                continue

            if ch.isalpha() or ch == "_":
                ident: list[str] = []
                while (c := self._peek()) is not None and (c.isalnum() or c == "_"):
                    ident.append(c)
                    self._advance()
                value = "".join(ident)
                if value == "type":
                    kind = TYPE
                elif value == "fun":
                    kind = FUN
                else:
                    kind = IDENT
                tokens.append(Token(kind, value, start_line, start_col))
                continue

            raise LexerError(
                f"Unexpected character {ch!r} at line {self.line}, column {self.col}"
            )
        tokens.append(Token("EOF", "$", self.line, self.col))
        return tokens


class ParserError(Exception):
    pass


@dataclass
class ASTNode:
    line: int
    column: int


@dataclass
class Program(ASTNode):
    datatypes: list["ADT"]
    functions: list["FuncDefinition"]

    def check(self):
        defined_adts: set[str] = set()
        for f in self.datatypes:
            if f.name in defined_adts:
                raise NotImplementedError()
            defined_adts.add(f.name)

        defined_functions: dict[str, FuncDefinition] = {}
        defined_functions.update(PREAMBLE_FUNCS)
        for f in self.functions:
            if f.name in defined_functions:
                raise NotImplementedError()
            defined_functions[f.name] = f

        defined_constructors: dict[str, "ConstructorDecl"] = {}
        for adt in self.datatypes:
            adt.check(defined_adts, defined_constructors)

        for f in self.functions:
            f.check(defined_functions, defined_adts, defined_constructors)


@dataclass
class ADT(ASTNode):
    name: str
    constructors: list["ConstructorDecl"]

    def check(
        self,
        defined_datatypes: set[str],
        defined_constructors: dict[str, "ConstructorDecl"],
    ):
        for c in self.constructors:
            if c.name in defined_constructors:
                raise SemanticError("unknown constructor", c.line, c.column)
            defined_constructors[c.name] = c

            for t in c.arg_types:
                if t.value not in defined_datatypes and t.value not in PREAMBLE_TYPES:
                    raise SemanticError(
                        f"unknown arg type: `{t.value}`", t.line, t.column
                    )


@dataclass
class ConstructorDecl(ASTNode):
    type: str
    name: str
    arg_types: list[Token]


@dataclass
class FuncDefinition(ASTNode):
    name: str
    args_types: list[str]
    return_type: str

    clauses: list["Clause"]

    def check(
        self,
        defined_functions: dict[str, "FuncDefinition"],
        defined_datatypes: set[str],
        defined_constructors: dict[str, "ConstructorDecl"],
    ):
        for t in self.args_types:
            if t not in defined_datatypes and t not in PREAMBLE_TYPES:
                raise NotImplementedError()

        if (
            self.return_type not in defined_datatypes
            and self.return_type not in PREAMBLE_TYPES
        ):
            raise NotImplementedError()

        for clause in self.clauses:
            clause.check(
                self.name, defined_functions, defined_constructors, self.return_type
            )


@dataclass
class Clause(ASTNode):
    lhs_patters: "ClauseLHS"
    rhs: "Expr"

    def check(
        self,
        parent_func_name: str,
        defined_funcs: dict[str, FuncDefinition],
        defined_constructors: dict[str, ConstructorDecl],
        expected_return_type: str,
    ):
        ident2type = self.lhs_patters.check(
            defined_funcs[parent_func_name], defined_constructors
        )
        return_type = check_expression(
            self.rhs, ident2type, defined_funcs, defined_constructors
        )
        if return_type != expected_return_type:
            raise SemanticError(
                f"type mismatch. expected: {expected_return_type}. actual: {return_type}",
                self.rhs.line,
                self.rhs.column,
            )


@dataclass
class ClauseLHS(ASTNode):
    func_name: str
    args: list["ConstructorPattern | Token"]

    def check(
        self,
        parent_func: FuncDefinition,
        defined_constructors: dict[str, ConstructorDecl],
    ) -> dict[str, str]:
        if self.func_name != parent_func.name:
            raise SemanticError(
                f"expected a clause for a function `{parent_func.name}`, not `{self.func_name}`",
                self.line,
                self.column,
            )

        defined_idents: dict[str, str] = {}
        d = deque(((i, t) for i, t in zip(self.args, parent_func.args_types)))
        while len(d) > 0:
            arg, expected_type = d.popleft()
            match arg:
                case Token() as ident:
                    if ident.value in defined_idents:
                        raise SemanticError(
                            "identifier is already defined", ident.line, ident.column
                        )
                    defined_idents[ident.value] = expected_type

                case ConstructorPattern(line=line, column=column, name=name, args=args):
                    if name not in defined_constructors:
                        raise SemanticError("unknown constructor", line, column)

                    constructor_info = defined_constructors[name]
                    if constructor_info.type != expected_type:
                        raise SemanticError(
                            f"constructor of unexpected type. expected: {expected_type}. actual: {constructor_info.type}",
                            line,
                            column,
                        )

                    if len(constructor_info.arg_types) != len(args):
                        raise SemanticError(
                            f"constructor {name} has a wrong number of params. expected: {len(constructor_info.arg_types)}. actual: {len(args)}",
                            line,
                            column,
                        )

                    for arg, expected_arg_type in reversed(
                        list(zip(args, constructor_info.arg_types))
                    ):
                        d.appendleft((arg, expected_arg_type.value))

        return defined_idents


@dataclass
class ConstructorPattern(ASTNode):
    name: str
    args: list["ConstructorPattern | Token"]


@dataclass
class ConstructorCall(ASTNode):
    name: str
    args: list["Expr"]


@dataclass
class FunctionCall(ASTNode):
    name: str
    args: list["Expr"]


Expr = FunctionCall | ConstructorCall | Token


def check_expression(
    e: Expr,
    ident2type: dict[str, str],
    defined_functions: dict[str, FuncDefinition],
    defined_constructors: dict[str, ConstructorDecl],
) -> str:
    match e:
        case FunctionCall() as call:
            if (function_info := defined_functions.get(call.name)) is None:
                raise SemanticError(
                    f"unknown funciton: {call.name}",
                    call.line,
                    call.column,
                )

            for arg, expected_arg_type in zip(call.args, function_info.args_types):
                arg_type = check_expression(
                    arg, ident2type, defined_functions, defined_constructors
                )
                if arg_type != expected_arg_type:
                    raise SemanticError(
                        f"type mismatch. actual: {arg_type}. expected: {expected_arg_type}",
                        arg.line,
                        arg.column,
                    )

            return function_info.return_type
        case ConstructorCall() as constructor:
            if (constructor_info := defined_constructors.get(constructor.name)) is None:
                raise SemanticError(
                    f"unknown constructor: {constructor.name}",
                    constructor.line,
                    constructor.column,
                )

            if len(constructor.args) != len(constructor_info.arg_types):
                raise SemanticError(
                    f"constructor argument count mismatch. expected: {len(constructor_info.arg_types)}. actual: {len(constructor.args)}",
                    constructor.line,
                    constructor.column,
                )

            for arg, expected_arg_type in zip(
                constructor.args, (t.value for t in constructor_info.arg_types)
            ):
                arg_type = check_expression(
                    arg, ident2type, defined_functions, defined_constructors
                )
                if arg_type != expected_arg_type:
                    raise SemanticError(
                        f"type mismatch. actual: {arg_type}. expected: {expected_arg_type}",
                        arg.line,
                        arg.column,
                    )

            return constructor_info.type
        case Token(type="IDENT") as ident:
            if (t := ident2type.get(ident.value)) is None:
                if (t := defined_constructors.get(ident.value)) is None:
                    raise SemanticError(
                        f"unknown ident: {ident.value}", ident.line, ident.column
                    )
                if len(t.arg_types) != 0:
                    raise SemanticError(
                        f"invalid use of constructor {ident.value}",
                        ident.line,
                        ident.column,
                    )
                return t.type
            return t
        case Token(type="NUMBER"):
            return INT_TYPE
        case Token():
            raise RuntimeError("unreachable")


PREAMBLE_FUNCS = {
    "add": FuncDefinition(-1, -1, "add", [INT_TYPE, INT_TYPE], INT_TYPE, []),
    "mul": FuncDefinition(-1, -1, "mul", [INT_TYPE, INT_TYPE], INT_TYPE, []),
}


class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.cur = 0

        self.errors: list[str] = []

    def advance(self):
        self.cur += 1

    def peek(self) -> Optional[Token]:
        if self.cur >= len(self.tokens):
            return None
        return self.tokens[self.cur]

    def report(self, mes: str, line: int, col: int) -> Never:
        mes = f"[{line},{col}]: {mes}"
        self.errors.append(mes)
        raise ParserError(mes)

    def consume(self, expected: TOKEN_TYPE) -> Token:
        t = self.peek()
        if t is None:
            self.report("unexpected end of file", -1, -1)
        if t.type != expected:
            raise ParserError(
                f"unexpected token type: {t.type}. token: {t}", t.line, t.column
            )
        self.advance()
        return t

    def parse_program(self) -> tuple[Program, list[str]]:
        """
        axiom
        Program ::= (ADT | Func)* EOF
        """
        p = Program(1, 1, [], [])
        while True:
            t = self.peek()
            if t is None:
                self.report("unexpected end of file", -1, -1)

            try:
                match t.type:
                    case "TYPE":
                        adt = self.parse_adt()
                        p.datatypes.append(adt)
                    case "FUN":
                        func = self.parse_func_decl()
                        p.functions.append(func)
                    case "EOF":
                        break
                    case _:
                        self.report(
                            f"unexpected token type: {t.type}. token: {t}",
                            t.line,
                            t.column,
                        )
            except ParserError:
                self.recover()

        return p, self.errors

    def recover(self):
        while (c := self.peek()) is not None and c.type not in ("EOF", "DOT"):
            self.advance()

        if c is None:
            self.report("couldn't recover: unexpected end of file", -1, -1)

        if c.type == "DOT":
            self.advance()

    def parse_adt(self) -> ADT:
        """
        ADT ::= "type" IDENT ":" (IDENT)+ ("|" IDENT+)* "."
        """
        type_token = self.consume("TYPE")
        adt_name = self.consume("IDENT").value
        self.consume("COLON")

        adt = ADT(type_token.line, type_token.column, adt_name, [])
        while True:
            constructor_name_token = self.consume("IDENT")
            args: list[Token] = []

            while (c := self.peek()) is not None and c.type == "IDENT":
                self.advance()
                args.append(c)

            if c is None:
                self.report("unexpected end of file", -1, -1)

            adt.constructors.append(
                ConstructorDecl(
                    constructor_name_token.line,
                    constructor_name_token.column,
                    adt_name,
                    constructor_name_token.value,
                    args,
                )
            )

            if c.type == "DOT":
                self.advance()
                break
            self.consume("PIPE")
        return adt

    def parse_func_decl(self) -> FuncDefinition:
        """
        Func ::= "fun" "(" (IDENT)+ ")" "->" IDENT ":" clause ("|" clause)* "."
        """

        fun_token = self.consume("FUN")
        self.consume("LEFT_PAREN")
        name = self.consume("IDENT").value

        args_types: list[str] = []
        while (c := self.peek()) is not None and c.type == "IDENT":
            self.advance()
            args_types.append(c.value)

        if c is None:
            self.report("unexpected end of file", -1, -1)

        self.consume("RIGHT_PAREN")
        self.consume("ARROW")

        return_type = self.consume("IDENT").value
        self.consume("COLON")

        clauses: list[Clause] = [self.parse_clause()]
        while (c := self.peek()) is not None and c.type == "PIPE":
            self.advance()
            clauses.append(self.parse_clause())
        self.consume("DOT")
        return FuncDefinition(
            fun_token.line, fun_token.column, name, args_types, return_type, clauses
        )

    def parse_clause(self):
        """
        clause ::= "(" IDENT (Pattern)* ")" "->" Expr
        """
        start = self.consume("LEFT_PAREN")
        func_name = self.consume("IDENT").value

        args: list[Token | ConstructorPattern] = []
        while (c := self.peek()) is not None and c.type != "RIGHT_PAREN":
            arg = self.parse_pattern()
            args.append(arg)
        self.consume("RIGHT_PAREN")
        self.consume("ARROW")

        expr = self.parse_expr()
        clause = Clause(
            start.line,
            start.column,
            ClauseLHS(start.line, start.column, func_name, args),
            expr,
        )
        return clause

    def parse_expr(self) -> Expr:
        """
        Expr ::= FuncCall | ConstructorCall | IDENT | NUMBER
        """

        c = self.peek()
        if c is None:
            self.report("unexpected end of file", -1, -1)
        if c.type == "LEFT_PAREN":
            return self.parse_func_call()
        elif c.type == "LEFT_BRACE":
            return self.parse_constructor_call()
        elif c.type == "NUMBER":
            self.advance()
            return c

        return self.consume("IDENT")

    def parse_constructor_call(self) -> ConstructorCall:
        """
        ConstructorCall ::= "[" IDENT (Expr)* "]"
        """

        start = self.consume("LEFT_BRACE")
        constructor_name = self.consume("IDENT").value

        args: list[Expr] = []
        while (c := self.peek()) is not None and c.type != "RIGHT_BRACE":
            arg = self.parse_expr()
            args.append(arg)
        self.consume("RIGHT_BRACE")

        return ConstructorCall(start.line, start.column, constructor_name, args)

    def parse_func_call(self) -> FunctionCall:
        """
        FuncCall ::= "(" IDENT (Expr)* ")"
        """

        start = self.consume("LEFT_PAREN")
        func_name = self.consume("IDENT").value

        args: list[Expr] = []
        while (c := self.peek()) is not None and c.type != "RIGHT_PAREN":
            arg = self.parse_expr()
            args.append(arg)
        self.consume("RIGHT_PAREN")

        return FunctionCall(start.line, start.column, func_name, args)

    def parse_pattern(self) -> Token | ConstructorPattern:
        """
        Pattern ::= IDENT | "[" IDENT (Pattern)* "]"
        """

        start = self.peek()
        if start is None:
            self.report("unexpected end of file", -1, -1)

        if start.type == "IDENT":
            return self.consume("IDENT")

        self.consume("LEFT_BRACE")
        constructor_name = self.consume("IDENT").value

        args: list[Token | ConstructorPattern] = []
        while (c := self.peek()) is not None and c.type != "RIGHT_BRACE":
            arg = self.parse_pattern()
            args.append(arg)

        self.consume("RIGHT_BRACE")
        return ConstructorPattern(start.line, start.column, constructor_name, args)


if __name__ == "__main__":
    with open("./input.txt", "r") as f:
        sample = "".join(f.readlines())

    tokens = Lexer(sample).tokenize()
    (res, errs) = Parser(tokens).parse_program()

    try:
        res.check()
        print("OK")
    except SemanticError as e:
        print(e.message)
        exit(1)
    # pprint(res)
    # pprint(errs)
