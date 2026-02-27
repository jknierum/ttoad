import re

PYTHON_RULES = [

    # comments
    (re.compile(r"#.*"), 3),

    # keywords
    (re.compile(r"\b(def|class|if|elif|else|return|for|while|import|from|as|pass|break|continue|not)\b"), 4),

    # strings
    (re.compile(r"\".*?\"|\'.*?\'"), 5),

    # numbers
    (re.compile(r"\b\d+\b"), 6),

    # extra
    (re.compile(r"\b(key)\b"),4),


    # assignment
    (re.compile(r"(?<![=!<>])=(?!=)"), 2),

    # comparison
    (re.compile(r"==|!=|<=|>="), 2),

    # math
    (re.compile(r"\+|\-|\*|/|%"), 2),

]
