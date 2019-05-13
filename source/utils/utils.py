#!/usr/bin/env python3

import os
import sys
import shutil
import fnmatch
import hashlib

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

def md5_file(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

def build_break(prjpath):
    fingerprint = prjpath + "/build/fingerprint"
    os.remove(fingerprint)
    sys.exit(1)

def deps_travel(prjpath, func, arg1=None, arg2=None):
    res = True
    deps = prjpath + "/depends/"
    if os.path.isdir(deps):
        subdirs = os.listdir(deps)
        for subdir in subdirs:
            if os.path.isdir(deps + subdir):
                if arg1 == None:
                    func(deps + subdir)
                else:
                    res &= func(deps + subdir, arg1, arg2)
    return res

def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            if not os.path.exists(d):
                os.makedirs(d)
            copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)