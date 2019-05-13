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


def __copy_includes(subdir):
    prjpath = subdir.split("/depends/", 2)[0]
    if not os.path.isdir(prjpath + "/includes"):
        os.makedirs(prjpath + "/includes")
    copytree(subdir + "/includes", prjpath + "/includes/")

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
    versfile = prjpath + "/code/version.json"

    cfiles = list_ext_files(prjpath + "/code", "*")
    jfiles = list_ext_files(prjpath + "/recipes", "*.json")
    if versfile in cfiles: cfiles.remove(versfile)
    fingp_cur = __files_fingerprint(prjpath, cfiles + jfiles)
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
    oprint.add(prjname + " build complete in " + str(delta.microseconds / 1000) + "ms")
    oprint.print()

def orbibuild(prjpath, app_args, recipes_use=None):
    res = True
    stime = None
    buildid = str(uuid.uuid4())

    res &= __fingerprint_check(prjpath)

    if recipes_use == None:
        recipes_use = recipes_names(prjpath)

    res &= deps_travel(prjpath, orbibuild, app_args, recipes_use)

    if (not res or app_args.force) and not app_args.clean:
        deps_travel(prjpath, __copy_includes)
        stime = datetime.datetime.now()
        orbibuild_project(prjpath, app_args, buildid, recipes_use)

    if app_args.clean:
        shutil.rmtree(prjpath + "/build", True)
        shutil.rmtree(prjpath + "/bin", True)
    else:
        __build_complete(prjpath, stime)

    return res