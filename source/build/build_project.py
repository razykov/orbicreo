#!/usr/bin/env python3

import os
import sys
import shutil
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
from version     import ProjectVersion

def main():
    try:
        orbibuild_project(sys.argv[1])
    except ValueError as e:
        print (e.args[0])

def __compile(prjpath, app_args, recipe, buildid):
    objdir = prjpath + "/build/obj/" + recipe.os + "_" + recipe.arch
    cfiles = list_ext_files(prjpath + "/code", '*.c')

    shutil.rmtree(objdir, True)
    os.makedirs(objdir)

    vers = ProjectVersion(prjpath)
    if not app_args.rebuild:
        vers.inc_version()
    vers = vers.macro_def()
    append_prefix(vers, "-D")

    compile_errors = []
    compile_warngs = []
    def __thread_compile(_lock, prjpath, filename, recipe):
        md5 = md5_file(filename)
        objfile = os.path.abspath(objdir) + "/" + str(md5) + ".o"
        
        def options():
            options  = []
            options += [recipe.compiler_name]
            options += recipe.inherited_options
            options += recipe.compiler_options
            options += recipe.dependency_list
            options += vers
            options += recipe.include_dirs
            options += ["-c", "-o", objfile, filename]
            return options
        
        proc = subprocess.Popen(options(), stderr=subprocess.PIPE)
        proc.wait()
        
        bts = proc.communicate()[1]
        outpt = str(bts)
        if proc.returncode:
            compile_errors.append( (filename, str(bts, 'utf-8')) )
        if proc.returncode or outpt.find(": warning:") != -1:
            compile_warngs.append( (filename, str(bts, 'utf-8')) )
        
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
        build_break(prjpath)

    if len(compile_warngs):
        oprint.file = sys.stderr
        oprint.start("Warnings")
        for wrn in compile_warngs:
            oprint.add(wrn[1])
            if wrn != compile_warngs[-1]:
                oprint.add_line()
        oprint.print()
        oprint.file = sys.stdout

def __linking(prjpath, recipe):
    obj = prjpath + "/build/obj/" + recipe.os + "_" + recipe.arch
    subbindir = "/bin/" + recipe.os + "_" + recipe.arch
    bindir = os.path.abspath(prjpath + subbindir)

    if not os.path.exists(bindir):
        os.makedirs(bindir)
    shutil.rmtree(bindir + "/*", True)

    objfiles = list_ext_files(obj, '*.o')
    options = [recipe.compiler_name] + recipe.linker_options + objfiles + \
               recipe.dependency_list + ["-o", bindir + "/" + recipe.binfile()]
    proc = subprocess.Popen(options, stderr=subprocess.PIPE)
    proc.wait()

    if not proc.returncode:
        oprint.start("Linking")
        for s in objfiles:
            oprint.add("./" + s.replace(prjpath, ""))
        oprint.add_line()
        oprint.add_eq("." + subbindir + "/" + recipe.binfile())
        oprint.print()
    else:
        oprint.start("Linking errors")
        oprint.add( str(proc.communicate()[1], 'utf-8') )
        oprint.print()
        build_break(prjpath)

def __copy_files(prjpath, recipe):
    if len(recipe.copy_files):
        oprint.start("Copy files")
        for cpf in recipe.copy_files:
            if os.path.isfile(cpf[0]) and os.path.isdir(cpf[1]):
                oprint.add("./" + cpf[0] + " -> " + cpf[1])
                shutil.copyfile(cpf[0], cpf[1] + "/" + cpf[0]);
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

def __copy_bins(subdir):
    prjpath = subdir.split("/depends/", 2)[0]
    copytree(subdir + "/bin", prjpath + "bin/")

def orbibuild_project(prjpath, app_args, buildid, recipes_use=None):
    if not os.path.isdir(prjpath):
        raise ValueError("Incorrect path '" + prjpath + "'")
    prjpath = os.path.abspath(prjpath) + "/"

    builddir = prjpath + "/build"
    if not os.path.exists(builddir):
        os.makedirs(builddir)
    
    if __get_build_id(builddir) == buildid:
        return
    __set_build_id(builddir, buildid)

    recipes = None
    try:
        recipes = Recipes(prjpath, recipes_use)
    except ValueError as e:
        print (e.args[0])
        build_break(prjpath)

    export(prjpath)
    for recipe in recipes.list:
        __info_recipe(recipe)
        __compile(prjpath, app_args, recipe, buildid)
        deps_travel(prjpath, __copy_bins)
        __linking(prjpath, recipe)
        __copy_files(prjpath, recipe)


if __name__ == "__main__":
    main()