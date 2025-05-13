from typing import Generator, TextIO
from dataclasses import dataclass

from src.text.processors import Segment, Position, TextWithPosition
from src.common.abc import IGraphVizible
from src.common.pretty import wrap

# ==============================================


@dataclass(frozen=True)
class Keyword(Segment, IGraphVizible):
    value: str

    def to_graphviz(self) -> str:
        return '\t{} [label="{}"]\n'.format(
            self.node_name, wrap(str(self)).replace('"', "'")
        )


@dataclass(frozen=True)
class EOF(Segment, IGraphVizible):
    def to_graphviz(self) -> str:
        return '\t{} [label="{}"]\n'.format(
            self.node_name, wrap(str(self)).replace('"', "'")
        )


@dataclass(frozen=True)
class Number(Segment, IGraphVizible):
    value: int

    def to_graphviz(self) -> str:
        return '\t{} [label="{}"]\n'.format(
            self.node_name, wrap(str(self)).replace('"', "'")
        )


@dataclass(frozen=True)
class ScanError:
    message: str
    pos: Position


Token = Number  | Keyword | EOF


class Scanner:
    def __init__(self, f: TextIO):
        self._text = TextWithPosition(f)

    def skip_spaces(self):
        while True:
            cur = self._text.peek()
            if cur is None or not cur.isspace():
                return
            self._text.advance()

    def parse_keyword(self):
        cur = self._text.peek()
        assert cur == "`"
        self._text.advance()

    def find_whitespace(self):
        while True:
            cur = self._text.peek()
            if cur is None or cur.isspace():
                break
            self._text.advance()

    def assert_string(self, target: str):
        for i in range(len(target)):
            cur = self._text.peek()
            if cur != target[i]:
                return False
            self._text.advance()
        next = self._text.peek()
        if next is not None and not next.isspace():
            return False
        return True

    def __iter__(self) -> Generator[Token | ScanError, None, None]:
        errored = False
        while True:
            self.skip_spaces()
            cur = self._text.peek()
            if cur is None:
                yield EOF(start=self._text.position(), end=self._text.position())
                return
            if cur == "+":
                errored = False
                start_p = self._text.position()
                self._text.advance()
                end_p = self._text.position()
                yield Keyword("+", start=start_p, end=end_p)
            elif cur == "*":
                errored = False
                start_p = self._text.position()
                self._text.advance()
                end_p = self._text.position()
                yield Keyword("-", start=start_p, end=end_p)
            elif cur.isdigit():
                errored = False
                start_p = self._text.position()
                val = 0
                while True:
                    val += int(cur)
                    self._text.advance()
                    cur = self._text.peek()
                    if cur is None or not cur.isdigit():
                        break
                
                end_p = self._text.position()
                yield Number(val, start=start_p, end=end_p)
            else:
                if errored:
                    self._text.advance()
                    continue
                errored = True
                yield ScanError(f"unexpected symbol: {cur}", self._text.position())
                self._text.advance()
