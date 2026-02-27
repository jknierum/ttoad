import curses
import sys
import time
import os
from datetime import datetime
import signal
import os
import subprocess
from syntax.engine import SyntaxHighlighter
from syntax import SYNTAX_MAP
import argparse

parser = argparse.ArgumentParser(
    prog="tinyt",
    description="Tinyt — a lightweight terminal text editor",
    epilog="""
    --Keybindings--
    save: ctrl + s
    quit: ctrl + q
    """,
    formatter_class=argparse.RawTextHelpFormatter
)

parser.add_argument(
    "filename",
    nargs="?",
    default=None,
    help="File to open (creates new file if it doesn't exist)"
)

args = parser.parse_args()

filename = args.filename


def load_syntax(filename):
    ext = os.path.splitext(filename)[1]
    rules = SYNTAX_MAP.get(ext, [])
    return SyntaxHighlighter(rules)

signal.signal(signal.SIGINT, signal.SIG_IGN) #ctrl + c
#signal.signal(signal.SIGTSTP, signal.SIG_IGN) #crtl + z

os.system("stty -ixon")

filename = args.filename

def open_file(filename):
    text = []
    try:
        with open(filename, "r") as f:
            for line in f:
                text.append(line.rstrip("\n"))  # remove newline
    except FileNotFoundError:
        text = [""]  # start with empty text if file doesn’t exist
    return text

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
    line = text[cursor_y]

    if not line:
        return ""

    # If cursor is at end of line, step back one
    if cursor_x == len(line) and cursor_x > 0:
        cursor_x -= 1

    # If not on a word character, return empty
    if not (line[cursor_x].isalnum() or line[cursor_x] == "_"):
        return ""

    # Find word start
    start = cursor_x
    while start > 0 and (line[start - 1].isalnum() or line[start - 1] == "_"):
        start -= 1

    # Find word end
    end = cursor_x
    while end < len(line) and (line[end].isalnum() or line[end] == "_"):
        end += 1

    return line[start:end]

def get_current_prefix(text, cursor_y, cursor_x):
    line = text[cursor_y]

    if not line or cursor_x == 0:
        return ""

    i = cursor_x - 1

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
    return sorted([w for w in words if w.startswith(prefix) and w != prefix])

def apply_autocomplete(text, cursor_y, cursor_x, suggestion, prefix):
    line = text[cursor_y]
    remainder = suggestion[len(prefix):]

    text[cursor_y] = (
        line[:cursor_x] + remainder + line[cursor_x:]
    )

    return cursor_x + len(remainder)

def can_autocomplete(text, cursor_y, cursor_x, mode, key, prefix = ""):
    line = text[cursor_y]
    if not mode == "insert":
        return False

    if not prefix:
        return False
    # Case 1: Cursor at end of line
    if cursor_x == len(line):
        return True

    # Case 2: Character after cursor is space
    if line[cursor_x] == " ":
        return True

    if line[cursor_x] in "(){}[]":
        return True

    return False

def get_indent_level(line):
    #"""Return number of leading spaces"""
    count = 0
    for char in line:
        if char == " ":
            count += 1
        else:
            break
    return count

def check_for_block(text, cursor_y):
    if not text:
        return cursor_y, cursor_y

    target_indent = get_indent_level(text[cursor_y])

    start = cursor_y
    end = cursor_y

    # Check upward
    y = cursor_y - 1
    while y >= 0:
        if get_indent_level(text[y]) >= target_indent:
            start = y
            y -= 1
        else:
            break

    # Check downward
    y = cursor_y + 1
    while y < len(text):
        if get_indent_level(text[y]) >= target_indent:
            end = y
            y += 1
        else:
            break

    return start, end

def save_undo_state(undo_stack, text, cursor_x, cursor_y):
    undo_stack.append((
        text.copy(),
        cursor_x,
        cursor_y
    ))

    # Limit history size (optional, prevents memory explosion)
    if len(undo_stack) > 500:
        undo_stack.pop(0)


