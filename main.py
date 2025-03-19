from dataclasses import dataclass
from enum import Enum, IntEnum, auto
import sys
from typing import Iterator, Literal, Optional, TextIO


State = Literal[
    "0 2 7 18 20",
    "1",
    "3",
    "22",
    "5 6",
    "11 19",
    "19",
    "8 19",
    "15 16",
    "21",
    "TRAP",
    "16 17",
    "9 19",
    "10 19",
    "12 19",
    "13 19",
    "14 19",
    "19 23",
    "4",
]


START_STATE: State = "0 2 7 18 20"


class Domain(Enum):
    EOF = auto()
    OPERATOR_BANG = auto()
    OPERATOR_COLON = auto()
    SPACES = auto()
    DIGIT = auto()
    KEYWORD_CLEAN = auto()
    KEYWORD_ALL = auto()
    COMMENT = auto()
    IDENT = auto()


@dataclass(frozen=True)
class Position:
    row: int
    col: int


@dataclass(frozen=True)
class Segment:
    start: Position
    end: Position


@dataclass(frozen=True)
class EOF(Segment):
    pass


@dataclass(frozen=True)
class OperatorBang(Segment):
    pass


@dataclass(frozen=True)
class OperatorColon(Segment):
    pass


@dataclass(frozen=True)
class Spaces(Segment):
    pass


@dataclass(frozen=True)
class Digit(Segment):
    value: int


@dataclass(frozen=True)
class KeywordClean(Segment):
    pass


@dataclass(frozen=True)
class KeywordAll(Segment):
    pass


@dataclass(frozen=True)
class Comment(Segment):
    message: str


@dataclass(frozen=True)
class Ident(Segment):
    name: str


Token = (
    EOF
    | OperatorBang
    | OperatorColon
    | Digit
    | KeywordClean
    | KeywordAll
    | Comment
    | Ident
)


class SymbolType(IntEnum):
    EOF = 0
    BANG = auto()
    COLON = auto()
    SPACE = auto()
    NEW_LINE = auto()
    C = auto()
    L = auto()
    A = auto()
    E = auto()
    N = auto()
    HASH = auto()
    DIGIT = auto()
    OTHER_CHARS = auto()
    ALPHABET = auto()
    SLASH = auto()


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


class TextWithPosition(Text):
    def __init__(self, f: TextIO):
        super().__init__(f)
        self._row = 1
        self._col = 1

    def position(self) -> Position:
        return Position(self._row, self._col)

    def peek(self):
        r = super().peek()
        if r == "\r":
            return "\n"
        return r

    def advance(self):
        cur = self.peek()
        if cur is None:
            return

        if cur == "\r":
            super().advance()
            next = self.peek()
            if next == "\n":
                super().advance()
            self._row += 1
            self._col = 1
        elif cur == "\n":
            super().advance()
            self._row += 1
            self._col = 1
        else:
            self._col += 1
            super().advance()


