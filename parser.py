from dataclasses import dataclass
from pprint import pprint
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
class Program:
    datatypes: list["ADT"]
    functions: list["FuncDefinition"]


@dataclass
class ADT:
    name: str
    constructors: list["ConstructorDecl"]


@dataclass
class ConstructorDecl:
    name: str
    arg_types: list[str]


@dataclass
class FuncDefinition:
    name: str
    args_types: list[str]
    return_type: str

    clauses: list["Clause"]


@dataclass
class Clause:
    lhs_patters: "ClauseLHS"
    rhs: "Expr"


@dataclass
class ClauseLHS:
    func_name: str
    args: list["ConstructorPattern | str"]


@dataclass
class ConstructorPattern:
    name: str
    args: list["ConstructorPattern | str"]


@dataclass
class ConstructorCall:
    name: str
    args: list["Expr"]


@dataclass
class FunctionCall:
    name: str
    args: list["Expr"]


Expr = FunctionCall | ConstructorCall | str | int


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
        p = Program([], [])
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
        ADT ::= "type" IDENT ":" (IDENT)+ ("|" IDENT)* "."
        """
        self.consume("TYPE")
        name = self.consume("IDENT").value
        self.consume("COLON")

        adt = ADT(name, [])
        while True:
            constructor_name = self.consume("IDENT").value
            args: list[str] = []

            while (c := self.peek()) is not None and c.type == "IDENT":
                self.advance()
                args.append(c.value)

            if c is None:
                self.report("unexpected end of file", -1, -1)

            adt.constructors.append(ConstructorDecl(constructor_name, args))
            if c.type == "DOT":
                self.advance()
                break
            self.consume("PIPE")
        return adt

    def parse_func_decl(self) -> FuncDefinition:
        """
        "Func" ::= "fun" "(" (IDENT)+ ")" "->" IDENT ":" clause ("|" clause)* "."
        """

        self.consume("FUN")
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
        return FuncDefinition(name, args_types, return_type, clauses)

    def parse_clause(self):
        """
        clause ::= "(" IDENT (Pattern)* ")" "->" Expr
        """

        self.consume("LEFT_PAREN")
        func_name = self.consume("IDENT").value

        args: list[str | ConstructorPattern] = []
        while (c := self.peek()) is not None and c.type != "RIGHT_PAREN":
            arg = self.parse_pattern()
            args.append(arg)
        self.consume("RIGHT_PAREN")
        self.consume("ARROW")

        expr = self.parse_expr()
        clause = Clause(ClauseLHS(func_name, args), expr)
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
            return int(c.value)

        return self.consume("IDENT").value

    def parse_constructor_call(self) -> ConstructorCall:
        """
        ConstructorCall ::= "[" IDENT (Expr)* "]"
        """

        self.consume("LEFT_BRACE")
        constructor_name = self.consume("IDENT").value

        args: list[Expr] = []
        while (c := self.peek()) is not None and c.type != "RIGHT_BRACE":
            arg = self.parse_expr()
            args.append(arg)
        self.consume("RIGHT_BRACE")

        return ConstructorCall(constructor_name, args)

    def parse_func_call(self) -> FunctionCall:
        """
        FuncCall ::= "(" IDENT (Expr)* ")"
        """

        self.consume("LEFT_PAREN")
        func_name = self.consume("IDENT").value

        args: list[Expr] = []
        while (c := self.peek()) is not None and c.type != "RIGHT_PAREN":
            arg = self.parse_expr()
            args.append(arg)
        self.consume("RIGHT_PAREN")

        return FunctionCall(func_name, args)

    def parse_pattern(self) -> str | ConstructorPattern:
        """
        Pattern ::= IDENT | "[" IDENT (Pattern)* "]"
        """

        c = self.peek()
        if c is None:
            self.report("unexpected end of file", -1, -1)

        if c.type == "IDENT":
            return self.consume("IDENT").value

        self.consume("LEFT_BRACE")
        constructor_name = self.consume("IDENT").value

        args: list[str | ConstructorPattern] = []
        while (c := self.peek()) is not None and c.type != "RIGHT_BRACE":
            arg = self.parse_pattern()
            args.append(arg)

        self.consume("RIGHT_BRACE")
        return ConstructorPattern(constructor_name, args)


if __name__ == "__main__":
    with open("./input.txt", "r") as f:
        sample = "".join(f.readlines())

    tokens = Lexer(sample).tokenize()
    (res, errs) = Parser(tokens).parse_program()
    pprint(res)
    pprint(errs)
