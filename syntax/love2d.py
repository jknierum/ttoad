# syntax/love2d.py
import re

# Lua keywords (complete list)
LUA_KEYWORDS = r"\b(and|break|do|else|elseif|end|false|for|function|if|in|local|nil|not|or|repeat|return|then|true|until|while)\b"

# Lua built-in functions
LUA_BUILTINS = r"\b(assert|collectgarbage|dofile|error|getmetatable|ipairs|load|loadfile|next|pairs|pcall|print|rawequal|rawget|rawlen|rawset|select|setmetatable|tonumber|tostring|type|xpcall|_G|_VERSION)\b"

# Lua math library
MATH_FUNCTIONS = r"\bmath\.(abs|acos|asin|atan|atan2|ceil|cos|cosh|deg|exp|floor|fmod|frexp|ldexp|log|log10|max|min|modf|pi|pow|rad|random|randomseed|sin|sinh|sqrt|tan|tanh)\b"

# Lua string library
STRING_FUNCTIONS = r"\bstring\.(byte|char|dump|find|format|gmatch|gsub|len|lower|match|rep|reverse|sub|upper)\b"

# Lua table library
TABLE_FUNCTIONS = r"\btable\.(concat|insert|move|pack|remove|sort|unpack)\b"

# Lua coroutine library
COROUTINE_FUNCTIONS = r"\bcoroutine\.(create|resume|running|status|wrap|yield)\b"

# Lua io library
IO_FUNCTIONS = r"\bio\.(close|flush|input|lines|open|output|popen|read|tmpfile|type|write)\b"

# Lua os library
OS_FUNCTIONS = r"\bos\.(clock|date|difftime|execute|exit|getenv|remove|rename|setlocale|time|tmpname)\b"

# Lua debug library
DEBUG_FUNCTIONS = r"\bdebug\.(debug|getfenv|gethook|getinfo|getlocal|getmetatable|getregistry|getupvalue|getuservalue|setfenv|sethook|setlocal|setmetatable|setupvalue|setuservalue|traceback|upvalueid|upvaluejoin)\b"

# Love2D callbacks (event functions)
LOVE_CALLBACKS = r"\b(love\.(load|update|draw|keypressed|keyreleased|mousepressed|mousereleased|mousemoved|wheelmoved|touchpressed|touchreleased|touchmoved|joystickpressed|joystickreleased|joystickaxis|joystickhat|focus|visible|quit|resize|threaderror|directorydropped|filedropped|textinput|textedited))\b"

# Love2D constants
LOVE_CONSTANTS = r"\b(love\.(draw_line|draw_fill|draw_hline|draw_vline|default_filter|default_mipmap_filter|keyboard_key|scancode|touch))\b"

