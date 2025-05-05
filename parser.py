from collections import defaultdict, deque
import sys
from typing import Any, DefaultDict, Deque, Generator, Literal, Optional, TextIO
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


@dataclass(frozen=True)
class Segment:
    start: Position
    end: Position


@dataclass(frozen=True)
class LeftParen(Segment): ...


@dataclass(frozen=True)
class RightParen(Segment): ...


@dataclass(frozen=True)
class Identifier(Segment): ...


@dataclass(frozen=True)
class Plus(Segment): ...


@dataclass(frozen=True)
class Mult(Segment): ...


@dataclass
class EOF: ...


@dataclass(frozen=True)
class ScanError:
    message: str
    pos: Position


Token = Plus | Mult | LeftParen | RightParen | Identifier | EOF


class Scanner:
    def __init__(self, f: TextIO):
        self._text = Text(f)

        self._row = 1
        self._col = 1

    def position(self) -> Position:
        return Position(self._row, self._col)

    def skip_spaces(self):
        while True:
            cur = self._text.peek()
            if cur is None or not cur.isspace():
                return
            self._advance()

    def _advance(self):
        cur = self._text.peek()
        if cur is None:
            return

        if cur == "\r":
            self._text.advance()
            next = self._text.peek()
            if next == "\n":
                self._text.advance()
            self._row += 1
            self._col = 1
        elif cur == "\n":
            self._text.advance()
            self._row += 1
            self._col = 1
        else:
            self._col += 1
            self._text.advance()

    def __iter__(self) -> Generator[Token | ScanError, None, None]:
        errored = False
        while True:
            self.skip_spaces()
            cur = self._text.peek()
            if cur is None:
                yield EOF()
                return

            if cur == "n":
                p = self.position()
                self._advance()
                end_p = self.position()
                yield Identifier(p, end_p)
                errored = False
                continue
            elif cur == "(":
                p = self.position()
                self._advance()
                end_p = self.position()
                yield LeftParen(p, end_p)
                errored = False
                continue
            elif cur == ")":
                p = self.position()
                self._advance()
                end_p = self.position()
                yield RightParen(p, end_p)
                errored = False
                continue
            elif cur == "+":
                p = self.position()
                self._advance()
                end_p = self.position()
                yield Plus(p, end_p)
                errored = False
                continue
            elif cur == "*":
                p = self.position()
                self._advance()
                end_p = self.position()
                yield Mult(p, end_p)
                errored = False
                continue
            else:
                if errored:
                    self._advance()
                    continue
                errored = True
                yield ScanError(f"unexpected symbol: {cur}", self.position())
                self._advance()


class Analyzer:
    NON_TERMINALS = Literal["E", "E1", "T", "T1", "F"]
    TERMINALS = Literal["n", "(", "+", "*", ")", "$"]
    EPSILON_T = Literal["EPSILON"]
    EPSILON: EPSILON_T = "EPSILON"

    _table: dict[
        NON_TERMINALS,
        dict[
            type[Identifier]
            | type[LeftParen]
            | type[Plus]
            | type[Mult]
            | type[RightParen]
            | type[EOF],
            list[TERMINALS | NON_TERMINALS | EPSILON_T],
        ],
    ] = {
        "E": {
            Identifier: ["T", "E1"],
            LeftParen: ["T", "E1"],
            Plus: [],
            Mult: [],
            RightParen: [],
            EOF: [],
        },
        "E1": {
            Identifier: [],
            LeftParen: [],
            Plus: ["+", "T", "E1"],
            Mult: [],
            RightParen: ["EPSILON"],
            EOF: ["EPSILON"],
        },
        "T": {
            Identifier: ["F", "T1"],
            LeftParen: ["F", "T1"],
            Plus: [],
            Mult: [],
            RightParen: [],
            EOF: [],
        },
        "T1": {
            Identifier: [],
            LeftParen: [],
            Plus: ["EPSILON"],
            Mult: ["*", "F", "T1"],
            RightParen: ["EPSILON"],
            EOF: ["EPSILON"],
        },
        "F": {
            Identifier: ["n"],
            LeftParen: ["(", "E", ")"],
            Plus: [],
            Mult: [],
            RightParen: [],
            EOF: [],
        },
    }

    def __init__(self, s: Scanner):
        self.scanner = s

    def parse(self):
        
        depth_siblings: DefaultDict[int, list[Analyzer.EPSILON_T | Analyzer.TERMINALS | Analyzer.NON_TERMINALS]] = defaultdict(lambda: [])

        token_stream = iter(self.scanner)
        # TODO: ОБНОВЛЯЙ ТОКЕН!!!!
        token = next(token_stream)
        
        graph = "digraph {\n"
        c = 0
        INIT_NODE_NAME = f"E({c})"
        c += 1
        graph += f"\t{INIT_NODE_NAME}\n"
        d: Deque[tuple[Analyzer.EPSILON_T | Analyzer.TERMINALS | Analyzer.NON_TERMINALS, str, int]] = deque([("E", INIT_NODE_NAME, 0)])
        while True:
            (top, node_name, depth) = d.popleft()
            depth_siblings[depth].append(top)
            match top:
                case "n":
                    if type(token) != Identifier:
                        raise RuntimeError(f"expected Identifier, but {type(token)} found")
                case "(":
                    if type(token) != LeftParen:
                        raise RuntimeError(f"expected LeftParen, but {type(token)} found")
                case "*":
                    if type(token) != Mult:
                        raise RuntimeError(f"expected Mult, but {type(token)} found")
                case "+":
                    if type(token) != Plus:
                        raise RuntimeError(f"expected Plus, but {type(token)} found")
                case ")":
                    if type(token) != RightParen:
                        raise RuntimeError(f"expected RightParen, but {type(token)} found")
                case "$":
                    if type(token) != EOF:
                        raise RuntimeError(f"expected EOF, but {type(token)} found")
                    break
                case "EPSILON": 
                    continue
                case non_terminal:
                    expected = Analyzer._table[non_terminal]
                    match token:
                        case Plus() | Mult() | LeftParen() | RightParen() | Identifier() | EOF():
                            rule = expected[type(token)]
                            if len(rule) == 0:
                                raise NotImplementedError("throw an error indicating rule violation")

                            for i in reversed(rule):
                                child_name = f"{i}({c})"
                                graph += f"\t{node_name}->{child_name}\n"
                                d.appendleft((i, child_name, depth + 1))
                                c += 1
                        case ScanError():
                            raise NotImplementedError("handle scanner errors")
        graph += "}"
        print(graph)


def main():
    s = Scanner(open("./test.txt"))
    a = Analyzer(s)
    a.parse()


if __name__ == "__main__":
    main()
