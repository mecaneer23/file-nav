#!/usr/bin/env python3

import curses
import subprocess

selector = 0
def run(command):
    return subprocess.Popen(
        command.split(),
        stdout=subprocess.PIPE
    ).communicate()[0].decode()


def main(stdscr):
    exit(run("ls"))
    return stdscr.getch()


if __name__ == "__main__":
    curses.wrapper(main)

