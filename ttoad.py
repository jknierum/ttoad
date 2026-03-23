import curses
import sys
import time
import os
from datetime import datetime
import signal
import os
import subprocess
import importlib.util
from syntax.engine import SyntaxHighlighter
from syntax import SYNTAX_MAP
import argparse

# Default keybindings (fallback if config not found)
DEFAULT_NORMAL_MODE = {
    'up': curses.KEY_UP,
    'down': curses.KEY_DOWN,
    'left': curses.KEY_LEFT,
    'right': curses.KEY_RIGHT,
    'page_up': curses.KEY_PPAGE,
    'page_down': curses.KEY_NPAGE,
    'home': curses.KEY_HOME,
    'end': curses.KEY_END,
    'insert_mode': 105,
    'find_mode': 102,
    'find_mode_global': 70,
    'find_ctrl': 6,
    'jump_mode': 106,
    'jump_mode_ctrl': 10,
    'select_start': 0,
    'select_word': 119,
    'select_line': 108,
    'select_block': 98,
    'select_all': 97,
    'yank': 121,
    'yank_ctrl': 25,
    'paste': 112,
    'paste_ctrl': 16,
    'cut': 120,
    'cut_ctrl': 24,
    'delete': 100,
    'comment': 99,
    'wrap_round': 40,
    'wrap_curly': 123,
    'wrap_square': 91,
    'wrap_quote_single': 39,
    'wrap_quote_double': 34,
    'undo': 21,
    'redo': 18,
    'save': 19,
    'save_as': 1,
    'quit': 17,
}

DEFAULT_SETTINGS = {
    'TAB_SIZE': 4,
    'LEFT_MARGIN': 6,
    'TOP_MARGIN': 3,
    'LINE_NUMBER_STYLE': "normal",
    'COMMENT_CHAR': "#",
    'AUTO_CLOSE_BRACKETS': True,
    'AUTO_CLOSE_QUOTES': True,
    'AUTO_INDENT': True,
    'AUTO_COMPLETE': True,
    'AUTO_COMPLETE_SUGGESTIONS': 5,
    'UNDO_LIMIT': 500,
}

def load_config():
    """Load keybindings and settings from config files"""
    config_dir = os.path.expanduser("~/.config/ttoad")
    keybindings = DEFAULT_NORMAL_MODE.copy()
    settings = DEFAULT_SETTINGS.copy()

    # Create config directory if it doesn't exist
    if not os.path.exists(config_dir):
        try:
            os.makedirs(config_dir)
            # Create default config files
            create_default_configs(config_dir)
        except:
            pass  # Fail silently, use defaults

    # Try to load keybindings
    config_file = os.path.join(config_dir, "config.py")
    if os.path.exists(config_file):
        try:
            spec = importlib.util.spec_from_file_location("user_config", config_file)
            user_config = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(user_config)

            # Update keybindings if they exist
            if hasattr(user_config, 'NORMAL_MODE'):
                keybindings.update(user_config.NORMAL_MODE)
        except:
            pass  # Use defaults on error

    # Try to load settings
    settings_file = os.path.join(config_dir, "settings.py")
    if os.path.exists(settings_file):
        try:
            spec = importlib.util.spec_from_file_location("user_settings", settings_file)
            user_settings = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(user_settings)

            # Update settings
            for key in DEFAULT_SETTINGS:
                if hasattr(user_settings, key):
                    settings[key] = getattr(user_settings, key)
        except:
            pass  # Use defaults on error

    return keybindings, settings

def create_default_configs(config_dir):
    """Create default config files if they don't exist"""
    # Create config.py
    config_path = os.path.join(config_dir, "config.py")
    if not os.path.exists(config_path):
        with open(config_path, 'w') as f:
            f.write('''# Ttoad Keybindings Configuration
# Key codes reference:
# - Printable chars: ASCII values (97 = 'a', 65 = 'A', etc.)
# - Ctrl+letter: 1-26 (Ctrl+A=1, Ctrl+B=2, etc.)
# - Special keys: Use curses constants (curses.KEY_UP, curses.KEY_F1, etc.)
# - Enter: 13 (after curses.nonl())
# - Backspace: 127 or 8

import curses

NORMAL_MODE = {
    # Navigation
    'up': curses.KEY_UP,
    'down': curses.KEY_DOWN,
    'left': curses.KEY_LEFT,
    'right': curses.KEY_RIGHT,
    'page_up': curses.KEY_PPAGE,
    'page_down': curses.KEY_NPAGE,
    'home': curses.KEY_HOME,
    'end': curses.KEY_END,

    # Mode switching
    'insert_mode': 105,  # 'i'
    'find_mode': 102,     # 'f'
    'find_mode_global': 70,  # 'F'
    'jump_mode': 74,      # 'J'
    'jump_mode_ctrl': 10,  # Ctrl+J

    # Selection
    'select_start': 0,     # Ctrl+Space
    'select_word': 119,    # 'w'
    'select_line': 108,    # 'l'
    'select_block': 98,    # 'b'
    'select_all': 97,      # 'a'

    # Actions
    'yank': 121,           # 'y'
    'yank_ctrl': 25,       # Ctrl+Y
    'paste': 112,          # 'p'
    'paste_ctrl': 16,      # Ctrl+P
    'cut': 120,            # 'x'
    'cut_ctrl': 24,        # Ctrl+X
    'delete': 100,         # 'd'
    'comment': 99,         # 'c'

    # Bracket wrapping
    'wrap_round': 40,      # '('
    'wrap_curly': 123,     # '{'
    'wrap_square': 91,     # '['
    'wrap_quote_single': 39,  # "'"
    'wrap_quote_double': 34,  # '"'

    # Undo/Redo
    'undo': 21,            # Ctrl+U
    'redo': 18,            # Ctrl+R

    # File operations
    'save': 19,            # Ctrl+S
    'save_as': 1,          # Ctrl+A
    'quit': 17,            # Ctrl+Q
}
''')

    # Create settings.py
    settings_path = os.path.join(config_dir, "settings.py")
    if not os.path.exists(settings_path):
        with open(settings_path, 'w') as f:
            f.write('''# Ttoad Editor Settings

# Editor appearance
TAB_SIZE = 4
LEFT_MARGIN = 6
TOP_MARGIN = 3
LINE_NUMBER_STYLE = "normal"  # "normal" or "vim"
COMMENT_CHAR = "#"

# Behavior
AUTO_CLOSE_BRACKETS = True
AUTO_CLOSE_QUOTES = True
AUTO_INDENT = True
AUTO_COMPLETE = True
AUTO_COMPLETE_SUGGESTIONS = 5

# History
UNDO_LIMIT = 500
''')

parser = argparse.ArgumentParser(
    prog="Ttoad",
    description="Ttoad: a Tiny terminal model code editor ",
    epilog="""

    --Keybindings--
    # Mode switching
    'insert_mode': 105,      # 'i'
    'find_mode': 102,        # 'f'
    'find_mode_global': 70,  # 'F'
    'jump_mode': 74,         # 'J'
    'jump_mode_ctrl': 10,    # Ctrl+J

    # Selection
    'select_start': 0,       # Ctrl+Space
    'select_word': 119,      # 'w'
    'select_line': 108,      # 'l'
    'select_block': 98,      # 'b'
    'select_all': 97,        # 'a'

    # Actions
    'yank': 121,             # 'y'
    'yank_ctrl': 25,         # Ctrl+Y
    'paste': 112,            # 'p'
    'paste_ctrl': 16,        # Ctrl+P
    'cut': 120,              # 'x'
    'cut_ctrl': 24,          # Ctrl+X
    'delete': 100,           # 'd'
    'comment': 99,           # 'c'

    # Undo/Redo
    'undo': 21,              # Ctrl+U
    'redo': 18,              # Ctrl+R

    # File operations
    'save': 19,              # Ctrl+S
    'save_as': 1,            # Ctrl+A
    'quit': 17,              # Ctrl+Q

    # Mouse
    click to set cursor
    click and drag to select
    dbl click to exit selection

    Config.py and settings.py files in ~/.config/ttoad/
    Move ttoad to back: ctrl + z (fg to bring back to front)

    """,
    formatter_class=argparse.RawTextHelpFormatter
)

import subprocess
import sys



# Add the fzf flag
parser.add_argument(
    "-f", "--fzf",
    action="store_true",
    help="Open fzf file picker to select a file"
)

parser.add_argument(
    "filename",
    nargs="?",
    default=None,
    help="File to open (creates new file if it doesn't exist)"
)


args = parser.parse_args()

# Handle fzf flag
if args.fzf:
    try:
        import subprocess
        result = subprocess.run(['fzf'], capture_output=True, text=True, check=True)
        selected = result.stdout.strip()
        if selected:
            filename = selected
        else:
            print("No file selected")
            sys.exit(0)
    except subprocess.CalledProcessError:
        print("File selection cancelled")
        sys.exit(0)
    except FileNotFoundError:
        print("Error: fzf is not installed. Please install fzf first.")
        sys.exit(1)
else:
    filename = args.filename

# If no filename provided (and not using fzf), show error
if not filename:
    print("Enter a filename to create or edit a file.")
    print("Usage: ttoad [filename] or ttoad -f to use fzf")
    sys.exit(1)

