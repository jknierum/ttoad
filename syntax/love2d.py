import re

LOVE2D_RULES = [
    # comments
    (re.compile(r"--.*"), 3),

    # keywords
    (re.compile(r"\b(function|if|then|else|elseif|end|for|while|do|return|local|nil|false|true|and|or|not|repeat|until|break)\b"), 4),

    # function names - using fixed-width lookbehind (assume 1 space after function)
    (re.compile(r"(?<=\bfunction )([a-zA-Z_][a-zA-Z0-9_.:]*)"), 7),

    # strings
    (re.compile(r"\".*?\"|\'.*?\'"), 5),

    # numbers
    (re.compile(r"\b\d+\b"), 6),

    # assignment
    (re.compile(r"(?<![=!<>])=(?!=)"), 2),

    # comparison
    (re.compile(r"==|~=|<=|>=|<|>"), 2),

    # math
    (re.compile(r"\+|\-|\*|/|%|\^"), 2),
]