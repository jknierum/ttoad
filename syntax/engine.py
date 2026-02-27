import curses
import re

class SyntaxHighlighter:
    def __init__(self, rules):
        self.rules = rules

    def highlight_line(self, stdscr, y, x, line):
        pos = 0

        while pos < len(line):
            match, color = self._find_match(line, pos)

            if match:
                stdscr.addstr(y, x + pos, match.group(), curses.color_pair(color))
                pos = match.end()
            else:
                stdscr.addstr(y, x + pos, line[pos])
                pos += 1

    def _find_match(self, line, start):
        for pattern, color in self.rules:
            match = pattern.match(line, start)
            if match:
                return match, color
        return None, None