def open_file(filename):
    text = []
    try:
        with open(filename, "r") as f:
            for line in f:
                text.append(line.rstrip("\n"))  # remove newline
    except FileNotFoundError:
        text = [""]  # start with empty text if file doesn’t exist
    return text

# Load the file
try:
    text = open_file(filename)
except Exception as e:
    # If there's any error opening the file, start with empty buffer
    text = [""]
    print(f"Warning: Could not open {filename}, starting with empty buffer: {e}", file=sys.stderr)

def load_syntax(filename):
    ext = os.path.splitext(filename)[1]
    rules = SYNTAX_MAP.get(ext, [])
    return SyntaxHighlighter(rules)

signal.signal(signal.SIGINT, signal.SIG_IGN) #ctrl + c
#signal.signal(signal.SIGTSTP, signal.SIG_IGN) #crtl + z

os.system("stty -ixon")


def save_file(filename, text):
    for i, line in enumerate(text):
        text[i] = text[i].rstrip()

    if not filename:
        return
    try:
        with open(filename, "w") as f:
            for line in text:
                f.write(str(line).rstrip() + "\n")  # convert to string just in case
    except Exception as e:
        # optional: show error in editor
        pass

def format_display_filename(path):
    if not path:
        return "New File"

    # Normalize path
    path = os.path.normpath(path)

    parent = os.path.basename(os.path.dirname(path))
    filename = os.path.basename(path)

    if parent:
        return f"{parent}/{filename}"
    else:
        return filename

def delete_current_word(text, cursor_y, cursor_x):
    line = text[cursor_y]

    if not line:
        return cursor_x

    length = len(line)

    # If cursor is at end of line, look left
    if cursor_x == length:
        cursor_x -= 1
        if cursor_x < 0:
            return 0

    char = line[cursor_x]

    # -------------------------
    # CASE 1: Delete spaces
    # -------------------------
    if char == " ":
        start = cursor_x
        while start > 0 and line[start - 1] == " ":
            start -= 1

        end = cursor_x
        while end < length and line[end] == " ":
            end += 1

        text[cursor_y] = line[:start] + line[end-1:]
        return start

    # -------------------------
    # CASE 2: Delete word
    # -------------------------
    if char.isalnum() or char == "_":
        start = cursor_x
        while start > 0 and (line[start - 1].isalnum() or line[start - 1] == "_"):
            start -= 1

        end = cursor_x
        while end < length and (line[end].isalnum() or line[end] == "_"):
            end += 1

        text[cursor_y] = line[:start] + line[end:]
        return start

    return cursor_x

def get_current_word(text, cursor_y, cursor_x):
    if cursor_y < 0 or cursor_y >= len(text):
        return cursor_x, cursor_x

    line = text[cursor_y]
    start = cursor_x
    end = cursor_x

    if not line:
        return start, end

    # If cursor is at end of line, step back one
    if cursor_x == len(line) and cursor_x > 0:
        cursor_x -= 1

    # If not on a word character, return empty
    if not (line[cursor_x].isalnum() or line[cursor_x] == "_"):
        return start, end

    # Find word start
    start = cursor_x
    while start > 0 and (line[start - 1].isalnum() or line[start - 1] == "_"):
        start -= 1

    # Find word end
    end = cursor_x
    while end < len(line) and (line[end].isalnum() or line[end] == "_"):
        end += 1

    return start, end

def get_current_prefix(text, cursor_y, cursor_x):
    if cursor_y < 0 or cursor_y >= len(text):
        return ""

    line = text[cursor_y]

    i = cursor_x - 1

    if not line or cursor_x == 0:
        return ""


    if not (line[i].isalnum() or line[i] == "_"):
        return ""

    start = i
    while start > 0 and (line[start - 1].isalnum() or line[start - 1] == "_"):
        start -= 1

    return line[start:cursor_x]

def collect_words(text):
    words = set()

    for line in text:
        current = ""
        for ch in line:
            if ch.isalnum() or ch == "_":
                current += ch
            else:
                if current:
                    words.add(current)
                    current = ""
        if current:
            words.add(current)

    return words

def get_autocomplete_list(prefix, words):
    return sorted([w for w in words if w.lower().startswith(prefix.lower()) and w.lower() != prefix.lower()])


def apply_autocomplete(mode, query, text, cursor_y, cursor_x, suggestion, prefix):
    line = text[cursor_y]
    remainder = suggestion[len(prefix):]


    if mode == "find":
        return query + remainder

    else:
        text[cursor_y] = (
            line[:cursor_x - len(prefix)] + suggestion + line[cursor_x:]
        )
        return cursor_x + len(remainder)

def can_autocomplete(text, cursor_y, cursor_x, mode, nav_key_last, prefix = ""):
    line = text[cursor_y]
    if mode == "normal":
        return False
    if nav_key_last:
        return False

    if not prefix:
        return False
    # Case 1: Cursor at end of line
    #if cursor_x == len(line):
    #    return True

    # Case 2: Character after cursor is space
#    if line[cursor_x] == " ":
#        return True

    #if line[cursor_x] in "(){}[] ":
    #   return True

    return True

def get_indent_level(line):
    #"""Return number of leading spaces"""
    count = 0
    for char in line:
        if char == " ":
            count += 1
        else:
            break
    return count

def check_for_block(text, cursor_y, comment_cha):
    if not text:
        return cursor_y, cursor_y

    target_indent = get_indent_level(text[cursor_y])

    start = cursor_y
    end = cursor_y

    # Check upward
    y = cursor_y - 1
    while y >= 0:
        if len(text[y]) == 0:
            break
        elif get_indent_level(text[y]) > target_indent:
            start = y
            y -= 1
        else:
            break

    # Check downward
    y = cursor_y + 1
    while y < len(text):
        line = text[y]
        if len(text[y]) == 0:
            break

        elif line[0] == comment_cha:
            end = y
            y += 1

        elif get_indent_level(text[y]) >= target_indent:
            end = y
            y += 1
        else:
            break

    return start, end

def save_undo_state(undo_stack, text, cursor_x, cursor_y, scroll_pos_x, scroll_pos_y):

    undo_stack.append((
        text.copy(),
        cursor_x,
        cursor_y,
        scroll_pos_x,
        scroll_pos_y
    ))

    # Clear redo stack when new action happens (IMPORTANT)
    # redo_stack.clear()  ← do this outside this function if needed

    # Limit history size
    if len(undo_stack) > 500:
        undo_stack.pop(0)

def perform_undo(undo_stack, redo_stack, text, cursor_x, cursor_y, scroll_pos_x, scroll_pos_y):

    if not undo_stack:
        return text, cursor_x, cursor_y, scroll_pos_x, scroll_pos_y

    # Save current state to redo
    redo_stack.append((
        text.copy(),
        cursor_x,
        cursor_y,
        scroll_pos_x,
        scroll_pos_y
    ))

    prev_text, prev_x, prev_y, prev_scroll_x, prev_scroll_y = undo_stack.pop()

    return (
        prev_text.copy(),
        prev_x,
        prev_y,
        prev_scroll_x,
        prev_scroll_y
    )

def perform_redo(undo_stack, redo_stack, text, cursor_x, cursor_y, scroll_pos_x, scroll_pos_y):

    if not redo_stack:
        return text, cursor_x, cursor_y, scroll_pos_x, scroll_pos_y

    # Save current state to undo
    undo_stack.append((
        text.copy(),
        cursor_x,
        cursor_y,
        scroll_pos_x,
        scroll_pos_y
    ))

    next_text, next_x, next_y, next_scroll_x, next_scroll_y = redo_stack.pop()

    return (
        next_text.copy(),
        next_x,
        next_y,
        next_scroll_x,
        next_scroll_y
    )

def paste_from_clipboard():
    try:
        result = subprocess.run(
            ['wl-paste'],
            capture_output=True,
            text=True
        )
        return result.stdout
    except:
        return ""

def insert_paste(text, cursor_y, cursor_x, paste_string):
    # Strip any trailing newline that might be causing issues
    paste_string = paste_string.rstrip('\n')

    lines = paste_string.split('\n')
    current_line = text[cursor_y]
    before_cursor = current_line[:cursor_x]
    after_cursor = current_line[cursor_x:]

    if len(lines) == 1:
        # Single line paste
        text[cursor_y] = before_cursor + lines[0] + after_cursor
        cursor_x += len(lines[0])
    else:
        # Multi-line paste
        text[cursor_y] = before_cursor + lines[0]

        for i in range(1, len(lines)):
            cursor_y += 1
            if i == len(lines) - 1:
                text.insert(cursor_y, lines[i] + after_cursor)
            else:
                text.insert(cursor_y, lines[i])

        cursor_x = len(lines[-1])

    return cursor_y, cursor_x


def copy_to_clipboard(text):
    try:
        process = subprocess.Popen(
        ['wl-copy'],
        stdin=subprocess.PIPE,
        text=True
        )
        process.communicate(text)
    except Exception as e:
        pass


def safe_addstr(stdscr, y, x, string, attr=0):
    height, width = stdscr.getmaxyx()

    if y < 0 or y >= height or x < 0 or x >= width:
        return

    stdscr.addstr(y, x, string[:width - x], attr)

