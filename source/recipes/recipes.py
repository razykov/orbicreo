#!/usr/bin/env python3

import os
import re
import sys
import json

sys.path.append( os.path.abspath(os.path.dirname(__file__) + "/../utils" ))
from utils import *


class RecipeJson(object):
    __params = {
        "project_name"        : [str],
        "project_type"        : [str],
        "export_file_prefix"  : [str],
        "compiler_name"       : [str],
        "compiler_std"        : [str],
        "compiler_options"    : [list, str],
        "dependency_includes" : [list, str],
        "inherited_options"   : [list, str]
    }
    __oses = ["windows", "linux", "bsd", "minix"]
    __json_files_regexp = "(" + lst_to_str(__oses, "|") + ")_(86|64)\.json"

    def __json_verify(self, jsn):
        for key, value in jsn.items():
            if not isinstance(value, self.__params[key][0]):
                raise ValueError("Incorrect type of \"" + key + "\" field. "
                                 "Expected type " + str(self.__params[key][0]) )
            if isinstance(value, list):
                for e in value:
                    if not isinstance(e, self.__params[key][1]):
                        raise ValueError("Incorrect type of \"" + key + "\" subfield. "
                                         "Expected type " + str(self.__params[key][1]) )
    def __init__(self, filename):
        super(RecipeJson, self).__init__()
        self.filename = filename
        generalfilename = os.path.dirname(filename) + "/general.json"
        if not os.path.exists(generalfilename):
            self.gen_json = { }
        else:
            with open(generalfilename, "rb") as f:
                self.gen_json = json.loads(f.read())

        with open(filename, "r") as f:
            self.recipe_json = json.loads(f.read())

        try:
            self.__json_verify(self.gen_json)
            self.__json_verify(self.recipe_json)
        except ValueError as e:
            print (e.args[0])
            exit()

        self.json = self.gen_json.copy()
        for key, value in self.recipe_json.items():
            if isinstance(value, str):
                self.json[key] = value
            elif isinstance(value, list):
                if not key in self.json:
                    self.json[key] = []
                for s in value:
                    self.json[key].append(s)

        regs = re.findall(self.__json_files_regexp, filename)
        if regs[0][0] != "":
            self.json['os'] = regs[0][0]
        else:
            raise ValueError("Unknown os for '" + filename + "' recipe")
        if regs[0][1] != "":
            self.json['arch'] = regs[0][1]
        else:
            raise ValueError("Unknown arch for '" + filename + "' recipe")

    def read(self, key, required, defval=None):
        if key in self.json:
            return self.json[key]
        elif required:
            raise ValueError("Field \'" + key + "\' not found in " + self.filename)
        else:
            return defval

class Recipe(object):
    def __new__(self, filename):
        self = super(Recipe, self).__new__(self)

        if not os.path.exists(filename):
            return None

        self.filename = filename
        try:
            rj = RecipeJson(filename)
            self.os                  = rj.read('os',                  True)
            self.arch                = rj.read('arch',                True)
            self.project_name        = rj.read('project_name',        True)
            self.project_type        = rj.read('project_type',        True)
            self.export_file_prefix  = rj.read('export_file_prefix',  True)
            self.compiler_name       = rj.read('compiler_name',       False, "gcc")
            self.compiler_std        = rj.read('compiler_std',        False, "gnu89")
            self.compiler_options    = rj.read('compiler_options',    False, [])
            self.dependency_includes = rj.read('dependency_includes', False, [])
            self.inherited_options   = rj.read('inherited_options',   False, [])
            self.linker_options      = []
            self.binfile_prefix      = ""
            self.binfile_extenstion  = ""
        except ValueError as e:
            print (e.args[0])
            return None

        if self.project_type == "lib":
            self.linker_options.append("shared")
            self.compiler_options.append("fPIC")
            if self.os == "linux":
                self.binfile_prefix = "lib"
                self.binfile_extenstion = ".so"
            if self.os == "windows":
                self.binfile_extenstion = ".dll"

        append_prefix(self.compiler_options,  "-")
        append_prefix(self.linker_options,    "-")
        append_prefix(self.inherited_options, "-")

        return self

    def __str__(self):
        reslt = ""
        reslt = reslt + "============= " + self.name() + " =============\n"
        reslt = reslt + "        File: " +     self.filename              + "\n"
        reslt = reslt + "Project name: " +     self.project_name          + "\n"
        reslt = reslt + "Project type: " +     self.project_type          + "\n"
        reslt = reslt + "BFile prefix: " +     self.export_file_prefix    + "\n"
        reslt = reslt + "Compiler std: " +     self.compiler_std          + "\n"
        reslt = reslt + "Compiler opt: " +     self.compiler_opt_insert() + "\n"
        reslt = reslt + "  Linker opt: " +     self.linker_opt_insert()   + "\n"
        reslt = reslt + "    Includes: " + str(self.dependency_includes)  + "\n"
        reslt = reslt + "============="
        return reslt

    def name(self):
        return self.os.title() + " (x" + self.arch + ")"

    def binfile(self):
        res = ""
        res += self.binfile_prefix
        res += self.project_name
        res += self.binfile_extenstion
        return res

    def includes_insert(self):
        res = ""
        if self.dependency_includes != None:
            for inc in self.dependency_includes:
                res += "#include " + inc + "\n"
        return res

    def compiler_opt_insert(self):
        res = ""
        for opt in self.inherited_options + self.compiler_options:
            res += opt + " "
        return res
    def linker_opt_insert(self):
        res = ""
        for opt in self.linker_options:
            res += opt + " "
        return res

class Recipes(object):
    def __init__(self, prjpath):
        super(Recipes, self).__init__()
        self.list = []

        if not os.path.isdir(prjpath):
            raise ValueError(prjpath + " not found")
        if not os.path.isdir(prjpath + "/recipes"):
            raise ValueError(os.path.abspath(prjpath + "/recipes") + " not found")

        recipes_files = list_ext_files(prjpath + "/recipes", "*_*.json")
        for rfile in recipes_files:
            self.list.append(Recipe(rfile))


def main():
    recps = Recipes(sys.argv[1])

    for recp in recps.list:
        print( str(recp) )

if __name__ == "__main__":
    main()