# syntax/bash.py
import re

BASH_RULES = [
    # comments
    (re.compile(r"#.*"), 1),

    # shebang line (special handling)
    (re.compile(r"^#!.*"), 4),  # Highlight as keyword/special

    # keywords (control structures, builtins, etc.)
    (re.compile(r"\b(if|then|elif|else|fi|for|while|until|do|done|case|esac|select|function|in|continue|break|return|exit|export|unset|readonly|shift|eval|exec|source|\.)\b"), 4),

    # commands/builtins
    (re.compile(r"\b(echo|printf|read|cd|pwd|mkdir|rmdir|rm|cp|mv|ls|cat|grep|sed|awk|cut|sort|uniq|wc|find|xargs|chmod|chown|ps|kill|jobs|fg|bg|wait|type|which|alias|unalias|bind|getopts)\b"), 7),  # Function name color

    # variable assignments (without $)
    (re.compile(r"\b[a-zA-Z_][a-zA-Z0-9_]*\s*=(?!=)"), 2),

    # variable usage ($VAR, ${VAR})
    (re.compile(r"\$[a-zA-Z_][a-zA-Z0-9_]*|\$\{[a-zA-Z_][a-zA-Z0-9_]*\}"), 6),  # Number color (or use yellow)

    # special variables ($?, $#, $@, $*, $$, $!, $-, $_)
    (re.compile(r"\$\?|\$\#|\$\@|\$\*|\$\$|\$!|\$-|\$_"), 6),

    # command substitution $(...)
    (re.compile(r"\$\([^)]*\)"), 6),

    # strings (double and single quoted)
    (re.compile(r"\".*?\"|\'.*?\'"), 5),

    # numbers
    (re.compile(r"\b[0-9]+\b"), 6),

    # redirections and pipes
    (re.compile(r">>?|<<?|\|"), 2),

    # logical operators
    (re.compile(r"&&|\|\|"), 2),

    # test operators inside [[ ]]
    (re.compile(r"==|!=|=~|<=|>=|<|>"), 2),

    # function names (after function keyword) - FIXED: using \s instead of \s+
    (re.compile(r"\bfunction\s+([a-zA-Z_][a-zA-Z0-9_]*)"), 7),

    # function names (name followed by ())
    (re.compile(r"([a-zA-Z_][a-zA-Z0-9_]*)\(\)"), 7),

    # path patterns (common directories/files)
    (re.compile(r"/(bin|boot|dev|etc|home|lib|mnt|opt|proc|root|sbin|sys|tmp|usr|var)(/|\\b)"), 8),  # Cyan color

    # brace expansions {1..10}
    (re.compile(r"\{[^}]+\}"), 8),
]