def perform_undo(undo_stack, redo_stack, text, cursor_x, cursor_y):
    if not undo_stack:
        return text, cursor_x, cursor_y

    redo_stack.append((text.copy(), cursor_x, cursor_y))

    prev_text, prev_x, prev_y = undo_stack.pop()

    return prev_text.copy(), prev_x, prev_y


def perform_redo(undo_stack, redo_stack, text, cursor_x, cursor_y):
    if not redo_stack:
        return text, cursor_x, cursor_y

    undo_stack.append((text.copy(), cursor_x, cursor_y))

    next_text, next_x, next_y = redo_stack.pop()

    return next_text.copy(), next_x, next_y

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
    lines = paste_string.split('\n')

    before = text[cursor_y][:cursor_x]
    after = text[cursor_y][cursor_x:]

    text[cursor_y] = before + lines[0]

    for i in range(1, len(lines)):
        cursor_y += 1
        text.insert(cursor_y, lines[i])

    text[cursor_y] += after

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

def editior(stdscr, filename):
    stdscr.timeout(50)  # refresh every 50ms
    curses.set_escdelay(1)
    status_message = ""
    status_time = 0
    curses.curs_set(1)

    curses.start_color()  # Enable color mode
    curses.use_default_colors()  # Optional: let terminal default background show

    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_BLUE, curses.COLOR_BLACK)   # keywords
    curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)  # comments
    curses.init_pair(4, curses.COLOR_RED, curses.COLOR_BLACK)   # constants
    curses.init_pair(5, curses.COLOR_YELLOW, curses.COLOR_BLACK) # strings
    curses.init_pair(6, curses.COLOR_MAGENTA, curses.COLOR_BLACK)# love2d
    stdscr.clear()

    if filename:
        text = open_file(filename)
    else:
        text = [""]

    # Create syntax highlighter
    ext = os.path.splitext(filename)[1] if filename else ""
    rules = SYNTAX_MAP.get(ext, [])
    highlighter = SyntaxHighlighter(rules)

    cursor_y = 0
    cursor_x =0
    tab_size = 4
    left_margin = 6
    top_margin = 3
    mode = "find" #"normal"
    yanked = ""
    last_key = -1
    last_key_time = 0
    clear_last_key = False
    stored_cursor_pos_x = 0
    store_prefix = ""
    suggestion_sel = 0
    suggestions_shown = 5
    suggestion_on = False
    comment_cha = "#"
    find_string = ""

    scroll_pos_y = 0
    scroll_pos_x = 0
    undo_stack = []
    redo_stack = []
    tm_colour = 1
    saved_text_for_check = text.copy()

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
        line_length = len(text[cursor_y])
        height, width = stdscr.getmaxyx()
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
        else:
            stdscr.addstr(1, left_margin, " " + dis_filename + " ", curses.color_pair(tm_colour) | curses.A_BOLD | curses.A_REVERSE)

        #TIME

        y = 1
        x = width - left_margin - len(str(current_time))

        x = max(0, x)

        stdscr.addstr(
            y,
            x,
            current_time[:width - x - 1],
            curses.color_pair(1)
        )

        # Draw text
        height, width = stdscr.getmaxyx()
        visible_height = height - (top_margin * 2)  # number of lines we can display
        visible_width = width - (left_margin)

        for i, line in enumerate(text[scroll_pos_y:scroll_pos_y + visible_height]):
            if i >= height - (top_margin * 2):
                break  # don't draw past bottom of screen

        # Draw the line
            visible_line = line[scroll_pos_x:scroll_pos_x + visible_width]
            highlighter.highlight_line(stdscr, i + top_margin, left_margin, visible_line)

        # Draw line numbers
            line_count = str(i + 1)
            ln_x = 4 #max(0, (left_margin - len(line_count)) - 1)
            line_num_width = 4

            num_style = "normal"
            if num_style == "normal":
                if i == screen_y:
                    stdscr.addstr(i + top_margin, 0, str(int(line_count) + scroll_pos_y).rjust(line_num_width +1), curses.color_pair(5) | curses.A_REVERSE | curses.A_BOLD)
                else:
                    stdscr.addstr(i + top_margin, 0, str(int(line_count) + scroll_pos_y).rjust(line_num_width), curses.color_pair(1))

            elif num_style == "vim":
                if i == screen_y:
                    stdscr.addstr(i + top_margin, 0, str(int(line_count) + scroll_pos_y).rjust(line_num_width +1), curses.color_pair(5) | curses.A_REVERSE | curses.A_BOLD)
                elif i > screen_y:
                    stdscr.addstr(i + top_margin, 0, str(int(line_count) + scroll_pos_y - cursor_y - 1).rjust(line_num_width), curses.color_pair(1))
                elif i < screen_y:
                    stdscr.addstr(i + top_margin, 0, str(-(int(line_count) + scroll_pos_y - cursor_y - 1)).rjust(line_num_width), curses.color_pair(1))




        mode_dis = mode.upper()
        stdscr.addstr(height - 2, left_margin, " " + mode_dis + " ", curses.color_pair(5) | curses.A_REVERSE | curses.A_BOLD)


        #FIND
        if mode == "find":
            ####WORKING
        #yanked
        if yanked:
            y = height - 2
            x = width - len(yanked) - 1

            x = max(0, x)

            stdscr.addstr(
                y,
                x,
                yanked[:width - x - 1],
                curses.color_pair(1)
            )
