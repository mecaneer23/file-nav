#!/usr/bin/env python3

import curses
from pathlib import Path
import sys


def make_printable_sublist(height: int, lst: list, cursor: int):
    if len(lst) < height:
        return lst, cursor
    start = max(0, cursor - height // 2)
    end = min(len(lst), start + height)
    if end - start < height:
        if start == 0:
            end = min(len(lst), height)
        else:
            start = max(0, end - height)
    sublist = lst[start:end]
    cursor -= start
    return sublist, cursor


def print_items(win, items, selected):
    items, selected = make_printable_sublist(win.getmaxyx()[0] - 2, items, selected)
    for i, v in enumerate(items):
        win.addstr(
            i + 1,
            1,
            v.split("/")[-1],
            curses.A_REVERSE if i == selected else 0,
        )


def ensure_within_bounds(counter, minimum, maximum):
    if counter < minimum:
        return minimum
    elif counter > maximum - 1:
        return maximum - 1
    else:
        return counter


def explore_dir(stdscr, directory: Path):
    selected = 0
    items = [".."] + sorted([i for i in directory.iterdir()])
    assert items, directory
    maxlen = len(str(max(items, key=lambda x: len(str(x)))))
    items = [str(i).ljust(maxlen) for i in items]
    scroll = curses.newwin(
        min(stdscr.getmaxyx()[0] // 2, len(items) + 2),
        maxlen + 2,
        stdscr.getmaxyx()[0] // 10,
        (stdscr.getmaxyx()[1] - (maxlen + 1)) // 2,
    )
    stdscr.refresh()

    while True:
        scroll.box()
        stdscr.addstr(stdscr.getmaxyx()[0] // 10 - 1, (stdscr.getmaxyx()[1] - (maxlen + 1)) // 2 - (len(str(directory)) // 2), str(directory))
        print_items(scroll, items, selected)
        scroll.refresh()
        stdscr.refresh()
        try:
            key = stdscr.getch()
        except KeyboardInterrupt:  # ^C
            return
        if key in (259, 107):  # up | k
            selected -= 1
        elif key in (258, 106):  # down | j
            selected += 1
        elif key in (113, 27):  # q | esc
            return
        elif key == 10:  # enter
            path = Path(str(directory.joinpath(Path(items[selected]).name)).strip())
            if path.is_file():
                exit(path)
            return path
        else:
            continue
        selected = ensure_within_bounds(selected, 0, len(items))


def main(stdscr, directory: Path):
    curses.use_default_colors()
    curses.curs_set(0)
    while True:
        directory = explore_dir(stdscr, directory)
        if directory is None:
            return
        stdscr.clear()


if __name__ == "__main__":
    curses.wrapper(
        main,
        directory=Path(sys.argv[1]).absolute() if len(sys.argv) > 1 else Path("."),
    )
