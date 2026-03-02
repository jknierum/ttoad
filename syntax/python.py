import re

PYTHON_RULES = [
    # comments
    (re.compile(r"#.*"), 3),

    # keywords (def and class are here)
    (re.compile(r"\b(def|class|if|elif|else|return|for|while|import|from|as|pass|break|continue|not|and|or|is|None|True|False|in)\b"), 4),

    # function names - using fixed-width lookbehind (assume 1 space after def)
    (re.compile(r"(?<=\bdef )([a-zA-Z_][a-zA-Z0-9_]*)"), 7),

    # class names - using fixed-width lookbehind (assume 1 space after class)
    (re.compile(r"(?<=\bclass )([a-zA-Z_][a-zA-Z0-9_]*)"), 7),

    # strings
    (re.compile(r"\".*?\"|\'.*?\'"), 5),

    # numbers
    (re.compile(r"\b\d+\b"), 6),

    # assignment
    (re.compile(r"(?<![=!<>])=(?!=)"), 2),

    # comparison
    (re.compile(r"==|!=|<=|>="), 2),

    # math
    (re.compile(r"\+|\-|\*|/|%"), 2),
]