# Build the LOVE2D_RULES list
LOVE2D_RULES = [
    # Multi-line comment start (handled separately, but we need to track state)
    (re.compile(r"--\[\[.*?\]\]", re.DOTALL), 1),  # Long comments

    # Single line comments (after code)
    (re.compile(r"--.*"), 1),

    # String literals (with escape sequences)
    (re.compile(r"\[\[.*?\]\]", re.DOTALL), 5),  # Long strings
    (re.compile(r"\".*?(?<!\\)\"", re.DOTALL), 5),  # Double-quoted strings
    (re.compile(r"\'.*?(?<!\\)\'", re.DOTALL), 5),  # Single-quoted strings

    # Numbers (hex, scientific, decimal)
    (re.compile(r"\b0x[0-9a-fA-F]+\b"), 6),  # Hex
    (re.compile(r"\b\d+\.\d*[eE]?[+-]?\d*\b"), 6),  # Float with exponent
    (re.compile(r"\b\d+\.\d+\b"), 6),  # Float
    (re.compile(r"\b\d+\b"), 6),  # Integer

    # Love2D callbacks (highest priority)
    (re.compile(LOVE_CALLBACKS), 7),

    # Love2D core module
    (re.compile(r"\blove\.(audio|data|event|filesystem|font|graphics|image|joystick|keyboard|math|mouse|physics|sound|system|thread|timer|touch|video|window)\b"), 4),

    # Love2D graphics functions
    (re.compile(r"\blove\.graphics\.(circle|rectangle|ellipse|arc|polygon|line|points?|print|draw|newFont|newImage|newQuad|newCanvas|newSpriteBatch|newParticleSystem|newText|newVideo|newMesh|newShader)\b"), 7),

    # Love2D graphics state functions
    (re.compile(r"\blove\.graphics\.(setColor|setBackgroundColor|setBlendMode|setFont|setLineWidth|setNewFont|setScissor|setStencil|setWireframe|origin|pop|push|rotate|scale|shear|translate)\b"), 8),

    # Love2D graphics getters
    (re.compile(r"\blove\.graphics\.(getColor|getBackgroundColor|getBlendMode|getFont|getHeight|getWidth|getDPI)\b"), 8),

    # Love2D audio functions
    (re.compile(r"\blove\.audio\.(newSource|play|pause|stop|rewind|setVolume|getVolume|setPosition|getPosition|setVelocity|getVelocity|setLooping|isLooping|setPitch|getPitch)\b"), 7),

    # Love2D keyboard functions
    (re.compile(r"\blove\.keyboard\.(isDown|setKeyRepeat|hasKeyRepeat|getKeyFromScancode|getScancodeFromKey)\b"), 7),

    # Love2D mouse functions
    (re.compile(r"\blove\.mouse\.(isDown|setVisible|isVisible|setPosition|getPosition|setCursor|getCursor|setGrabbed|isGrabbed)\b"), 7),

    # Love2D physics functions
    (re.compile(r"\blove\.physics\.(newWorld|newBody|newFixture|newShape|newCircleShape|newRectangleShape|newPolygonShape|newEdgeShape|newChainShape|newDistanceJoint|newFrictionJoint|newGearJoint|newMouseJoint|newPrismaticJoint|newPulleyJoint|newRevoluteJoint|newRopeJoint|newWeldJoint|newWheelJoint)\b"), 7),

    # Love2D filesystem functions
    (re.compile(r"\blove\.filesystem\.(exists|createDirectory|remove|getDirectoryItems|write|read|lines|load|isFile|isDirectory|getInfo|setIdentity|getIdentity|setRequirePath|getRequirePath)\b"), 7),

    # Love2D timer functions
    (re.compile(r"\blove\.timer\.(getTime|getDelta|sleep|step|getAverageDelta|getFPS)\b"), 7),

    # Love2D window functions
    (re.compile(r"\blove\.window\.(setMode|getMode|setTitle|getTitle|setIcon|getIcon|setVSync|getVSync|setFullscreen|getFullscreen|hasFocus|hasMouseFocus|setPosition|getPosition)\b"), 7),

    # Lua keywords
    (re.compile(LUA_KEYWORDS), 4),

    # Lua built-in functions
    (re.compile(LUA_BUILTINS), 7),

    # Math library
    (re.compile(MATH_FUNCTIONS), 7),

    # String library
    (re.compile(STRING_FUNCTIONS), 7),

    # Table library
    (re.compile(TABLE_FUNCTIONS), 7),

    # Coroutine library
    (re.compile(COROUTINE_FUNCTIONS), 7),

    # IO library
    (re.compile(IO_FUNCTIONS), 7),

    # OS library
    (re.compile(OS_FUNCTIONS), 7),

    # Debug library
    (re.compile(DEBUG_FUNCTIONS), 7),

    # Function calls (global functions)
    (re.compile(r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*\("), 7),

    # Self references
    (re.compile(r"\bself\b"), 7),

    # Operators (assignments, comparisons, math)
    (re.compile(r"(?<![=!<>])=(?!=)"), 2),  # Assignment
    (re.compile(r"==|~=|<=|>=|<|>"), 2),  # Comparison
    (re.compile(r"\+|\-|\*|/|%|\^|#"), 2),  # Math and length operators

    # Concatenation
    (re.compile(r"\.\."), 2),

    # Love2D constants (after module patterns)
    (re.compile(LOVE_CONSTANTS), 8),
]

# Export the variable
__all__ = ['LOVE2D_RULES']
