#!/usr/bin/env python3

import os
import sys
import shutil
import hashlib
import fnmatch
import _thread
import subprocess

sys.path.append( os.path.abspath(os.path.dirname(__file__) + "/../utils"   ))
sys.path.append( os.path.abspath(os.path.dirname(__file__) + "/../export"  ))
sys.path.append( os.path.abspath(os.path.dirname(__file__) + "/../recipes" ))
from utils       import *
from export      import export
from recipes     import Recipes
from orbiprinter import OrbiPrinter as oprint


def main():
    try:
        orbibuild_project(sys.argv[1])
    except ValueError as e:
        print (e.args[0])

def __md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def __compile(prjpath, recipe):
    objdir = prjpath + "/build/obj"
    cfiles = list_ext_files(prjpath + "/code", '*.c')

    shutil.rmtree(objdir, True)
    os.makedirs(objdir)

    compile_errors = []
    def __thread_compile(_lock, prjpath, filename, recipe):
        md5 = __md5(filename)
        objfile = os.path.abspath(prjpath + "/build/obj/") + "/" + str(md5) + ".o"

        def options():
            options  = []
            options += [recipe.compiler_name]
            options += recipe.inherited_options
            options += recipe.compiler_options
            options += recipe.dependency_list
            options += recipe.include_dirs
            options += ["-c", "-Iincludes/"]
            options += ["-o", objfile, filename]
            return options
        
        proc = subprocess.Popen(options(), stderr=subprocess.PIPE)
        proc.wait()

        if proc.returncode:
            err = proc.communicate()[1]
            compile_errors.append( (filename, str(err, 'utf-8')) )

        filename = filename.replace(prjpath, "./")
        oprint.add(filename)
        _lock.release()

    locks = []
    oprint.start("Compiling")
    for file in cfiles:
        _lock = _thread.allocate_lock()
        _lock.acquire()
        _thread.start_new_thread(__thread_compile,
                                 (_lock, prjpath, file, recipe,))
        locks.append(_lock)
    for _lock in locks:
        _lock.acquire()
    oprint.print()

    if len(compile_errors):
        oprint.file = sys.stderr
        oprint.start("Errors")
        for err in compile_errors:
            oprint.add(err[1])
            if err != compile_errors[-1]:
                oprint.add_line()
        oprint.print()
        sys.exit(1)

def __linking(prjpath, recipe):
    obj = prjpath + "/build/obj"
    subbindir = "/bin/" + recipe.os + "_" + recipe.arch
    bindir = os.path.abspath(prjpath + subbindir)

    if not os.path.exists(bindir):
        os.makedirs(bindir)
    shutil.rmtree(bindir + "/*", True)

    objfiles = list_ext_files(obj, '*.o')
    options = [recipe.compiler_name] + recipe.linker_options + \
              ["-o", bindir + "/" + recipe.binfile()] + objfiles
    subprocess.call(options)

    oprint.start("Linking")
    for s in objfiles:
        oprint.add("./" + s.replace(prjpath, ""))
    oprint.add_line()
    oprint.add("." + subbindir + "/" + recipe.binfile())
    oprint.print()

def __info_recipe(recipe):
    oprint.start("Configuring project " + recipe.name())
    oprint.add("Compiler name: " + recipe.compiler_name)
    oprint.add("Compiler std : " + recipe.compiler_std)
    oprint.add("Compiler opt : " + recipe.compiler_opt_insert())
    oprint.add("Linker   opt : " + recipe.linker_opt_insert())
    oprint.print()

def __set_build_id(build_dir, id):
    with open(build_dir + "/build.uuid", "w") as file:
        file.write(id)

def __get_build_id(build_dir):
    uuid = ""
    uuid_file = build_dir + "/build.uuid"
    if os.path.isfile(uuid_file):
        with open(uuid_file, "r") as file:
            uuid = file.readline()
    return uuid

def orbibuild_project(prjpath, id):
    if not os.path.isdir(prjpath):
        raise ValueError("Incorrect path '" + prjpath + "'")
    prjpath = os.path.abspath(prjpath) + "/"

    builddir = prjpath + "/build"
    if not os.path.exists(builddir):
        os.makedirs(builddir)
    
    if __get_build_id(builddir) == id:
        return
    __set_build_id(builddir, id)

    recipes = None
    try:
        recipes = Recipes(prjpath)
    except ValueError as e:
            print (e.args[0])
            sys.exit(1)

    for recipe in recipes.list:
        __info_recipe(recipe)
        export(prjpath)
        __compile(prjpath, recipe)
        __linking(prjpath, recipe)


if __name__ == "__main__":
    main()