def is_selected(y, x, cursor_y, cursor_x, start_y, start_x):
    if (y, x) < (start_y, start_x):
        start_y, start_x, cursor_y, cursor_x = cursor_y, cursor_x, start_y, start_x

    return (y, x) >= (start_y, start_x) and (y, x) < (cursor_y, cursor_x)

def get_selected_text(text, start_y, start_x, end_y, end_x):

    if (start_y, start_x) > (end_y, end_x):
        start_y, start_x, end_y, end_x = end_y, end_x, start_y, start_x

    result = []

    for y in range(start_y, end_y + 1):

        line = text[y]

        if y == start_y and y == end_y:
            result.append(line[start_x:end_x])

        elif y == start_y:
            result.append(line[start_x:])

        elif y == end_y:
            result.append(line[:end_x])

        else:
            result.append(line)

    return "\n".join(result)

def delete_selection(text, select_start_y, select_start_x, cursor_y, cursor_x):
    # Normalize selection order
    if (cursor_y, cursor_x) < (select_start_y, select_start_x):
        start_y, start_x = cursor_y, cursor_x
        end_y, end_x = select_start_y, select_start_x
    else:
        start_y, start_x = select_start_y, select_start_x
        end_y, end_x = cursor_y, cursor_x

    # Handle zero-width selection
    if start_y == end_y and start_x == end_x:
        return start_y, start_x

    # Get the text before the selection
    before = "\n".join(text[:start_y])
    if start_y < len(text):
        before += ("\n" if before else "") + text[start_y][:start_x]

    # Get the text after the selection
    after = text[end_y][end_x:] + ("\n" if end_y < len(text)-1 else "")
    if end_y + 1 < len(text):
        after += "\n".join(text[end_y + 1:])

    # Combine and split
    full_text = before + after
    new_text = full_text.split("\n") if full_text else [""]

    # Update the original text
    text.clear()
    text.extend(new_text)

    # Return cursor position at the merge point
    return start_y, start_x

def indent_selection(text, select_start_y, cursor_y, tab="    "):

    # Normalize order
    start_y = min(select_start_y, cursor_y)
    end_y = max(select_start_y, cursor_y)

    # Indent each line
    for i in range(start_y, end_y + 1):
        text[i] = tab + text[i]

    # Move cursor to stay visually correct
    return start_y, end_y

def unindent_selection(text, select_start_y, cursor_y, tab="    "):

    start_y = min(select_start_y, cursor_y)
    end_y = max(select_start_y, cursor_y)

    for i in range(start_y, end_y + 1):
        if text[i].startswith(tab):
            text[i] = text[i][len(tab):]
def find_all(text, word):
    results = []

    if not word:
        return results

    word_len = len(word)
    word_lower = word.lower()  # Convert search word to lowercase once

    for y, line in enumerate(text):
        x = 0
        line_lower = line.lower()  # Convert current line to lowercase

        while True:
            x = line_lower.find(word_lower, x)  # Search in lowercase version

            if x == -1:
                break

            start_y = y
            start_x = x
            end_y = y
            end_x = x + word_len

            results.append((start_y, start_x, end_y, end_x))

            x += word_len  # move forward to avoid infinite loop

    return results

def next_match(matches, cursor_y, cursor_x):
    if not matches:
        return cursor_y, cursor_x

    # find first match after cursor
    for start_y, start_x, end_y, end_x in matches:
        if (start_y, start_x) > (cursor_y, cursor_x):
            return start_y, start_x

    # wrap around to first match
    return matches[0][0], matches[0][1]

def last_match(matches, cursor_y, cursor_x):
    if not matches:
        return cursor_y, cursor_x

    # Find first match that ends BEFORE the cursor position
    # (not just starts before)
    for start_y, start_x, end_y, end_x in reversed(matches):
        # Check if this match ends before the cursor position
        if (end_y, end_x) < (cursor_y, cursor_x):
            return start_y, start_x

    # If no match ends before cursor, wrap to last match
    return matches[-1][0], matches[-1][1]

def find_and_highlight(text, query, cursor_y, cursor_x, scroll_pos_y, visible_height):
    """Find all matches and return matches list and visible matches for highlighting"""
    if not query:
        return [], []

    matches = find_all(text, query)

    # Filter matches that are visible on screen
    visible_matches = []
    for start_y, start_x, end_y, end_x in matches:
        if start_y >= scroll_pos_y and start_y < scroll_pos_y + visible_height:
            visible_matches.append((start_y, start_x, end_y, end_x))

    return matches, visible_matches

def find_next_match(matches, cursor_y, cursor_x):
    """Find the next match after cursor position"""
    if not matches:
        return None

    # Find first match after cursor
    for start_y, start_x, end_y, end_x in matches:
        if (start_y, start_x) > (cursor_y, cursor_x):
            return (start_y, start_x)

    # Wrap around to first match
    return (matches[0][0], matches[0][1])


def add_before_after_selected(key_before, key_after, text, select_start_x , select_start_y, cursor_x, cursor_y):
    start_line = text[select_start_y]
    text[select_start_y] = start_line[:select_start_x] + chr(key_before) + start_line[select_start_x:]
    select_start_x += 1
    if select_start_y == cursor_y:
        cursor_x +=1

    end_line = text[cursor_y]
    text[cursor_y] = end_line[:cursor_x] + chr(key_after) + end_line[cursor_x:]

def get_comment_char(filename):
    """Return the appropriate comment character based on file extension"""
    if not filename:
        return "#"  # Default

    ext = os.path.splitext(filename)[1]
    basename = os.path.basename(filename)

    # Map file extensions to comment characters
    comment_map = {
        # Python
        '.py': '#',
        '.pyw': '#',

        # Lua/Love2D
        '.lua': '--',
        '.love': '--',

        # Shell scripts
        '.sh': '#',
        '.bash': '#',
        '.bashrc': '#',
        '.bash_profile': '#',
        '.zsh': '#',
        '.zshrc': '#',

        # Configuration files
        '.conf': '#',
        '.cfg': '#',

        # C/C++ style
        '.c': '//',
        '.cpp': '//',
        '.h': '//',
        '.hpp': '//',
        '.java': '//',
        '.js': '//',
        '.ts': '//',
        '.go': '//',
        '.rs': '//',
        '.swift': '//',

        # HTML/XML style
        '.html': '<!--',
        '.htm': '<!--',
        '.xml': '<!--',
        '.xhtml': '<!--',

        # CSS
        '.css': '/*',
        '.scss': '//',
        '.sass': '//',

        # Ruby
        '.rb': '#',
        '.erb': '<%#',

        # SQL
        '.sql': '--',

        # Makefiles
        'Makefile': '#',
        'makefile': '#',
        '.mk': '#',

        # Docker
        'Dockerfile': '#',

        # Default
        'default': '#'
    }

    # Check by basename first (for special files without extensions)
    if basename in comment_map:
        return comment_map[basename]

    # Then check by extension
    return comment_map.get(ext, '#')

