import re

LOVE2D_RULES = [
    (re.compile(r"--.*"), 3),
    (re.compile(r"\b(function|end|if|then|else|local)\b"), 2),
    (re.compile(r"\b(love\.graphics|love\.update|love\.draw)\b"), 6),
    (re.compile(r"\".*?\"|\'.*?\'"), 5),
]