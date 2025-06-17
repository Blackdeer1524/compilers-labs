from typing import Generator, Literal, Optional
import re
from dataclasses import dataclass
from sys import stdin


SPACES_MATCHER = re.compile(r"\s+")


@dataclass(frozen=True)
class Position:
    row: int
    col: int


class Text:
    _eof_matcher = re.compile("$")

    def __init__(self, text: str):
        self._text = text
        self._cursor = 0

        self._row = 1
        self._col = 1

    def __repr__(self):
        return self._text[self._cursor :]

    def empty(self):
        return self._cursor >= len(self._text)

    def get(self) -> tuple[str, int]:
        return self._text, self._cursor

    def position(self) -> Position:
        return Position(self._row, self._col)

    def skip_spaces(self):
        spaces = SPACES_MATCHER.match(*self.get())
        if spaces is not None:
            self.forward(len(spaces[0]))

    def forward(self, n: int) -> None:
        for _ in range(self._cursor, min(len(self._text), self._cursor + n)):
            if self._text[self._cursor] == "\n":
                self._row += 1
                self._col = 1
            else:
                self._col += 1
            self._cursor += 1


@dataclass(frozen=True)
class Ident:
    value: str
    pos: Position

    _odd_len_matcher = re.compile(r"([a-zA-Z][a-zA-Z])*[a-zA-Z]")
    # * - comment; ** - keyword; ***+ - ident
    _stars_matcher = re.compile(r"\*\*\*+")

    @staticmethod
    def match_stars(text: Text) -> Optional["Ident"]:
        res = Ident._stars_matcher.match(*text.get())
        if res is None:
            return None
        pos = text.position()
        text.forward(len(res[0]))
        return Ident(res[0], pos)

    @staticmethod
    def match_odd_ident(text: Text) -> Optional["Ident"]:
        res = Ident._odd_len_matcher.match(*text.get())
        if res is None:
            return None
        pos = text.position()
        text.forward(len(res[0]))
        return Ident(res[0], pos)


@dataclass(frozen=True)
class Comment:
    value: str
    pos: Position

    _comment_matcher = re.compile(r"\*.*(\n|$)")

    @staticmethod
    def match(text: Text) -> Optional["Comment"]:
        res = Comment._comment_matcher.match(*text.get())
        if res is None:
            return None
        pos = text.position()
        text.forward(len(res[0]))
        return Comment(res[0], pos)


@dataclass(frozen=True)
class Keyword:
    value: Literal["end", "with", "**"]
    pos: Position

    _end_matcher = re.compile(r"end")
    _with_matcher = re.compile(r"with")
    _dstar_matcher = re.compile(r"\*\*")

    @staticmethod
    def match_end(text: Text) -> Optional["Keyword"]:
        res = Keyword._end_matcher.match(*text.get())
        if res is None:
            return None
        pos = text.position()
        text.forward(len(res[0]))
        return Keyword("end", pos)

    @staticmethod
    def match_dstar(text: Text) -> Optional["Keyword"]:
        res = Keyword._dstar_matcher.match(*text.get())
        if res is None:
            return None
        pos = text.position()
        text.forward(len(res[0]))
        return Keyword("**", pos)

    @staticmethod
    def match_with(text: Text) -> Optional["Keyword"]:
        res = Keyword._with_matcher.match(*text.get())
        if res is None:
            return None
        pos = text.position()
        text.forward(len(res[0]))
        return Keyword("with", pos)


Token = Ident | Comment | Keyword


@dataclass(frozen=True)
class SyntaxError:
    pos: Position


class Scanner:
    def __init__(self, text: str):
        self._text = Text(text)

    def __iter__(self) -> Generator[Token | SyntaxError, None, None]:
        already_yielded_error = False
        while True:
            self._text.skip_spaces()
            if self._text.empty():
                break

            wt = Keyword.match_with(self._text)
            if wt is not None:
                yield wt
                already_yielded_error = False
                continue

            end = Keyword.match_end(self._text)
            if end is not None:
                yield end
                already_yielded_error = False
                continue

            stars = Ident.match_stars(self._text)
            if stars is not None:
                yield stars
                already_yielded_error = False
                continue

            star_star = Keyword.match_dstar(self._text)
            if star_star is not None:
                yield star_star
                already_yielded_error = False
                continue

            comment = Comment.match(self._text)
            if comment is not None:
                yield comment
                already_yielded_error = False
                continue

            odd_len = Ident.match_odd_ident(self._text)
            if odd_len is not None:
                yield odd_len
                already_yielded_error = False
                continue

            if not already_yielded_error:
                already_yielded_error = True
                error_pos = self._text.position()
                yield SyntaxError(error_pos)

            self._text.forward(1)


def main():
    text = "".join(stdin)
    for t in Scanner(text):
        print(t)


if __name__ == "__main__":
    main()