def editior(stdscr, filename):
    # Load user configuration
    keybindings, settings = load_config()

    # Apply settings to variables
    tab_size = settings['TAB_SIZE']
    left_margin = settings['LEFT_MARGIN']
    top_margin = settings['TOP_MARGIN']
    suggestions_shown = settings['AUTO_COMPLETE_SUGGESTIONS']

    # Get dynamic comment character based on file type
    dynamic_comment_char = get_comment_char(filename)

    # Use user setting if specified, otherwise use dynamic one
    comment_cha = settings.get('COMMENT_CHAR', dynamic_comment_char)
    # If the user setting is the default, override with dynamic
    if comment_cha == DEFAULT_SETTINGS['COMMENT_CHAR']:
        comment_cha = dynamic_comment_char

    suggestions_shown = settings['AUTO_COMPLETE_SUGGESTIONS']

    # Enable resize detection
    curses.cbreak()
    stdscr.keypad(True)

    # Enable mouse support
    curses.mousemask(curses.ALL_MOUSE_EVENTS | curses.REPORT_MOUSE_POSITION)
    curses.mouseinterval(0)  # Get mouse events as quickly as possible

    curses.set_escdelay(1)
    status_message = ""
    status_time = 0
    curses.curs_set(1)
    curses.nonl()

    try:
        curses.resizeterm(*stdscr.getmaxyx())
    except:
        pass

    curses.start_color()  # Enable color mode
    curses.use_default_colors()  # Optional: let terminal default background show

    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)   # operators/assignments
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)  # comments
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)    # keywords
    curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK) # strings
    curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)# numbers
    curses.init_pair(7, curses.COLOR_CYAN, curses.COLOR_BLACK)   # function names
    curses.init_pair(8, curses.COLOR_YELLOW, curses.COLOR_BLACK)  # decorators
    stdscr.clear()

    if filename:
        text = open_file(filename)
    else:
        text = [""]

    saved_text_for_check = text.copy()

    # Create syntax highlighter
    if filename:
        ext = os.path.splitext(filename)[1]
        basename = os.path.basename(filename)

        # Try to get rules by extension first
        rules = SYNTAX_MAP.get(ext, [])

        # If no rules found, try by basename (for files like .bashrc)
        if not rules:
            rules = SYNTAX_MAP.get(basename, [])
    else:
        rules = []

    highlighter = SyntaxHighlighter(rules)

    cursor_y = 0
    cursor_x = 0

    line_length = len(text[cursor_y]) if text else 0

    select_mode = False
    select_start_y = 0
    select_start_x = 0

    mode = "normal"
    yanked = ""
    last_key = -1
    last_key_time = 0
    clear_last_key = False
    stored_cursor_pos_x = 0
    store_prefix = ""
    suggestion_sel = 0
    suggestion_on = False
    find_string = ""
    nav_key_last = False

    scroll_pos_y = 0
    scroll_pos_x = 0
    jump_pos = ""
    undo_stack = []
    redo_stack = []
    tm_colour = 1
    saved_text_for_check = text.copy()

    find_query = ""
    find_y = 0
    find_x = 0
    query = ""

    find_matches = []  # Store all matches
    find_visible_matches = []  # Store visible matches for highlighting
    current_match_pos = None  # Current match position (for cursor)

    current_match_range = None  # Will store (start_y, start_x, end_y, end_x)

   # Mouse state variables
    mouse_dragging = False
    mouse_click_start_y = 0
    mouse_click_start_x = 0

    def get_tab_level(line, tab_size=4):
        count = 0

        for char in line:
            if char == " ":
                count += 1
            else:
                break

        return count // tab_size

    while True:

        stdscr.clear()
        current_time = datetime.now().strftime("%H:%M:%S")
        if text:
            line_length = len(text[cursor_y])
        else:
            line_length = 0

        # Minimum window size check
        height, width = stdscr.getmaxyx()
        if height < 10 or width < 30:
            stdscr.clear()
            stdscr.addstr(0, 0, "Terminal too small! Need at least 10x30", curses.A_BOLD)
            stdscr.addstr(2, 0, "Resize window or press Ctrl+Q to exit")
            stdscr.refresh()
            key = stdscr.getch()
            if key == keybindings['quit']:  # Ctrl+Q
                exit()
            continue

        visible_height = height - (top_margin * 2)
        visible_width = width - left_margin

        # Ensure valid dimensions
        if visible_height < 1:
            visible_height = 1
        if visible_width < 1:
            visible_width = 1

        mode_dis = mode.upper()

        suggestion_on = False
        screen_y = cursor_y - scroll_pos_y

        #check if cursor is longer than line
        if cursor_x > line_length:
            cursor_x = line_length

        # Top margin
        dis_filename = format_display_filename(filename)
        if saved_text_for_check == text:
            tm_colour = 5
        else:
            tm_colour = 1

        if status_message:
            stdscr.addstr(1, left_margin, " " + status_message + " ", curses.color_pair(5) | curses.A_BOLD | curses.A_REVERSE)
            if time.time() - status_time > 2:
                status_message = ""
        elif mode == "find":
            stdscr.addstr(1, left_margin, " FIND: " + query + " ", curses.color_pair(tm_colour) | curses.A_BOLD | curses.A_REVERSE)

        elif mode == "jump":
            stdscr.addstr(1, left_margin, " JUMP: " + jump_pos + " ", curses.color_pair(tm_colour) | curses.A_BOLD | curses.A_REVERSE)

        else:
            stdscr.addstr(1, left_margin, " " + dis_filename + " ", curses.color_pair(tm_colour) | curses.A_BOLD | curses.A_REVERSE)

        # Draw text
        height, width = stdscr.getmaxyx()
        visible_height = height - (top_margin * 2)  # number of lines we can display
        visible_width = width - (left_margin)

        # Calculate how many lines we can actually draw
        max_draw_lines = min(visible_height, len(text) - scroll_pos_y)

        for i in range(max_draw_lines):
            line_idx = scroll_pos_y + i
            if line_idx >= len(text):
                break

            line = text[line_idx]

            # Don't draw past bottom of screen
            if i + top_margin >= height:
                break

            # Draw the line
            visible_line = line[scroll_pos_x:scroll_pos_x + visible_width]

            # Ensure we don't try to draw beyond right edge
            if left_margin < width:
                highlighter.highlight_line(stdscr, i + top_margin, left_margin, visible_line)

            screen_line_y = line_idx

            # Draw line numbers
            line_count = str(i + 1 + scroll_pos_y)  # +scroll_pos_y to show actual line number
            line_num_width = 4

            if i == cursor_y - scroll_pos_y:
                stdscr.addstr(i + top_margin, 0, str(int(line_count)).rjust(line_num_width + 1),
                             curses.color_pair(5) | curses.A_REVERSE | curses.A_BOLD)
            else:
                stdscr.addstr(i + top_margin, 0, str(int(line_count)).rjust(line_num_width),
                             curses.color_pair(1))

            # Character-by-character drawing for selection/find highlighting
            for j, ch in enumerate(visible_line):
                screen_x = j + left_margin
                screen_y = i + top_margin
                actual_x = j + scroll_pos_x
                actual_y = line_idx

                # Check if this character is part of a find match
                is_match = False
                if mode == "find" and query and find_visible_matches:
                    for match_y, match_start_x, match_end_y, match_end_x in find_visible_matches:
                        if actual_y == match_y and actual_x >= match_start_x and actual_x < match_end_x:
                            is_match = True
                            break

                # Check if this is the current match
                is_current_match = False
                if current_match_range:
                    match_y, match_start_x, match_end_y, match_end_x = current_match_range
                    if actual_y == match_y and actual_x >= match_start_x and actual_x < match_end_x:
                        is_current_match = True

                if select_mode and is_selected(
                    actual_y,
                    actual_x,
                    cursor_y,
                    cursor_x,
                    select_start_y,
                    select_start_x
                ):
                    stdscr.addstr(screen_y, screen_x, ch, curses.A_REVERSE)
                elif is_current_match and mode == "find":
                    stdscr.addstr(screen_y, screen_x, ch, curses.A_REVERSE | curses.A_BOLD)
                elif is_match:
                    stdscr.addstr(screen_y, screen_x, ch, curses.color_pair(5) | curses.A_BOLD | curses.A_REVERSE)
                # else: normal text - already handled by syntax highlighter

        #MODE DISPLAY
        stdscr.addstr(height - 2, left_margin, " " + mode_dis + " ", curses.color_pair(5) | curses.A_REVERSE | curses.A_BOLD)

        #YANKED
        if yanked:
            first_line = yanked.split("\n", 1)[0]

            y = height - 2
            x = width - len(first_line) - 1
            max_len = width - x - 1
            if len(first_line) > max_len:
                first_line = first_line[:max_len - 3] + "..."

            safe_addstr(
                stdscr,
                y,
                x,
                first_line,
                curses.color_pair(1)
            )


        #Auto complete
        if mode == "find":
            prefix = query
            store_prefix = prefix
            words = collect_words(text)
            suggestion_list = get_autocomplete_list(prefix, words)


            if suggestion_list:
                suggestion_sel = max(0, min(suggestion_sel, len(suggestion_list) - 1))
            else:
                suggestion_sel = 0

            if prefix and can_autocomplete(text, cursor_y - scroll_pos_y, cursor_x, mode, nav_key_last, prefix):
                if suggestion_list:
                    suggestion = suggestion_list[suggestion_sel]

            if prefix and can_autocomplete(text, cursor_y - scroll_pos_y, cursor_x, mode, nav_key_last, prefix):
                if suggestion_list:
                    suggestion = suggestion_list[suggestion_sel]
                    suggestion_on = True
                    for i in range(min(suggestions_shown, len(suggestion_list))):
                        if i == suggestion_sel:
                            safe_addstr(stdscr, 1 + i + 1, left_margin + len(" FIND: "), suggestion_list[i], curses.color_pair(5) | curses.A_REVERSE)
                        else:
                            safe_addstr(stdscr, 1 + i + 1, left_margin + len(" FIND: "), suggestion_list[i], curses.color_pair(1) | curses.A_REVERSE)

                        safe_addstr(stdscr, 1, left_margin + len(prefix) + len(" FIND: "), suggestion_list[suggestion_sel][len(prefix):], curses.color_pair(1))
                else:
                    suggestion_on = False
                    suggestion_sel = 0
                    suggestion = None

        else:
            prefix = get_current_prefix(text, cursor_y, cursor_x)
            store_prefix = prefix
            words = collect_words(text)
            suggestion_list = get_autocomplete_list(prefix, words)


            if suggestion_list:
                suggestion_sel = max(0, min(suggestion_sel, len(suggestion_list) - 1))
            else:
                suggestion_sel = 0

            if prefix and can_autocomplete(text, cursor_y - scroll_pos_y, cursor_x, mode, nav_key_last, prefix) and mode == "insert":
                if suggestion_list:
                    suggestion = suggestion_list[suggestion_sel]

            if prefix and can_autocomplete(text, cursor_y - scroll_pos_y, cursor_x, mode, nav_key_last, prefix) and mode == "insert":
                if suggestion_list:
                    suggestion = suggestion_list[suggestion_sel]
                    suggestion_on = True
                    for i in range(min(suggestions_shown, len(suggestion_list))):
                        if i == suggestion_sel:
                            safe_addstr(stdscr, cursor_y - scroll_pos_y + top_margin + i + 1, (cursor_x - scroll_pos_x) + left_margin - len(prefix), suggestion_list[i], curses.color_pair(5) | curses.A_REVERSE)
                        else:
                            safe_addstr(stdscr, cursor_y - scroll_pos_y + top_margin + i + 1, (cursor_x - scroll_pos_x) + left_margin - len(prefix), suggestion_list[i], curses.color_pair(1) | curses.A_REVERSE)

                        safe_addstr(stdscr, cursor_y - scroll_pos_y + top_margin, (cursor_x - scroll_pos_x) + left_margin, suggestion_list[suggestion_sel][len(prefix):], curses.color_pair(1))
                else:
                    suggestion_on = False
                    suggestion_sel = 0
                    suggestion = None


        # Clip cursor so it stays inside screen
        cursor_y = max(0, min(cursor_y, len(text) - 1))

        # Clamp screen_y to visible area
        screen_y = cursor_y - scroll_pos_y
        screen_y = max(0, min(screen_y, visible_height - 1))
        screen_x = cursor_x - scroll_pos_x
        screen_x = max(0, min(screen_x, visible_width - 1))

        stdscr.move(screen_y + top_margin, screen_x + left_margin)

        stdscr.refresh()

        key = stdscr.getch()


        # Handle mouse events
        if key == curses.KEY_MOUSE:
            try:
                _, mx, my, _, bstate = curses.getmouse()

                # Convert screen coordinates to text coordinates
                text_y = my - top_margin + scroll_pos_y
                text_x = mx - left_margin + scroll_pos_x

                # Handle scroll wheel events
                if bstate & curses.BUTTON4_PRESSED:
                    scroll_pos_y = max(0, scroll_pos_y - 3)
                    continue

                elif bstate & curses.BUTTON5_PRESSED:
                    scroll_pos_y = min(len(text) - visible_height, scroll_pos_y + 3)
                    continue

                # Ensure coordinates are within bounds for click/drag
                if 0 <= text_y < len(text):
                    # Clamp text_x to line length
                    text_x = max(0, min(text_x, len(text[text_y])))

                    # Mouse button pressed
                    if bstate & curses.BUTTON1_PRESSED:
                        if select_mode:
                            if text_y == cursor_y and text_x == cursor_x:
                                select_mode = False
                            else:
                                cursor_y = text_y
                                cursor_x = text_x
                        else:
                            select_mode = False
                            select_start_y = text_y
                            select_start_x = text_x
                            cursor_y = text_y
                            cursor_x = text_x
                            stored_cursor_pos_x = cursor_x
                            stored_cursor_pos_y = cursor_y
                            mouse_dragging = True
                        continue

                    # Mouse button released
                    elif bstate & curses.BUTTON1_RELEASED:
                        if text_y == cursor_y and text_x == cursor_x:
                            mouse_dragging = False
