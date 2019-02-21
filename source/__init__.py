#!/usr/bin/env python3

import os
import sys

from build.build import orbibuild

def main():
    if not len(sys.argv) > 1:
        print("<programm> <project_path>")
        exit(1)

    try:
        orbibuild(sys.argv[1])
    except ValueError as e:
        print (e.args[0])

if __name__ == "__main__":
    main()