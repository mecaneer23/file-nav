#!/usr/bin/env python3

import curses
import subprocess
import os


def run(command: list):
    if command.split()[0] == "cd":
        return os.chdir(command.split()[1])
    return (
        subprocess.Popen(command.split(), stdout=subprocess.PIPE)
        .communicate()[0]
        .decode()
        .split("\n")[:-1]
    )


def print_items(win, items, selected):
    selected = len(items) - selected - 1
    for i, v in enumerate(items[::-1]):
        if i < selected + 5 and i > selected - 5:
            win.addstr(
                selected + 5 - i,
                1,
                v,
                curses.A_REVERSE if i == selected else 0,
            )


def ensure_within_bounds(counter, minimum, maximum):
    if counter < minimum:
        return minimum
    elif counter > maximum - 1:
        return maximum - 1
    else:
        return counter


def main(stdscr):
    curses.use_default_colors()
    curses.curs_set(0)
    selected = 0
    items = run("ls")
    maxlen = len(max(items, key=len))
    scroll = curses.newwin(
        11,
        maxlen + 2,
        stdscr.getmaxyx()[0] // 10,
        (stdscr.getmaxyx()[1] - (maxlen + 1)) // 2,
    )

    while True:
        scroll.box()
        print_items(scroll, items, selected)
        scroll.refresh()
        stdscr.refresh()
        try:
            key = stdscr.getch()  # python3 -c "print(ord('x'))"
        except KeyboardInterrupt:  # exit on ^C
            return
        if key in (259, 107):  # up | k
            selected += 1
            scroll.clear()
        elif key in (258, 106):  # down | j
            selected -= 1
            scroll.clear()
        elif key in (113, 27):  # q | esc
            return
        elif key == 10:  # enter
            return run(f"cd {items[selected]}")
        else:
            continue
        selected = ensure_within_bounds(selected, 0, len(items))


if __name__ == "__main__":
    print(curses.wrapper(main))
