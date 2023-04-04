#!/usr/bin/env python3

import curses
import subprocess
import os
import sys


def run(command: list):
    return (
        subprocess.Popen(
            safe_split(command), stdout=subprocess.PIPE
        )  # , stderr=open("error.txt", 'w'))
        .communicate()[0]
        .decode()
        .split("\n")[:-1]
    )


def safe_split(lst, sep=" "):
    output = []
    temp = ""
    i = 0
    while i < len(lst):
        if lst[i] == "\\":
            temp += " "
            i += 2
            continue
        if lst[i] == sep:
            output.append(temp)
            temp = ""
            i += 1
            continue
        temp += lst[i]
        i += 1
    output.append(temp)
    return output


def print_items(win, items, selected, maxlen):
    selected = len(items) - selected - 1
    for i in range(9):
        win.addstr(i + 1, 2, " " * maxlen)
    for i, v in enumerate(items[::-1]):
        if i < selected + 5 and i > selected - 5:
            win.addstr(
                selected + 5 - i,
                2,
                v,
                curses.A_REVERSE if i == selected else 0,
            )
    win.refresh()


def ensure_within_bounds(counter, minimum, maximum):
    if counter < minimum:
        return minimum
    elif counter > maximum - 1:
        return maximum - 1
    else:
        return counter


def explore_dir(stdscr, directory):
    selected = 0
    items = run(f"ls -a {directory}")
    assert items, repr(directory)
    maxlen = len(max(items, key=len))
    items = [i.ljust(maxlen) for i in items]
    scroll = curses.newwin(
        11,
        maxlen + 4,
        stdscr.getmaxyx()[0] // 10,
        (stdscr.getmaxyx()[1] - (maxlen + 1)) // 2,
    )
    stdscr.refresh()

    while True:
        scroll.box()
        print_items(scroll, items, selected, maxlen)
        scroll.refresh()
        stdscr.refresh()
        try:
            key = stdscr.getch()  # python3 -c "print(ord('x'))"
        except KeyboardInterrupt:  # exit on ^C
            return
        if key in (259, 107):  # up | k
            selected -= 1
        elif key in (258, 106):  # down | j
            selected += 1
        elif key in (113, 27):  # q | esc
            return
        elif key == 10:  # enter
            path = f"{directory}/{items[selected]}".strip()
            if not os.path.isdir(path.replace("\\", "")):
                exit(repr(path))
            return path
        else:
            continue
        selected = ensure_within_bounds(selected, 0, len(items))


def replace_backslash(string):
    output = ""
    i = 0
    while i < len(string):
        if string[i] == " " and string[i - 1] != "\\":
            output += "\\ "
            i += 1
            continue
        output += string[i]
        i += 1
    return output


def main(stdscr, directory: str):
    curses.use_default_colors()
    curses.curs_set(0)
    while True:
        directory = replace_backslash(
            explore_dir(stdscr, directory.rstrip("/").replace("/./", "/"))
        )
        if directory is None:
            return
        stdscr.clear()


if __name__ == "__main__":
    curses.wrapper(
        main,
        directory=(replace_backslash(sys.argv[1])
        if len(sys.argv[1]) > 1
        else f"/usr/../{sys.argv[1]}")
        if len(sys.argv) > 1
        else os.getcwd().replace(" ", "\ "),
    )
