from typing import Optional, TextIO
from dataclasses import dataclass


@dataclass(frozen=True)
class Position:
    row: int
    col: int


@dataclass(frozen=True, kw_only=True)
class Segment:
    start: Position
    end: Position


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
