#!/usr/bin/env python3

import os
import sys
import argparse

from build.build import orbibuild

def __arguments_parse():
    sys.argv[0] = "orbicreo"
    del(sys.argv[1])

    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--clean", action="store_true", 
                        help="clean project")
    parser.add_argument("-f", "--force", action="store_true", 
                        help="force rebuild project and all subprojects")
    parser.add_argument("-r", "--rebuild", action="store_true", 
                        help="build project without change number of build")
    parser_args = parser.parse_args()

    return parser_args

def main():
    if not len(sys.argv) > 1:
        print(sys.argv[0] + " <project_path>")
        exit(1)

    prjpath = sys.argv[1]
    app_args = __arguments_parse()

    try:
        orbibuild(prjpath, app_args)
    except ValueError as e:
        print (e.args[0])

if __name__ == "__main__":
    main()