class Automaton:
    # fmt: off
    DELTA: dict[State, list[State]] =  {
        "0 2 7 18 20": ["1","3","22","5 6","5 6","11 19","19","19","8 19","19","15 16","21","TRAP","19","TRAP"],
        "1": ["TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP"],
        "3": ["TRAP","4","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP"],
        "22": ["TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP"],
        "5 6": ["TRAP","TRAP","TRAP","5 6","5 6","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP"],
        "11 19": ["TRAP","TRAP","TRAP","TRAP","TRAP","19","12 19","19","19","19","TRAP","19","TRAP","19","TRAP"],
        "19": ["TRAP","TRAP","TRAP","TRAP","TRAP","19","19","19","19","19","TRAP","19","TRAP","19","TRAP"],
        "8 19": ["TRAP","TRAP","TRAP","TRAP","TRAP","19","9 19","19","19","19","TRAP","19","TRAP","19","TRAP"],
        "15 16": ["TRAP","15 16","15 16","15 16","TRAP","15 16","15 16","15 16","15 16","15 16","15 16","15 16","15 16","15 16","16 17"],
        "21": ["TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","21","TRAP","TRAP","TRAP"],
        "TRAP": ["TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP"],
        "16 17": ["TRAP","15 16","15 16","15 16","15 16","15 16","15 16","15 16","15 16","15 16","15 16","15 16","15 16","15 16","TRAP"],
        "9 19": ["TRAP","TRAP","TRAP","TRAP","TRAP","19","10 19","19","19","19","TRAP","19","TRAP","19","TRAP"],
        "10 19": ["TRAP","TRAP","TRAP","TRAP","TRAP","19","19","19","19","19","TRAP","19","TRAP","19","TRAP"],
        "12 19": ["TRAP","TRAP","TRAP","TRAP","TRAP","19","19","13 19","19","19","TRAP","19","TRAP","19","TRAP"],
        "13 19": ["TRAP","TRAP","TRAP","TRAP","TRAP","19","19","19","14 19","19","TRAP","19","TRAP","19","TRAP"],
        "14 19": ["TRAP","TRAP","TRAP","TRAP","TRAP","19","19","19","19","19 23","TRAP","19","TRAP","19","TRAP"],
        "19 23": ["TRAP","TRAP","TRAP","TRAP","TRAP","19","19","19","19","19","TRAP","19","TRAP","19","TRAP"],
        "4": ["TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP","TRAP"]
    }
    # fmt: on

    @staticmethod
    def _state2domain(s: State) -> Optional[Domain]:
        # fmt: off
        match s:
            case "0 2 7 18 20": return None
            case "1": return Domain.EOF
            case "3": return None
            case "22": return Domain.OPERATOR_COLON
            case "5 6": return Domain.SPACES
            case "8 19": return Domain.IDENT
            case "19": return Domain.IDENT
            case "11 19": return Domain.IDENT
            case "15 16": return Domain.COMMENT
            case "21": return Domain.DIGIT
            case "TRAP": return None
            case "16 17": return Domain.COMMENT
            case "12 19": return Domain.IDENT
            case "13 19": return Domain.IDENT
            case "14 19": return Domain.IDENT
            case "19 23": return Domain.KEYWORD_CLEAN
            case "9 19": return Domain.IDENT
            case "10 19": return Domain.KEYWORD_ALL
            case "4": return Domain.OPERATOR_BANG
        # fmt: on

    @staticmethod
    def classify_symbol(s: Optional[str]) -> SymbolType:
        if s is None:
            return SymbolType.EOF
        elif s == "!":
            return SymbolType.BANG
        elif s == ":":
            return SymbolType.COLON
        elif s in (" ", "\t"):
            return SymbolType.SPACE
        elif s in ("\n", "\r"):
            return SymbolType.NEW_LINE
        elif s == "c":
            return SymbolType.C
        elif s == "l":
            return SymbolType.L
        elif s == "e":
            return SymbolType.E
        elif s == "a":
            return SymbolType.A
        elif s == "n":
            return SymbolType.N
        elif s == "#":
            return SymbolType.HASH
        elif s.isdigit():
            return SymbolType.DIGIT
        elif s == "\\":
            return SymbolType.SLASH
        elif s.isalpha():
            return SymbolType.ALPHABET
        return SymbolType.OTHER_CHARS

    def __init__(self):
        self._state: State = START_STATE

    @property
    def state(self) -> State:
        return self._state

    def reset(self):
        self._state = START_STATE

    def peek_is_trap(self, st: SymbolType) -> bool:
        res = Automaton.DELTA[self._state][st]
        return res == "TRAP"

    def transition(self, st: SymbolType):
        self._state = Automaton.DELTA[self._state][st]

    def get_domain(self) -> Optional[Domain]:
        return Automaton._state2domain(self.state)


@dataclass(frozen=True)
class LexerError(Segment):
    message: str


class Lexer:
    def __init__(self, text: TextWithPosition):
        self._pos_text = text
        self._automaton = Automaton()
        self._recovering = False

    def _build_token(
        self, domain: Domain, attr: str, start: Position
    ) -> Optional[Token]:
        cur_pos = self._pos_text.position()
        prev_pos = Position(cur_pos.row, cur_pos.col - 1)
        match domain:
            case Domain.EOF:
                return EOF(start, prev_pos)
            case Domain.OPERATOR_BANG:
                return OperatorBang(start, prev_pos)
            case Domain.OPERATOR_COLON:
                return OperatorColon(start, prev_pos)
            case Domain.SPACES:
                return None
            case Domain.DIGIT:
                return Digit(start, prev_pos, int(attr))
            case Domain.KEYWORD_CLEAN:
                return KeywordClean(start, prev_pos)
            case Domain.KEYWORD_ALL:
                return KeywordAll(start, prev_pos)
            case Domain.COMMENT:
                return Comment(start, prev_pos, attr[1:].rstrip("\n"))
            case Domain.IDENT:
                return Ident(start, prev_pos, attr)

    def __iter__(self) -> Iterator[Token | LexerError]:
        while True:
            res = self._parse_prefix()
            if res is None:
                continue
            yield res
            if isinstance(res, EOF):
                return

    def _parse_prefix(self) -> Optional[Token] | LexerError:
        self._automaton.reset()
        start_pos = self._pos_text.position()
        pref = ""
        while True:
            s_opt: Optional[str] = self._pos_text.peek()
            st: SymbolType = Automaton.classify_symbol(s_opt)
            if self._automaton.peek_is_trap(st):
                domain_opt: Optional[Domain] = self._automaton.get_domain()
                if domain_opt is None:
                    if self._recovering:
                        self._pos_text.advance()
                        return None
                    self._recovering = True
                    err = LexerError(
                        start_pos, self._pos_text.position(), "Unexpected symbol"
                    )
                    return err
                token = self._build_token(domain_opt, pref, start_pos)
                self._recovering = False
                return token
            assert s_opt is not None
            pref += s_opt
            self._pos_text.advance()
            self._automaton.transition(st)


def main():
    t = TextWithPosition(sys.stdin)
    l = Lexer(t)
    for t in l:
        print(t)


if __name__ == "__main__":
    main()