#        if last_key:
#           stdscr.addstr(height - 2, width - left_margin, str(last_key), curses.color_pair(1))

        #Auto complete
        prefix = get_current_prefix(text, cursor_y, cursor_x)
        store_prefix = prefix
        words = collect_words(text)
        suggestion_list = get_autocomplete_list(prefix, words)


        if suggestion_list:
            suggestion_sel = max(0, min(suggestion_sel, len(suggestion_list) - 1))
        else:
            suggestion_sel = 0

        if prefix and can_autocomplete(text, cursor_y, cursor_x, mode, key, prefix) and mode == "insert":
            if suggestion_list:
                suggestion = suggestion_list[suggestion_sel]

        if prefix and can_autocomplete(text, cursor_y, cursor_x, mode, key, prefix) and mode == "insert":
            if suggestion_list:
                suggestion = suggestion_list[suggestion_sel]
                suggestion_on = True
                for i in range(min(suggestions_shown, len(suggestion_list))):
                    if i == suggestion_sel:
                        stdscr.addstr(screen_y + top_margin + i + 1, (cursor_x - scroll_pos_x) + left_margin - len(prefix), suggestion_list[i], curses.color_pair(5) | curses.A_REVERSE)
                    else:
                        stdscr.addstr(screen_y + top_margin + i + 1, (cursor_x - scroll_pos_x) + left_margin - len(prefix), suggestion_list[i], curses.color_pair(1) | curses.A_REVERSE)

                    stdscr.addstr(screen_y + top_margin, (cursor_x - scroll_pos_x) + left_margin, suggestion_list[suggestion_sel][len(prefix):], curses.color_pair(1))
            else:
                suggestion_on = False
                suggestion_sel = 0
                suggestion = None

        # Clip cursor so it stays inside screen
        cursor_y = max(0, min(cursor_y, len(text) - 1))
        cursor_x = max(0, min(cursor_x, width - (left_margin * 2) - 1))

        # Clamp screen_y to visible area
        screen_y = cursor_y - scroll_pos_y
        screen_y = max(0, min(screen_y, visible_height - 1))
        screen_x = cursor_x - scroll_pos_x
        screen_x = max(0, min(screen_x, visible_width - 1))

        stdscr.move(screen_y + top_margin, screen_x + left_margin)


        stdscr.refresh()

        key = stdscr.getch()

    # INSERT MODE
        if mode == "insert":
            if 32 <= key <= 126:
                save_undo_state(undo_stack, text, cursor_x, cursor_y)
                redo_stack.clear()
                line = text[cursor_y]
                text[cursor_y] = line[:cursor_x] + chr(key) + line[cursor_x:]
                cursor_x += 1
    # FIND MODE
        elif mode == "find":
           if 32 <= key <= 126:
                find_string = find_string + chr(key)
    # NORMAL MODE
        elif mode == "normal":
            #ESC
            if key == 31 or key == 105:
                mode = "insert"
            #y,Y
            elif key == 121: #y: yank word
                yanked = get_current_word(text, cursor_y, cursor_x)
                copy_to_clipboard(yanked)
