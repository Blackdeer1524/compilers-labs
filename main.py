# $ is equivalent to
# ! is equivalent to
# : is equivalent to
# space is equivalent to
# a is equivalent to
# l is equivalent to
# c is equivalent to
# e is equivalent to
# n is equivalent to
# # is equivalent to
# 0 is equivalent to 1
# 1 is equivalent to
# b is equivalent to d
# d is equivalent to
# NEW_LINE is equivalent to
# SLASH is equivalent to


from dataclasses import dataclass
from enum import Enum, IntEnum, StrEnum, auto
from typing import Literal, Optional, TextIO


States = (
    Literal["START"]
    | Literal["1"]
    | Literal["3"]
    | Literal["4"]
    | Literal["5 6"]
    | Literal["8 19"]
    | Literal["19"]
    | Literal["11 19"]
    | Literal["15 16"]
    | Literal["21"]
    | Literal["TRAP"]
    | Literal["16"]
    | Literal["16 17"]
    | Literal["12 19"]
    | Literal["13 19"]
    | Literal["14 19"]
    | Literal["10 19"]
    | Literal["9 19"]
)


class SymbolType(IntEnum):
    EOF = 0
    BANG = auto()
    COLON = auto()
    SPACE = auto()
    NEW_LINE = auto()
    C = auto()
    L = auto()
    E = auto()
    A = auto()
    N = auto()
    HASH = auto()
    DIGIT = auto()
    OTHER_CHARS = auto()
    SLASH = auto()
    UNKNOWN = auto()


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


class A:
    def __init__(self, text: TextWithPosition):
        self._text = text
        self._state: States = "START"

    # 18 * 14
    DELTA: dict[States, list[States]] = {
        "START": [
            "1",
            "3",
            "4",
            "5 6",
            "5 6",
            "8 19",
            "19",
            "11 19",
            "19",
            "19",
            "15 16",
            "21",
            "19",
            "TRAP",
        ],
        "1": [
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
        ],
        "3": [
            "TRAP",
            "4",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
        ],
        "4": [
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
        ],
        "5 6": [
            "TRAP",
            "TRAP",
            "TRAP",
            "5 6",
            "5 6",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
        ],
        "8 19": [
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "19",
            "9 19",
            "19",
            "19",
            "19",
            "TRAP",
            "19",
            "19",
            "TRAP",
        ],
        "19": [
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "19",
            "19",
            "19",
            "19",
            "19",
            "TRAP",
            "19",
            "19",
            "TRAP",
        ],
        "11 19": [
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "19",
            "12 19",
            "19",
            "19",
            "19",
            "TRAP",
            "19",
            "19",
            "TRAP",
        ],
        "15 16": [
            "TRAP",
            "15 16",
            "15 16",
            "15 16",
            "16",
            "15 16",
            "15 16",
            "15 16",
            "15 16",
            "15 16",
            "15 16",
            "15 16",
            "15 16",
            "16 17",
        ],
        "21": [
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "21",
            "TRAP",
            "TRAP",
        ],
        "TRAP": [
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
        ],
        "16": [
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
        ],
        "16 17": [
            "TRAP",
            "15 16",
            "15 16",
            "15 16",
            "15 16",
            "15 16",
            "15 16",
            "15 16",
            "15 16",
            "15 16",
            "15 16",
            "15 16",
            "15 16",
            "TRAP",
        ],
        "12 19": [
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "19",
            "19",
            "19",
            "13 19",
            "19",
            "TRAP",
            "19",
            "19",
            "TRAP",
        ],
        "13 19": [
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "14 19",
            "19",
            "19",
            "19",
            "19",
            "TRAP",
            "19",
            "19",
            "TRAP",
        ],
        "14 19": [
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "19",
            "19",
            "19",
            "19",
            "10 19",
            "TRAP",
            "19",
            "19",
            "TRAP",
        ],
        "10 19": [
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "19",
            "19",
            "19",
            "19",
            "19",
            "TRAP",
            "19",
            "19",
            "TRAP",
        ],
        "9 19": [
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "TRAP",
            "19",
            "10 19",
            "19",
            "19",
            "19",
            "TRAP",
            "19",
            "19",
            "TRAP",
        ],
    }

    def classify_char(self, c: Optional[str]) -> SymbolType: 
        if c is None:
            return SymbolType.EOF
        elif c == '$':
            return SymbolType.EOF
        elif c == "!":
            return SymbolType.BANG

        return SymbolType.UNKNOWN


    def parse(self):
        c = self._text.peek()
        

        A.DELTA[self._state][]


        

