# syntax/__init__.py
from syntax.python import PYTHON_RULES
from syntax.love2d import LOVE2D_RULES
from syntax.bash import BASH_RULES

# Define SYNTAX_MAP for the editor
SYNTAX_MAP = {
    # Python files
    ".py": PYTHON_RULES,
    ".pyw": PYTHON_RULES,
    
    # Lua/Love2D files
    ".lua": LOVE2D_RULES,
    ".love": LOVE2D_RULES,
    
    # Shell scripts
    '.sh': BASH_RULES,
    '.bash': BASH_RULES,
    '.bashrc': BASH_RULES,
    '.bash_profile': BASH_RULES,
    '.bash_login': BASH_RULES,
    '.bash_logout': BASH_RULES,
    '.profile': BASH_RULES,
    '.zshrc': BASH_RULES,  # Basic support for zsh
    '.zsh': BASH_RULES,
    
    # Configuration files
    '.conf': BASH_RULES,
    '.cfg': BASH_RULES,
}

# Export the map
__all__ = ['SYNTAX_MAP']