#                status_message = "Copied to clipboard"

            elif key == 89: #Y: Yank line
                yanked = text[cursor_y]
                copy_to_clipboard(yanked)
#                status_message = "Copied to clipboard"
            #p,P
            elif key == 112: #p: paste at cursor
                save_undo_state(undo_stack, text, cursor_x, cursor_y)
                redo_stack.clear()

                paste = paste_from_clipboard()
                cursor_y, cursor_x = insert_paste(text, cursor_y, cursor_x, paste)
            elif key == 80: #P: Paste whole line
                save_undo_state(undo_stack, text, cursor_x, cursor_y)
                redo_stack.clear()
                text[cursor_y] = ""
                paste = paste_from_clipboard()
                cursor_y, cursor_x = insert_paste(text, cursor_y, cursor_x, paste)

            #l: line
            elif key == 108:
                save_undo_state(undo_stack, text, cursor_x, cursor_y)
                redo_stack.clear()
                line = text[cursor_y]
                if last_key == 100: #d
                    del text[cursor_y]
                elif last_key == 47:
                    if line:
                        if not line[0] == comment_cha:
                            text[cursor_y] = comment_cha + line
                        else:
                           text[cursor_y] = text[cursor_y].lstrip(comment_cha)
                    else:
                        text[cursor_y] = comment_cha + line


            #b: block
            elif key == 98:
                save_undo_state(undo_stack, text, cursor_x, cursor_y)
                redo_stack.clear()
                line = text[cursor_y]
                if last_key == 100: #db: delete block
                    start, end = check_for_block(text, cursor_y)
                    del text[start:end+1]
                    cursor_y = start
                    cursor_x = 0
                if last_key == 47: #/l: comment block
                    if line[0] == comment_cha:
                        start, end = check_for_block(text, cursor_y)
                        for i in range(start, end + 1):
                            text[i] = text[i].lstrip(comment_cha)
                    else:
                        start, end = check_for_block(text, cursor_y)
                        for i in range(start, end + 1):
                            text[i] = comment_cha + text[i]

            #w: word
            elif key == 119:
                save_undo_state(undo_stack, text, cursor_x, cursor_y)
                redo_stack.clear()
                if last_key == 100: #dw: delete word
                    cursor_x = delete_current_word(text, cursor_y, cursor_x)
                    clear_last_key = True
            #s (select): word,line,block
            #elif key ==

    # ANY MODE
        if key == 27: # ESC
            mode = "normal"

        elif key == curses.KEY_BACKSPACE or key == 127:
            save_undo_state(undo_stack, text, cursor_x, cursor_y)
            redo_stack.clear()
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
                text[cursor_y - 1] += text[cursor_y]
                del text[cursor_y]
                cursor_y -= 1
                cursor_x = len(text[cursor_y])

        elif key == curses.KEY_DC: #DEL
            save_undo_state(undo_stack, text, cursor_x, cursor_y)
            redo_stack.clear()
            if cursor_x < len(text[cursor_y]):
                line = text[cursor_y]
                text[cursor_y] = line[:cursor_x] + line[1+cursor_x:]

            elif cursor_x == len(text[cursor_y]) and cursor_y < len(text) - 1:
                text[cursor_y] += text[cursor_y + 1]
                del text[cursor_y + 1]

        elif key == 9: #TAB
            save_undo_state(undo_stack, text, cursor_x, cursor_y)
            redo_stack.clear()
            if suggestion_on == True:
                cursor_x = apply_autocomplete(
                    text, cursor_y, cursor_x, suggestion, prefix
                )
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
            save_undo_state(undo_stack, text, cursor_x, cursor_y)
            redo_stack.clear()
            line = text[cursor_y]
            spaces_to_remove = 0

            if line.startswith(" " * tab_size):
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

        elif key == curses.KEY_END:
            line = text[cursor_y]
            cursor_x = len(line)

        elif key == curses.KEY_HOME:
            cursor_x = 0

        elif key == curses.KEY_ENTER or key == 10:
            save_undo_state(undo_stack, text, cursor_x, cursor_y)
            redo_stack.clear()
            if cursor_x == 0:
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


        elif key == curses.KEY_LEFT:
            if cursor_x > 0:
                cursor_x -= 1
                stored_cursor_pos_x = cursor_x

                if cursor_x < scroll_pos_x:
                    scroll_pos_x = cursor_x
                elif cursor_x >= scroll_pos_x + visible_width:
                    scroll_pos_x = cursor_x - visible_width + 1
        elif key == curses.KEY_RIGHT:
            if cursor_x < line_length:
                cursor_x += 1
                stored_cursor_pos_x = cursor_x

                if cursor_x < scroll_pos_x:
                    scroll_pos_x = cursor_x
                elif cursor_x >= scroll_pos_x + visible_width:
                    scroll_pos_x = cursor_x - visible_width + 1
        elif key == curses.KEY_UP:
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

        elif key == curses.KEY_DOWN:
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
        elif key == 21:
            text, cursor_x, cursor_y = perform_undo(
                undo_stack,
                redo_stack,
                text,
                cursor_x,
                cursor_y
            )
            status_message = "Undo"
            status_time = time.time()

        # Ctrl+Y → Redo
        elif key == 25:
            text, cursor_x, cursor_y = perform_redo(
                undo_stack,
                redo_stack,
                text,
                cursor_x,
                cursor_y
            )
            status_message = "Redo"
            status_time = time.time()

        elif key == 339: #pg up
            if cursor_y == scroll_pos_y:
                cursor_y = max(0, cursor_y - height)
                scroll_pos_y = cursor_y
            else:
                cursor_y = scroll_pos_y
        elif key == 338: #pgdn
            vh = visible_height - 1
            cursor_y = min(len(text) - 1, cursor_y + vh)

            if cursor_y >= scroll_pos_y + vh:
                scroll_pos_y = cursor_y - vh

            scroll_pos_y = max(0, min(scroll_pos_y, len(text) - vh))

        #SAVE
        elif key == 19: #ctrl + s
            if filename:
                    save_file(filename, text)
                    saved_text_for_check = text.copy()
                    dis_filename = format_display_filename(filename)
                    status_message = f"Saved {dis_filename}"
                    status_time = time.time()
                    mode = "normal"
        #PASTE
        elif key == 16: # Ctrl+P example
                save_undo_state(undo_stack, text, cursor_x, cursor_y)
                redo_stack.clear()

                paste = paste_from_clipboard()
                cursor_y, cursor_x = insert_paste(text, cursor_y, cursor_x, paste)

        #QUIT
        elif key == 17: #ctrl + q
            break


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

        # Ensure text is never empty
        if not text:
            text.append("")
            cursor_y = 0

        #status_message = str(last_key) #f"Key: {key}"


curses.wrapper(lambda stdscr: editior(stdscr, filename))
