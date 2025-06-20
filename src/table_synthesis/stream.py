class Stream:
    def __init__(self, tab_width: int = 4):
        self.tab_width = tab_width
        self.reset()

    def reset(self):
        self.txt = ""
        self.indent_level = 0
        self.is_str_start = True

    def _adjust_indent_level(self, delta: int) -> "Stream":
        self.indent_level = max(self.indent_level + delta, 0)
        return self

    def endl(self) -> "Stream":
        self.txt += "\n"
        self.is_str_start = True
        return self

    def push_line(self, s: str = "") -> "Stream":
        if self.is_str_start:
            self.txt += self.tab_width * self.indent_level * " "
            self.is_str_start = False
        self.txt += s
        self.endl()
        return self

    def emit(self):
        res = self.txt
        self.reset()
        return res

    def indent(self):
        class Indenter:
            def __init__(self, stream: Stream):
                self._stream = stream

            def __enter__(self):
                self._stream._adjust_indent_level(+1)
                return self._stream

            def __exit__(self, exc_type, exc_val, exc_tb):
                self._stream._adjust_indent_level(-1)

        return Indenter(self)
