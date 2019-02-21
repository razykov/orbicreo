#!/usr/bin/env python3

import os
import fnmatch

def list_ext_files(path, ext):
    res = []
    for root, dirnames, filenames in os.walk(path):
        for filename in fnmatch.filter(filenames, ext):
            res.append(os.path.abspath(os.path.join(root, filename)))
    return res

def lst_to_str(lst, declm=" "):
    res = ""
    for elem in lst:
        res += elem + declm
    res = res[0:-len(declm)]
    return res

def append_prefix(lst, prefx):
    lst[:] = [prefx + x for x in lst]