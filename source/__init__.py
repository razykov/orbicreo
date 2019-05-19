#!/usr/bin/env python3

import os
import sys
import argparse

sys.path.append( os.path.abspath(os.path.dirname(__file__) + "/build" ))
sys.path.append( os.path.abspath(os.path.dirname(__file__) + "/recipes" ))
sys.path.append( os.path.abspath(os.path.dirname(__file__) + "/utils" ))
sys.path.append( os.path.abspath(os.path.dirname(__file__) + "/export" ))
from utils import *
from build import orbibuild

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

def __is_orbi(path):
    code  = False
    recps = False
    for f in os.listdir(path):
        file_path = path + "/" + f
        if os.path.isdir(file_path):
            if f == "code":
                code  = True
            elif f == "recipes":
                recps = True
    return code and recps

def __try_build(prjpath, app_args):
    try:
        orbibuild(prjpath, app_args)
    except ValueError as e:
        print (e.args[0])


def main():
    if not len(sys.argv) > 1:
        print(sys.argv[0] + " <project_path>")
        exit(1)

    prjpath = sys.argv[1]
    app_args = __arguments_parse()

    if __is_orbi(prjpath):
        __try_build(prjpath, app_args)
    else:
        for f in os.listdir(prjpath):
            file_path = prjpath + "/" + f
            if __is_orbi(file_path):
                __try_build(file_path, app_args)


if __name__ == "__main__":
    main()