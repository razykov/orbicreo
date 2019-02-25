#!/usr/bin/env python3

import os
import re
import sys
import shutil
import hashlib
import fnmatch

sys.path.append( os.path.abspath(os.path.dirname(__file__) + "/../utils" ))
from orbiprinter import OrbiPrinter as oprint


def main():
    export("/home/rv/work/libbixi/")
    #with open("/home/rv/work/libbixi/code/definitions/bxiexport.h") as f:
    #    text = f.read()
    #    print(_struct_detect(text))



def _dependencies(filepath, stack):
    dirpth = os.path.dirname(filepath) + "/"
    text = ""

    with open(filepath) as f:
        text = f.read()

    deps = re.findall(r"#[ ]*include[ ]*\"([ ]*.+\.h[ ]*?)\"", text);

    for dep in deps:
        deppath = os.path.abspath(dirpth + dep)
        _dependencies(deppath, stack)
        if stack.count(deppath) == 0:
            stack.append(deppath)

    if stack.count(filepath) == 0:
        stack.append(filepath)

def _headers_list(prjpath):
    stack = []
    for root, dirnames, filenames in os.walk( os.path.abspath(prjpath + "/code") ):
        for filename in fnmatch.filter(filenames, '*.h'):
            header = os.path.join(root, filename)
            _dependencies(header, stack)
    return stack

def _struct_detect(text):
    strt1  = "EXPORT"
    end2 = "EXPORT_TO"
    strti = 0
    endi = 0
    state = "find"
    result = []
    exprt = ""
    balance = 0
    balance_q = 0
    prev_c = ""
    cmnt_ml = False
    cmnt_ol = False
    curline = ""

    def _comment():
        return cmnt_ml or cmnt_ol
    def _in_macro(line):
        deps = re.findall(r"(^[ ]*#[ ]*(ifndef|define|endif))", line);
        return len(deps) != 0

    for c in text:
        if c != "\n":
            curline += c
        else:
            _in_macro(curline)
            curline = ""

        if state == "find" and c == strt1[0]:
            strti += 1
            state = "check"
        elif state == "check":
            if c != strt1[strti]:
                state = "find"
                strti = 0
            elif strti == len(strt1) - 1:
                if not _in_macro(curline):
                    state = "copy_dc"
                strti = 0
            else:
                strti += 1
        elif state == "copy_dc":
            exprt = exprt + c

            if exprt.find("_FROM") == 0:
                state = "copy_ft"
            
            if c == "/" and prev_c == "/":
                cmnt_ol = True
            elif c == "\n":
                cmnt_ol = False
            elif prev_c == "/" and c == "*":
                cmnt_ml = True
            elif prev_c == "*" and c == "/":
                cmnt_ml = False
            elif c == "{" and balance_q == 0 and not _comment():
                balance += 1
            elif c == "}" and balance_q == 0 and not _comment():
                balance -= 1
            elif c == "\"" and prev_c != "\\":
                balance_q += 1 if balance_q == 0 else -1
            elif c == ";" and balance == 0 and balance_q == 0:
                exprt = exprt.strip()
                exprt = exprt + ("" if exprt.count("\n") == 0 else "\n")
                result.append(exprt)
                exprt = ""
                state = "find"
                strti = 0
        elif state == "copy_ft":
            exprt = exprt + c

            endi = endi + 1 if c == end2[endi] else 0
            if _in_macro(curline):
                endi = 0

            if endi == len(end2):
                exprt = exprt.replace("_FROM", "", 1)
                exprt = " ".join(exprt.rsplit(end2, 1))
                #exprt = exprt.replace(end2, "", 1)
                exprt = exprt.strip()
                exprt = exprt + ("" if exprt.count("\n") == 0 else "\n")
                result.append(exprt)
                exprt = ""
                state = "find"
                strti = 0
                endi  = 0
        prev_c = c
    return result

def _exports_file_list(filename):
    exports = []
    text = ""

    with open(filename) as f:
        text = f.read()

    exports += _struct_detect(text)

    return exports

def _exports_list(prjpath):
    headers = _headers_list(prjpath)
    exports = []

    oprint.start("Exporting")
    for header in headers:
        fexports = _exports_file_list(header)
        oprint.add( "./" + header.replace(prjpath, "") )
        if len(fexports) != 0:
            exports.append("\n\n/* Exported from ." + header.replace(prjpath, "") + " */")
        exports += fexports
    oprint.print()
    return exports

def export(prjpath):
    includes = os.path.abspath(prjpath + "/includes")
    tmpdir = "/tmp/includes_" + hashlib.md5(bytes(prjpath, "ascii")).hexdigest() + "/"
    libname = re.sub( r"(.)+/", "", os.path.abspath(prjpath) )
    tmpheader = tmpdir + libname + ".h"

    if not os.path.isdir(tmpdir):
        os.mkdir(tmpdir)
    with open(tmpheader, "w") as f:
        f.write("#ifndef " + libname.upper() + "_H\n")
        f.write("#define " + libname.upper() + "_H\n")

        for str in _exports_list(prjpath):
            f.write(str)
            f.write("\n")

        f.write("\n#endif /* " + libname.upper() + "_H */\n")
    if not os.path.exists(includes):
        os.makedirs(includes)
    shutil.rmtree(includes + "/*", True)
    shutil.copyfile(tmpheader, includes + "/" + os.path.basename(tmpheader))


if __name__ == "__main__":
    main()