#                            select_mode =  False
                        else:
                            select_mode = True
                            cursor_y = text_y
                            cursor_x = text_x
                        continue

            except:
                pass  # Ignore mouse errors

    # INSERT MODE
        if mode == "insert":
            if 32 <= key <= 126:
                save_undo_state(
                    undo_stack,
                    text,
                    cursor_x,
                    cursor_y,
                    scroll_pos_x,
                    scroll_pos_y
                )
                redo_stack.clear()
                line = text[cursor_y]
                text[cursor_y] = line[:cursor_x] + chr(key) + line[cursor_x:]
                cursor_x += 1

                if key in (39, 34):
                    line = text[cursor_y]
                    text[cursor_y] = line[:cursor_x] + chr(key) + line[cursor_x:]

                elif key == 91:
                    line = text[cursor_y]
                    text[cursor_y] = line[:cursor_x] + chr(93) + line[cursor_x:]

                elif key == 123:
                    line = text[cursor_y]
                    text[cursor_y] = line[:cursor_x] + chr(125) + line[cursor_x:]

                elif key == 40:
                    line = text[cursor_y]
                    text[cursor_y] = line[:cursor_x] + chr(41) + line[cursor_x:]

                select_mode = False


    #JUMP TO LINE MODE
        elif mode == "jump":
            if 48 <= key <= 57:
                jump_pos = jump_pos + chr(key)


            elif key == curses.KEY_BACKSPACE or key == 127:
                jump_pos = jump_pos[:-1]

            elif key == 13: #ENTER
                try:
                    target = int(jump_pos)-1
                except ValueError:
                    target = cursor_y
                    jump_pos = ""

                cursor_x = 0
                cursor_y = max(0, min(target, len(text) - 1))
                scroll_pos_y = max(0, cursor_y - visible_height // 2)

                mode = "normal"
                continue

    #FIND MODE
        elif mode == "find":
            if select_mode:
                selected = get_selected_text(
                            text,
                            select_start_y,
                            select_start_x,
                            cursor_y,
                            cursor_x
                        )
                query = selected
                select_mode = False
            else:
                # Update matches whenever query changes
                find_matches, find_visible_matches = find_and_highlight(
                    text, query, cursor_y, cursor_x, scroll_pos_y, visible_height
                )

                # Find the next match from current cursor position
                next_match_pos = find_next_match(find_matches, cursor_y, cursor_x -1)
                if next_match_pos:
                    current_match_pos = next_match_pos
                    # Update the full range for the current match
                    for match in find_matches:
                        if match[0] == next_match_pos[0] and match[1] == next_match_pos[1]:
                            current_match_range = match
                            break
                    # Move cursor to the match position
                    cursor_y, cursor_x = current_match_pos

                    # Adjust scroll to make the match visible
                    if cursor_y < scroll_pos_y:
                        scroll_pos_y = cursor_y
                    elif cursor_y >= scroll_pos_y + visible_height:
                        scroll_pos_y = cursor_y - visible_height + 1

                    if cursor_x < scroll_pos_x:
                        scroll_pos_x = cursor_x
                    elif cursor_x >= scroll_pos_x + visible_width:
                        scroll_pos_x = cursor_x - visible_width + 1

            #ENTER
            if key == 13:
                if suggestion_on == True:
                    query = apply_autocomplete(
                            mode, query, text, cursor_y, cursor_x, suggestion, prefix
                        )
                    # Update matches after autocomplete
                    find_matches, find_visible_matches = find_and_highlight(
                        text, query, cursor_y, cursor_x, scroll_pos_y, visible_height
                    )
                    # Find and move to next match
                    next_match_pos = find_next_match(find_matches, cursor_y, cursor_x)
                    if next_match_pos:
                        cursor_y, cursor_x = next_match_pos
                        # Find the full match range
                        for match in find_matches:
                            if match[0] == cursor_y and match[1] == cursor_x:
                                current_match_range = match
                                # Set selection to cover the entire word
                                select_mode = True
                                select_start_y = match[0]
                                select_start_x = match[1]
                                # Move cursor to end of the word
                                cursor_x = match[3]  # end_x
                                break

            #TAB
            if key == 9:
                if find_matches:
                    # Use the start of the current match for navigation
                    if select_mode and current_match_range:
                        nav_y, nav_x = current_match_range[0], current_match_range[1]
                    else:
                        nav_y, nav_x = cursor_y, cursor_x

                    # Get the next match position
                    next_pos = next_match(find_matches, nav_y, nav_x)
                    cursor_y, cursor_x = next_pos

                    # Find the full match range for this position
                    for match in find_matches:
                        if match[0] == cursor_y and match[1] == cursor_x:
                            current_match_range = match
                            # Set selection to cover the entire word
                            select_mode = True
                            select_start_y = match[0]
                            select_start_x = match[1]
                            # Move cursor to end of the word
                            cursor_x = match[3]  # end_x
                            break

                    # Adjust scroll to make the match visible
                    scroll_pos_y = cursor_y - int(visible_height / 2)
                    if scroll_pos_y > len(text):
                        scroll_pos_y = cursor_y
                    elif scroll_pos_y < 0:
                        scroll_pos_y = cursor_y
                    scroll_pos_x = 0

            #BTAB
            elif key == curses.KEY_BTAB or key == 353:
                if find_matches:
                    # Get the previous match position
                    prev_pos = last_match(find_matches, cursor_y, cursor_x)
                    cursor_y, cursor_x = prev_pos

                    # Find the full match range for this position
                    for match in find_matches:
                        if match[0] == cursor_y and match[1] == cursor_x:
                            current_match_range = match
                            # Set selection to cover the entire word
                            select_mode = True
                            select_start_y = match[0]
                            select_start_x = match[1]
                            # Move cursor to end of the word
                            cursor_x = match[3]  # end_x
                            break

                    # Adjust scroll to make the match visible
                    scroll_pos_y = cursor_y - int(visible_height / 2)
                    if scroll_pos_y > len(text):
                        scroll_pos_y = cursor_y
                    elif scroll_pos_y < 0:
                        scroll_pos_y = cursor_y
                    scroll_pos_x = 0


            #LETTERS
            elif 32 <= key <= 126:
                query = query + chr(key)
                # Find next match from current cursor position after updating query
                find_matches, find_visible_matches = find_and_highlight(
                    text, query, cursor_y, cursor_x, scroll_pos_y, visible_height
                )
                next_match_pos = find_next_match(find_matches, cursor_y, cursor_x)
                if next_match_pos:
                    cursor_y, cursor_x = next_match_pos
                    # Find the full match range
                    for match in find_matches:
                        if match[0] == cursor_y and match[1] == cursor_x:
                            current_match_range = match
                            # Set selection to cover the entire word
                            select_mode = True
                            select_start_y = match[0]
                            select_start_x = match[1]
                            # Move cursor to end of the word
                            cursor_x = match[3]  # end_x
                            break

                    # Adjust scroll to make the match visible
                    if cursor_y < scroll_pos_y:
                        scroll_pos_y = cursor_y
                    elif cursor_y >= scroll_pos_y + visible_height:
                        scroll_pos_y = cursor_y - visible_height + 1

                    if cursor_x < scroll_pos_x:
                        scroll_pos_x = cursor_x
                    elif cursor_x >= scroll_pos_x + visible_width:
                        scroll_pos_x = cursor_x - visible_width + 1

            #BACKSPACE
            elif key == curses.KEY_BACKSPACE or key == 127:
                query = query[:-1]
                # Find next match from current cursor position after updating query
                find_matches, find_visible_matches = find_and_highlight(
                    text, query, cursor_y, cursor_x, scroll_pos_y, visible_height
                )
                next_match_pos = find_next_match(find_matches, cursor_y, cursor_x)
                if next_match_pos:
                    cursor_y, cursor_x = next_match_pos
                    # Find the full match range
                    for match in find_matches:
                        if match[0] == cursor_y and match[1] == cursor_x:
                            current_match_range = match
                            # Set selection to cover the entire word
                            select_mode = True
                            select_start_y = match[0]
                            select_start_x = match[1]
                            # Move cursor to end of the word
                            cursor_x = match[3]  # end_x
                            break

                    # Adjust scroll to make the match visible
                    if cursor_y < scroll_pos_y:
                        scroll_pos_y = cursor_y
                    elif cursor_y >= scroll_pos_y + visible_height:
                        scroll_pos_y = cursor_y - visible_height + 1

                    if cursor_x < scroll_pos_x:
                        scroll_pos_x = cursor_x
                    elif cursor_x >= scroll_pos_x + visible_width:
                        scroll_pos_x = cursor_x - visible_width + 1


    # NORMAL MODE
        elif mode == "normal":
            #ESC
            if key == keybindings['insert_mode']:
                if  select_mode:
                    save_undo_state(
                        undo_stack,
                        text,
                        cursor_x,
                        cursor_y,
                        scroll_pos_x,
                        scroll_pos_y
                    )

                    redo_stack.clear()

                    cursor_y, cursor_x = delete_selection(
                            text,
                            select_start_y,
                            select_start_x,
                            cursor_y,
                            cursor_x
                    )

                mode = "insert"
                select_mode = False


            #ACTIONS (delete(d), copy(c)/yank(y), paste(p), paste over line(P), cut(x), jump forword(j), jump back(J), comment(/), tab(t), unTab(T))

            #(),{},[],'',"" when selected
            elif key == 91: #[]
                if select_mode:
                    save_undo_state(
                        undo_stack,
                        text,
                        cursor_x,
                        cursor_y,
                        scroll_pos_x,
                        scroll_pos_y
                    )

                    redo_stack.clear()

                    add_before_after_selected(key, 93, text, select_start_x , select_start_y, cursor_x, cursor_y)

                    select_mode = False


            elif key == 40: #()
                if select_mode:
                    save_undo_state(
                        undo_stack,
                        text,
                        cursor_x,
                        cursor_y,
                        scroll_pos_x,
                        scroll_pos_y
                    )

                    redo_stack.clear()

                    add_before_after_selected(key, 41, text, select_start_x , select_start_y, cursor_x, cursor_y)

                    select_mode = False


            elif key == 123: #{}
                if select_mode:
                    save_undo_state(
                        undo_stack,
                        text,
                        cursor_x,
                        cursor_y,
                        scroll_pos_x,
                        scroll_pos_y
                    )

                    redo_stack.clear()

                    add_before_after_selected(key, 125, text, select_start_x , select_start_y, cursor_x, cursor_y)

                    select_mode = False


            elif key in  (39,34): #"",''
                if select_mode:
                    save_undo_state(
                        undo_stack,
                        text,
                        cursor_x,
                        cursor_y,
                        scroll_pos_x,
                        scroll_pos_y
                    )

                    redo_stack.clear()

                    add_before_after_selected(key, key, text, select_start_x , select_start_y, cursor_x, cursor_y)

                    select_mode = False


            #JUMP j
            elif key == keybindings['jump_mode']:
                jump_pos = ""
                mode = "jump"

            #y,Y
            elif key == keybindings['yank']:
                if select_mode:
                    selected = get_selected_text(
                        text,
                        select_start_y,
                        select_start_x,
                        cursor_y,
                        cursor_x
                    )
                    yanked = selected
                    copy_to_clipboard(selected)
                    select_mode = False

            #p,P: Paste
            elif key == keybindings['paste']:
                save_undo_state(
                    undo_stack,
                    text,
                    cursor_x,
                    cursor_y,
                    scroll_pos_x,
                    scroll_pos_y
                )
                redo_stack.clear()


                if  select_mode:
                    cursor_y, cursor_x = delete_selection(
                            text,
                            select_start_y,
                            select_start_x,
                            cursor_y,
                            cursor_x
                        )

                paste = paste_from_clipboard()
                cursor_y, cursor_x = insert_paste(text, cursor_y, cursor_x, paste)
                select_mode = False

            #CUT
            elif key == keybindings['cut']:
                save_undo_state(
                    undo_stack,
                    text,
                    cursor_x,
                    cursor_y,
                    scroll_pos_x,
                    scroll_pos_y
                )
                redo_stack.clear()

                if select_mode:
                    selected = get_selected_text(
                        text,
                        select_start_y,
                        select_start_x,
                        cursor_y,
                        cursor_x
                    )
                    copy_to_clipboard(selected)

                    cursor_y, cursor_x = delete_selection(
                        text,
                        select_start_y,
                        select_start_x,
                        cursor_y,
                        cursor_x
                    )

                    select_mode = False


#LOCATORS
            #l: line select
            elif key == keybindings['select_line']:
                save_undo_state(
                    undo_stack,
                    text,
                    cursor_x,
                    cursor_y,
                    scroll_pos_x,
                    scroll_pos_y
                )
                redo_stack.clear()
                line = text[cursor_y]

                select_mode = True
                select_start_y = cursor_y
                select_start_x = 0
                cursor_x = len(line)

            #b: block select
            elif key == keybindings['select_block']:
                save_undo_state(
                    undo_stack,
                    text,
                    cursor_x,
                    cursor_y,
                    scroll_pos_x,
                    scroll_pos_y
                )
                redo_stack.clear()
                line = text[cursor_y]

                select_mode = True

                start, end = check_for_block(text, cursor_y, comment_cha)
                select_start_y = start
                select_start_x = 0
                cursor_y = end
                cursor_x = len(text[end])


            #d: delete
            elif key == keybindings['delete']:
                save_undo_state(
                    undo_stack,
                    text,
                    cursor_x,
                    cursor_y,
                    scroll_pos_x,
                    scroll_pos_y
                )
                redo_stack.clear()

                if select_start_x == cursor_x and select_start_y == cursor_y:
                    select_mode =  False

                if select_mode:
                    cursor_y, cursor_x = delete_selection(
                        text,
                        select_start_y,
                        select_start_x,
                        cursor_y,
                        cursor_x
                    )

                    select_mode = False


                else:
                    if cursor_x > 0:
                        line = text[cursor_y]
                        tab = get_tab_level(line)
                        indent_width = len(line) - len(line.lstrip(" "))
                        spaces_to_remove = 0

                        if indent_width >= tab_size and cursor_x <= indent_width:
                            # remove one indentation level
                            text[cursor_y] = line[tab_size:]
                            cursor_x = max(0, cursor_x - tab_size)
                        else:
                            text[cursor_y] = line[:cursor_x-1] + line[cursor_x:]
                            cursor_x -= 1


                    elif cursor_y > 0: #Move back to previous line and delete
                        cursor_x = len(text[cursor_y-1])
                        text[cursor_y - 1] += text[cursor_y]
                        del text[cursor_y]
                        cursor_y -= 1
            #/: comment
            elif key == keybindings['comment']:
                if select_mode:
                    save_undo_state(
                        undo_stack,
                        text,
                        cursor_x,
                        cursor_y,
                        scroll_pos_x,
                        scroll_pos_y
                    )
                    redo_stack.clear()
                    if not select_start_y == cursor_y:
                        line = text[cursor_y]

                        if line.startswith(comment_cha):
                            for i in range(select_start_y , cursor_y + 1):
                                text[i] = text[i].lstrip(comment_cha)
                        else:
                            for i in range(select_start_y , cursor_y + 1):
                                text[i] = comment_cha + text[i]
                        select_mode = False

                    elif select_start_x == 0:
                        line = text[cursor_y]

                        if line.startswith(comment_cha):
                            for i in range(select_start_y , cursor_y + 1):
                                text[i] = text[i].lstrip(comment_cha)
                        else:
                            for i in range(select_start_y , cursor_y + 1):
                                text[i] = comment_cha + text[i]
                        select_mode = False

                    else:
                        line = text[select_start_y]
                        if line[select_start_x-1] == comment_cha:
                            text[select_start_y] = line[:select_start_x-1] + line[select_start_x:]
                            select_start_x -= 1
                            select_mode = False

                        else:
                            text[select_start_y] = line[:select_start_x] + comment_cha + line[select_start_x:]
                            select_start_x += 1
                            select_mode = False


            #w: word
            elif key == keybindings['select_word']:
                save_undo_state(
                    undo_stack,
                    text,
                    cursor_x,
                    cursor_y,
                    scroll_pos_x,
                    scroll_pos_y
                )
                redo_stack.clear()

                select_mode = True
                start, end = get_current_word(text, cursor_y, cursor_x)
                select_start_y = cursor_y
                select_start_x = start
                cursor_y = cursor_y
                cursor_x = end

            #a: All
            elif key == keybindings['select_all']:
                save_undo_state(
                    undo_stack,
                    text,
                    cursor_x,
                    cursor_y,
                    scroll_pos_x,
                    scroll_pos_y
                )
                redo_stack.clear()

                select_mode = True
                select_start_y = 0
                select_start_x = 0
                cursor_y = len(text) - 1
                cursor_x = len(text[cursor_y])

            #FIND
            elif key == keybindings['find_mode']:
                if select_mode:
                    selected = get_selected_text(
                                text,
                                select_start_y,
                                select_start_x,
                                cursor_y,
                                cursor_x
                            )
                    query = selected
                else:
                    query = ""

                find_matches = []
                find_visible_matches = []
                current_match_range = None

                select_mode = False
                mode = "find"

            #FIND PERVIOUS SERCH
            elif key == keybindings['find_mode_global']:
                find_matches = []
                find_visible_matches = []
                current_match_range = None

                select_mode = False
                mode = "find"


    #ANY MODE BUT FIND
        if mode not in ("find", "jump"):
        #BACKSPACE
            if key == curses.KEY_BACKSPACE or key == 127:
                save_undo_state(
                    undo_stack,
                    text,
                    cursor_x,
                    cursor_y,
                    scroll_pos_x,
                    scroll_pos_y
                )
                redo_stack.clear()

                if select_mode:
                    cursor_y, cursor_x = delete_selection(
                        text,
                        select_start_y,
                        select_start_x,
                        cursor_y,
                        cursor_x
                    )

                    select_mode = False


                else:
                    if cursor_x > 0:
                        line = text[cursor_y]
                        tab = get_tab_level(line)
                        indent_width = len(line) - len(line.lstrip(" "))
                        spaces_to_remove = 0

                        if indent_width >= tab_size and cursor_x <= indent_width:
                            # remove one indentation level
                            text[cursor_y] = line[tab_size:]
                            cursor_x = max(0, cursor_x - tab_size)
                        else:
                            text[cursor_y] = line[:cursor_x-1] + line[cursor_x:]
                            cursor_x -= 1


                    elif cursor_y > 0: #Move back to previous line and delete
                        cursor_x = len(text[cursor_y-1])
                        text[cursor_y - 1] += text[cursor_y]
                        del text[cursor_y]
                        cursor_y -= 1


            elif key == curses.KEY_DC: #DEL
                save_undo_state(
                    undo_stack,
                    text,
                    cursor_x,
                    cursor_y,
                    scroll_pos_x,
                    scroll_pos_y
                )
                redo_stack.clear()
                if select_mode:
                    cursor_y, cursor_x = delete_selection(
                        text,
                        select_start_y,
                        select_start_x,
                        cursor_y,
                        cursor_x
                    )

                    select_mode = False
                else:
                    if cursor_x < len(text[cursor_y]):
                        line = text[cursor_y]
                        text[cursor_y] = line[:cursor_x] + line[1+cursor_x:]

                    elif cursor_x == len(text[cursor_y]) and cursor_y < len(text) - 1:
                        text[cursor_y] += text[cursor_y + 1]
                        del text[cursor_y + 1]
            #TAB/BTAB
            elif key == 9: #TAB
                save_undo_state(
                    undo_stack,
                    text,
                    cursor_x,
                    cursor_y,
                    scroll_pos_x,
                    scroll_pos_y
                )
                redo_stack.clear()
                if select_mode:
                    indent_selection(text, select_start_y, cursor_y)
                    cursor_x += 4
                else:
                    line = text[cursor_y]
                    # Count leading spaces
                    leading_spaces = len(line) - len(line.lstrip(" "))

                    # Compute how many spaces to add to align to next multiple of 4
                    spaces_to_add = tab_size - (leading_spaces % tab_size)

                    # Add spaces at the start
                    text[cursor_y] = (" " * spaces_to_add) + line

                    # Move cursor along if you want to stay at the same relative position
                    cursor_x += spaces_to_add

            elif key == curses.KEY_BTAB:
                save_undo_state(
                    undo_stack,
                    text,
                    cursor_x,
                    cursor_y,
                    scroll_pos_x,
                    scroll_pos_y
                )
                redo_stack.clear()
                line = text[cursor_y]
                spaces_to_remove = 0

                if select_mode:
                    unindent_selection(text, select_start_y, cursor_y)
                    cursor_x -= 4


                elif line.startswith(" " * tab_size):
                    text[cursor_y] = line[tab_size:]
                    cursor_x = max(0, cursor_x - tab_size)

                elif line.startswith(" "):
                    for i in range(min(4, len(line))):
                        if line[i] == " ":
                            spaces_to_remove += 1
                        else:
                            break

                    text[cursor_y] = line[spaces_to_remove:]
                    cursor_x = max(0, cursor_x - spaces_to_remove)

            elif key == keybindings['end']:
                line = text[cursor_y]
                cursor_x = len(line)
                # Ensure cursor is visible horizontally
                if cursor_x < scroll_pos_x:
                    scroll_pos_x = cursor_x
                elif cursor_x >= scroll_pos_x + visible_width:
                    scroll_pos_x = cursor_x - visible_width + 1

            elif key == keybindings['home']:
                line = text[cursor_y]
                front_line = len(line) - len(line.lstrip())
                if cursor_x <= front_line:
                    cursor_x = 0
                else:
                    cursor_x = front_line
                # Same visibility check
                if cursor_x < scroll_pos_x:
                    scroll_pos_x = cursor_x
                elif cursor_x >= scroll_pos_x + visible_width:
                    scroll_pos_x = cursor_x - visible_width + 1


            elif key == curses.KEY_ENTER or key == 13:
                if not mode == "find":
                    save_undo_state(
                        undo_stack,
                        text,
                        cursor_x,
                        cursor_y,
                        scroll_pos_x,
                        scroll_pos_y
                    )
                    redo_stack.clear()
                    if suggestion_on == True:
                        cursor_x = apply_autocomplete(
                            mode, query, text, cursor_y, cursor_x, suggestion, prefix
                        )

                    elif cursor_x == 0:
                        # insert new line with indent + remaining text
                        text.insert(cursor_y,"")

                        # move cursor to start of new line after indent
                        cursor_y += 1
                        cursor_x = 0
                    else:

                        line = text[cursor_y]

                        # get existing indent
                        indent = line[:len(line) - len(line.lstrip(" "))]

                        # split line
                        before = line[:cursor_x]
                        after = line[cursor_x:]

                        # replace current line
                        text[cursor_y] = before

                        # insert new line with indent + remaining text
                        text.insert(cursor_y + 1, indent + after)

                        # move cursor to start of new line after indent
                        cursor_y += 1
                        cursor_x = len(indent)

                    if cursor_y < scroll_pos_y:
                        scroll_pos_y = cursor_y
                    elif cursor_y >= scroll_pos_y + visible_height:
                        scroll_pos_y = cursor_y - visible_height + 1



    #ANY MODE
        if key == 27: # ESC
            if not mode == "find":
                select_mode = False
            else:
                if query:
                    select_mode = True
                else:
                    select_mode = False
            mode = "normal"
        #LEFT
        elif key ==  keybindings['left']:
            if mode == "find":
                mode = "normal"
            if cursor_x > 0:
                cursor_x -= 1
                stored_cursor_pos_x = cursor_x

                if cursor_x < scroll_pos_x:
                    scroll_pos_x = cursor_x
                elif cursor_x >= scroll_pos_x + visible_width:
                    scroll_pos_x = cursor_x - visible_width + 1

        #RIGHT
        elif key ==  keybindings['right']:
            if mode == "find":
                mode = "normal"
            if cursor_x < line_length:
                cursor_x += 1
                stored_cursor_pos_x = cursor_x

                if cursor_x < scroll_pos_x:
                    scroll_pos_x = cursor_x
                elif cursor_x >= scroll_pos_x + visible_width:
                    scroll_pos_x = cursor_x - visible_width + 1

        #UP
        elif key ==  keybindings['up']:
            if mode == "find" and not len(suggestion_list) > 0:
                mode = "normal"
            if suggestion_on == True:
                visible_count = min(suggestions_shown, len(suggestion_list))
                if suggestion_sel > 0:
                    suggestion_sel -= 1
                else:
                    suggestion_sel = visible_count - 1
            else:
                if cursor_y > 0:
                    cursor_y -= 1
                    line_length = len(text[cursor_y])
                    cursor_x = min(stored_cursor_pos_x, line_length)

                    if cursor_y < scroll_pos_y:
                        scroll_pos_y = cursor_y
                    elif cursor_y >= scroll_pos_y + visible_height:
                        scroll_pos_y = cursor_y - visible_height + 1

        #DOWN
        elif key ==  keybindings['down']:
            if mode == "find" and not len(suggestion_list) > 0:
                mode = "normal"
            if suggestion_on == True:
                visible_count = min(suggestions_shown, len(suggestion_list))
                if suggestion_sel < visible_count - 1:
                    suggestion_sel += 1
                else:
                    suggestion_sel = 0
            else:
                if cursor_y < len(text)-1:
                    cursor_y += 1
                    line_length = len(text[cursor_y])
                    cursor_x = min(stored_cursor_pos_x, line_length)

                if cursor_y < scroll_pos_y:
                    scroll_pos_y = cursor_y
                elif cursor_y >= scroll_pos_y + visible_height:
                    scroll_pos_y = cursor_y - visible_height + 1

        # Ctrl+U → Undo
        elif key == keybindings['undo']:  # Ctrl+U
            if mode == "find":
                mode = "normal"
            text, cursor_x, cursor_y, scroll_pos_x, scroll_pos_y = perform_undo(
                undo_stack,
                redo_stack,
                text,
                cursor_x,
                cursor_y,
                scroll_pos_x,
                scroll_pos_y
            )

            status_message = "Undo"
            status_time = time.time()
            select_mode = False

        # Ctrl+r (Redo)
        elif key == keybindings['redo']:  # Ctrl+R
            if mode == "find":
                mode = "normal"
            text, cursor_x, cursor_y, scroll_pos_x, scroll_pos_y = perform_redo(
                undo_stack,
                redo_stack,
                text,
                cursor_x,
                cursor_y,
                scroll_pos_x,
                scroll_pos_y
            )

            status_message = "Redo"
            status_time = time.time()
            select_mode = False

        #CTRL + J (JUMP)
        elif key == keybindings['jump_mode_ctrl']:  # Ctrl+J
            jump_pos = ""
            mode = "jump"

        #PGUP / PGDN
        elif key == keybindings['page_up']:
            if mode == "find":
                mode = "normal"
            half = height // 2
            scroll_pos_y = max(0, scroll_pos_y - half)
            cursor_y = max(
                scroll_pos_y,
                min(cursor_y - half, scroll_pos_y + height - 1)
            )

        elif key == keybindings['page_down']:
            if mode == "find":
                mode = "normal"
            half = visible_height // 2
            cursor_y_relivive_pos = cursor_y - scroll_pos_y
            cursor_y = min(len(text) - 1, cursor_y + half)
            scroll_pos_y = cursor_y - cursor_y_relivive_pos

        # Handle terminal resize
        elif key == curses.KEY_RESIZE:
            height, width = stdscr.getmaxyx()
            visible_height = max(1, height - (top_margin * 2))
            visible_width = max(1, width - left_margin)
            cursor_y = min(cursor_y, len(text) - 1)
            if text and cursor_y < len(text):
                cursor_x = min(cursor_x, len(text[cursor_y]))
            stdscr.clear()
            continue

        #SAVE
        elif key == keybindings['save']:  # Ctrl+S
            if filename:
                    save_file(filename, text)
                    saved_text_for_check = text.copy()
                    dis_filename = format_display_filename(filename)
                    status_message = f"Saved {dis_filename}"
                    status_time = time.time()
                    mode = "normal"
                    select_mode = False

        # SAVE AS - Ctrl+A
        elif key == keybindings['save_as']:  # Ctrl+A
            # Clear status area and show save prompt
            status_message = "Save as: "
            status_time = time.time()

            # Enter a mini input mode for filename
            filename_input = filename
            mode = "save_as"  # Temporary mode

            while mode == "save_as":
                # Show the prompt
                stdscr.move(height - 2, left_margin + len("SAVE AS") + 3)
                stdscr.clrtoeol()
                stdscr.addstr(height - 2, left_margin, " SAVE AS: " + filename_input + " ",
                             curses.color_pair(5) | curses.A_REVERSE | curses.A_BOLD)
                stdscr.refresh()

                ch = stdscr.getch()

                if ch == 10 or ch == 13:  # Enter key
                    if filename_input.strip():
                        # Save to new filename
                        new_filename = filename_input.strip()
                        try:
                            save_file(new_filename, text)
                            filename = new_filename  # Update current filename
                            saved_text_for_check = text.copy()

                            # Update syntax highlighting for new file extension
                            ext = os.path.splitext(filename)[1] if filename else ""
                            rules = SYNTAX_MAP.get(ext, [])
                            highlighter = SyntaxHighlighter(rules)

                            status_message = f"Saved as {format_display_filename(filename)}"
                            status_time = time.time()
                        except Exception as e:
                            status_message = f"Save failed: {str(e)[:30]}..."
                            status_time = time.time()
                    mode = "normal"

                elif ch == 27:  # ESC - cancel
                    mode = "normal"
                    status_message = "Save cancelled"
                    status_time = time.time()

                elif ch == 127 or ch == curses.KEY_BACKSPACE:  # Backspace
                    if filename_input:
                        filename_input = filename_input[:-1]

                elif 32 <= ch <= 126:  # Printable characters
                    filename_input += chr(ch)

            select_mode = False

        #PASTE
        elif key == keybindings['paste_ctrl']:  # Ctrl+P
            if mode == "find":
                paste = paste_from_clipboard()
                query = query + paste
            elif select_mode:
                save_undo_state(
                    undo_stack,
                    text,
                    cursor_x,
                    cursor_y,
                    scroll_pos_x,
                    scroll_pos_y
                )
                redo_stack.clear()

                # Store the cursor position before deletion
                old_cursor_y = cursor_y
                old_cursor_x = cursor_x

                # Delete the selection and get new cursor position
                new_y, new_x = delete_selection(
                    text,
                    select_start_y,
                    select_start_x,
                    cursor_y,
                    cursor_x
                )

                # Set cursor to the deletion result position
                cursor_y = new_y
                cursor_x = new_x

                # Now paste at that position
                paste = paste_from_clipboard()
                cursor_y, cursor_x = insert_paste(text, cursor_y, cursor_x, paste)
                select_mode = False

            else:
                save_undo_state(
                    undo_stack,
                    text,
                    cursor_x,
                    cursor_y,
                    scroll_pos_x,
                    scroll_pos_y
                )
                redo_stack.clear()

                paste = paste_from_clipboard()
                cursor_y, cursor_x = insert_paste(text, cursor_y, cursor_x, paste)
                select_mode = False


        #YANK
        elif key == keybindings['yank_ctrl']:  # Ctrl+Y
            if mode == "find":
                mode = "normal"
            if select_mode:
                selected = get_selected_text(
                    text,
                    select_start_y,
                    select_start_x,
                    cursor_y,
                    cursor_x
                )
                copy_to_clipboard(selected)

        #CUT
        elif key == keybindings['cut_ctrl']:  # Ctrl+X
            if mode == "find":
                mode = "normal"
            if select_mode:
                save_undo_state(
                    undo_stack,
                    text,
                    cursor_x,
                    cursor_y,
                    scroll_pos_x,
                    scroll_pos_y
                )
                redo_stack.clear()

                selected = get_selected_text(
                    text,
                    select_start_y,
                    select_start_x,
                    cursor_y,
                    cursor_x
                )
                copy_to_clipboard(selected)

                cursor_y, cursor_x = delete_selection(
                    text,
                    select_start_y,
                    select_start_x,
                    cursor_y,
                    cursor_x
                )

                select_mode = False

        elif key ==  keybindings['find_ctrl']:
                if select_mode:
                    selected = get_selected_text(
                                text,
                                select_start_y,
                                select_start_x,
                                cursor_y,
                                cursor_x
                            )
                    query = selected
                else:
                    query = ""

                find_matches = []
                find_visible_matches = []
                current_match_range = None

                select_mode = False
                mode = "find"


        #SELECT
        elif key == keybindings['select_start']:  # Ctrl+Space
            if mode == "find":
                mode = "normal"
            if select_mode:
                mode = "normal"
                select_mode = False
            else:
                mode = "normal"
                select_mode = True
                select_start_y = cursor_y
                select_start_x = cursor_x

        elif key == 17:
            exit()

        #status_time = time.time()
        current_time = time.time()

        # Auto-clear after 1 second
        if current_time - last_key_time > 0.3:
            last_key = -1

        if current_time - status_time > 2:
            status_message = None

        if key != -1:
            if clear_last_key:
                last_key = -1
                last_key_time = 0
                clear_last_key = False
            else:
                last_key = key
                last_key_time = current_time

        #Was last not -1 key an arrow?
            NAV_KEYS = {
                keybindings['up'],
                keybindings['down'],
                keybindings['left'],
                keybindings['right'],
                keybindings['home'],
                keybindings['end'],
                keybindings['page_up'],
                keybindings['page_down']
            }

            if key in NAV_KEYS and not can_autocomplete(text, cursor_y, cursor_x, mode, nav_key_last, prefix):
                nav_key_last  = True
            else:
                nav_key_last = False

        # Ensure text is never empty
        if not text:
            text.append("")
            cursor_y = 0


curses.wrapper(lambda stdscr: editior(stdscr, filename))
