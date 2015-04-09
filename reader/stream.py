"""
    The character stream.
"""
from data import Position

class CStream(object):
    def __init__(self, source, index=0, col=0, lno=1):
        self.col = col
        self.index = index
        self.lno = lno
        self.source = source

    def advance(self):
        c = self.current
        self.index += 1
        self.col += 1
        if c == '\n':
            self.lno += 1
            self.col = 0
        return c

    @property
    def current(self):
        return self.source[self.index]

    @property
    def filled(self):
        return self.index < len(self.source)

    @property
    def position(self):
        return Position(self.col, self.lno)

    def is_sym(self):
        if self.filled:
            ch = self.current
            return ch.isalpha() or ch == '_'
        return False

    def is_digit(self):
        if self.filled:
            return self.current.isdigit()
        return False

    def is_hex(self):
        if self.filled:
            return self.current in '0123456789abcdefABCDEF'
        return False

    def is_space(self):
        if self.filled:
            return self.current.isspace()
        return False