# |             |   $  |   !  |   :   | space | NEW_LINE |   a   |   l   |   c   |   e   |   n   |   #   | DIGIT | OTHER_CHAR |  SLASH |
# | START |   1  |   3  |   4   |  5 6  |    5 6   | 8 19  |  19   | 11 19 |  19   |  19   | 15 16 |  21   |    19      |  TRAP  |
# |      1      | TRAP | TRAP | TRAP  | TRAP  |   TRAP   | TRAP  | TRAP  | TRAP  | TRAP  | TRAP  | TRAP  | TRAP  |   TRAP     |  TRAP  |
# |      3      | TRAP |   4  | TRAP  | TRAP  |   TRAP   | TRAP  | TRAP  | TRAP  | TRAP  | TRAP  | TRAP  | TRAP  |   TRAP     |  TRAP  |
# |      4      | TRAP | TRAP | TRAP  | TRAP  |   TRAP   | TRAP  | TRAP  | TRAP  | TRAP  | TRAP  | TRAP  | TRAP  |   TRAP     |  TRAP  |
# |     5 6     | TRAP | TRAP | TRAP  |  5 6  |    5 6   | TRAP  | TRAP  | TRAP  | TRAP  | TRAP  | TRAP  | TRAP  |   TRAP     |  TRAP  |
# |    8 19     | TRAP | TRAP | TRAP  | TRAP  |   TRAP   |  19   | 9 19  |  19   |  19   |  19   | TRAP  |  19   |    19      |  TRAP  |
# |     19      | TRAP | TRAP | TRAP  | TRAP  |   TRAP   |  19   |  19   |  19   |  19   |  19   | TRAP  |  19   |    19      |  TRAP  |
# |    11 19    | TRAP | TRAP | TRAP  | TRAP  |   TRAP   |  19   | 12 19 |  19   |  19   |  19   | TRAP  |  19   |    19      |  TRAP  |
# |    15 16    | TRAP | 15 16| 15 16 | 15 16 |    16    | 15 16 | 15 16 | 15 16 | 15 16 | 15 16 | 15 16 | 15 16 |   15 16    |  16 17 |
# |     21      | TRAP | TRAP | TRAP  | TRAP  |   TRAP   | TRAP  | TRAP  | TRAP  | TRAP  | TRAP  | TRAP  |  21   |   TRAP     |  TRAP  |
# |             | TRAP | TRAP | TRAP  | TRAP  |   TRAP   | TRAP  | TRAP  | TRAP  | TRAP  | TRAP  | TRAP  | TRAP  |   TRAP     |  TRAP  |
# |     16      | TRAP | TRAP | TRAP  | TRAP  |   TRAP   | TRAP  | TRAP  | TRAP  | TRAP  | TRAP  | TRAP  | TRAP  |   TRAP     |  TRAP  |
# |    16 17    | TRAP | 15 16| 15 16 | 15 16 |   15 16  | 15 16 | 15 16 | 15 16 | 15 16 | 15 16 | 15 16 | 15 16 |   15 16    |  TRAP  |
# |    12 19    | TRAP | TRAP | TRAP  | TRAP  |   TRAP   |  19   |  19   |  19   | 13 19 |  19   | TRAP  |  19   |    19      |  TRAP  |
# |    13 19    | TRAP | TRAP | TRAP  | TRAP  |   TRAP   | 14 19 |  19   |  19   |  19   |  19   | TRAP  |  19   |    19      |  TRAP  |
# |    14 19    | TRAP | TRAP | TRAP  | TRAP  |   TRAP   |  19   |  19   |  19   |  19   | 10 19 | TRAP  |  19   |    19      |  TRAP  |
# |    10 19    | TRAP | TRAP | TRAP  | TRAP  |   TRAP   |  19   |  19   |  19   |  19   |  19   | TRAP  |  19   |    19      |  TRAP  |
# |    9 19     | TRAP | TRAP | TRAP  | TRAP  |   TRAP   |  19   | 10 19 |  19   |  19   |  19   | TRAP  |  19   |    19      |  TRAP  |
