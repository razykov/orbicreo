#!/usr/bin/env python3

import os
import sys
import uuid
import shutil

sys.path.append( os.path.abspath(os.path.dirname(__file__)))
from build_project import orbibuild_project


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)

def __copy_bins(subdir):
    prjpath = subdir.split("/depends/", 2)[0]
    copytree(subdir + "/bin", prjpath + "/bin/")

def __copy_includes(subdir):
    prjpath = subdir.split("/depends/", 2)[0]
    if not os.path.isdir(prjpath + "/includes"):
        os.makedirs(prjpath + "/includes")
    copytree(subdir + "/includes", prjpath + "/includes/")

def __deps_travel(prjpath, func):
    deps = prjpath + "/depends/"
    if os.path.isdir(deps):
        subdirs = os.listdir(deps)
        for subdir in subdirs:
            if os.path.isdir(deps + subdir):
                func(deps + subdir)

def orbibuild(prjpath):
    
    buildid = str(uuid.uuid4())

    __deps_travel(prjpath, orbibuild)    
    __deps_travel(prjpath, __copy_includes)
    orbibuild_project(prjpath, buildid)
    __deps_travel(prjpath, __copy_bins)
    print(prjpath)

