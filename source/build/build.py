#!/usr/bin/env python3

import os
import sys
import uuid
import shutil
import pickle
import datetime

sys.path.append( os.path.abspath(os.path.dirname(__file__)))
sys.path.append( os.path.abspath(os.path.dirname(__file__) + "/../recipes" ))
sys.path.append( os.path.abspath(os.path.dirname(__file__) + "/../utils" ))
from utils         import *
from build_project import orbibuild_project
from recipes       import recipes_names
from orbiprinter   import OrbiPrinter as oprint


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

def __deps_travel(prjpath, func, arg1=None):
    res = True
    deps = prjpath + "/depends/"
    if os.path.isdir(deps):
        subdirs = os.listdir(deps)
        for subdir in subdirs:
            if os.path.isdir(deps + subdir):
                if arg1 == None:
                    func(deps + subdir)
                else:
                    res &= func(deps + subdir, arg1)
    return res

def __files_fingerprint(prjpath, files):
    res = {}
    for file in files:
        relfile = "./" + os.path.abspath(file).replace(prjpath, "")
        relfile = relfile.replace("//", "/")
        res[relfile] = md5_file(file)
    return res

def __fingerprint_check(prjpath):
    res = False
    builddir = prjpath + "/build"
    fpfile = builddir + "/fingerprint"

    cfiles = list_ext_files(prjpath + "/code", "*.c")
    hfiles = list_ext_files(prjpath + "/code", "*.h")
    jfiles = list_ext_files(prjpath + "/recipes", "*.json")
    fingp_cur = __files_fingerprint(prjpath, cfiles + hfiles + jfiles)
    fingp_old = None

    if os.path.isfile(fpfile):
        fingp_old = pickle.load( open( fpfile, "rb" ) )

    res = fingp_cur == fingp_old
    if not os.path.isdir(builddir):
        os.makedirs(builddir)
    pickle.dump(fingp_cur, open( fpfile, "wb" ))
    return res

def __build_complete(prjpath, stime):
    prjname = os.path.basename(prjpath)
    etime = datetime.datetime.now()
    #if prjname.find("Lib") == 0:
    #    prjname = prjname[:3] + prjname[3].upper() + prjname[4:]

    delta = etime - (stime if stime != None else etime)

    oprint.start("Build complete")
    oprint.add(prjname + " build complete in " + str(delta.microseconds/ 1000) + "ms")
    oprint.print()

def orbibuild(prjpath, recipes_use=None):
    res = True
    stime = None
    buildid = str(uuid.uuid4())

    res &= __fingerprint_check(prjpath)

    if recipes_use == None:
        recipes_use = recipes_names(prjpath)

    res &= __deps_travel(prjpath, orbibuild, recipes_use)
    if not res:
        __deps_travel(prjpath, __copy_includes)
        stime = datetime.datetime.now()
        orbibuild_project(prjpath, buildid, recipes_use)
        __deps_travel(prjpath, __copy_bins)
    __build_complete(prjpath, stime)

    return res