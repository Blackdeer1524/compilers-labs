import sys
from typing import Generator, Optional, TextIO
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


# Строковые литералы: ограничены обратными кавычками, могут
#   занимать несколько строчек текста, для включения
#   обратной кавычки она удваивается.

# Числовые литералы: десятичные литералы представляют
#   собой последовательности десятичных цифр, двоичные
#    — последовательности нулей и единиц, оканчивающиеся буквой «b».

# Идентификаторы: последовательности десятичных цифр и
#   знаков «?», «*» и «|», не начинающиеся с цифры.


@dataclass(frozen=True)
class Segment:
    start: Position
    end: Position


@dataclass(frozen=True)
class Integer(Segment):
    value: int


@dataclass(frozen=True)
class String(Segment):
    value: str


@dataclass(frozen=True)
class Identifier(Segment):
    value: str


@dataclass
class EOF: ...


@dataclass(frozen=True)
class ScanError:
    message: str
    pos: Position


Token = Integer | String | EOF | Identifier


class Scanner:
    _IDENT_PREFIX = ("?", "*", "|")

    def __init__(self, f: TextIO):
        self._text = Text(f)

        self._row = 1
        self._col = 1

    def position(self) -> Position:
        return Position(self._row, self._col)

    def parse_ident(self) -> str:
        assert self._text.peek() in Scanner._IDENT_PREFIX

        acc = ""
        while True:
            cur = self._text.peek()
            if cur is None:
                return acc

            if cur not in Scanner._IDENT_PREFIX and not cur.isnumeric():
                return acc

            acc += cur
            self._advance()

    # fails only in case of EOF
    def parse_str(self) -> Optional[str]:
        assert self._text.peek() == "`"
        self._advance()

        acc = ""
        while True:
            cur = self._text.peek()
            if cur is None:
                return None

            if cur == "`":
                self._advance()
                next = self._text.peek()
                if next == "`":
                    acc += "`"
                    self._advance()
                else:
                    return acc
            else:
                acc += cur
                self._advance()

    def parse_int(self) -> int:
        cur = self._text.peek()
        assert cur is not None and cur.isnumeric()

        acc = 0
        is_binary = True
        while True:
            cur = self._text.peek()
            if cur is None:
                return acc

            if not cur.isnumeric():
                if cur == "b" and is_binary:
                    self._advance()
                    return int(str(acc), 2)
                return acc

            int_cur = int(cur)
            if int_cur > 1:
                is_binary = False

            acc = acc * 10 + int(cur)
            self._advance()

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

            if cur.isnumeric():
                p = self.position()
                result = self.parse_int()
                end_p = self.position()
                yield Integer(p, Position(end_p.row, end_p.col - 1), result)
                errored = False
                continue
            elif cur in Scanner._IDENT_PREFIX:
                p = self.position()
                result = self.parse_ident()
                end_p = self.position()
                yield Identifier(p, Position(end_p.row, end_p.col - 1), result)
                errored = False
                continue
            elif cur == "`":
                p = self.position()
                string = self.parse_str()
                if string is None:
                    yield ScanError('Expected ", but EOF found', self.position())
                    return
                end_p = self.position()
                yield String(p, Position(end_p.row, end_p.col - 1), string)
                errored = False
                continue
            else:
                if errored:
                    self._advance()
                    continue
                errored = True
                yield ScanError(f"unexpected symbol: {cur}", self.position())
                self._advance()


def main():
    s = Scanner(sys.stdin)
    for t in s:
        print(t)


if __name__ == "__main__":
    main()