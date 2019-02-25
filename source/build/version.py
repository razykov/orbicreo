#!/usr/bin/env python3

import os
import json


def main():
    ver = ProjectVersion("/home/razykov/work/libfenrir/")
    ver.inc_version()
    print(ver.macro_def())

class ProjectVersion(object):
    def __init__(self, prjpath):
        self.prjpath = prjpath
        self.verfile = os.path.abspath(prjpath + "/code/version.json")

    def create_version(self):
        if not os.path.isfile(self.verfile):
            ver_node = {
                "major" : 0,
                "minor" : 0,
                "build" : 0
            }
            self.set_version(ver_node)

    def set_version(self, version):
        jsn_node = {}
        jsn_node["version"] = version
        jsn_str = str(json.dumps(jsn_node, indent=4))
        with open(self.verfile, "w") as f:
            f.write(jsn_str)

    def get_version(self):
        self.create_version()
        jsn_str = ""
        with open(self.verfile, "r") as f:
            jsn_str = f.read()
        return json.loads(jsn_str)["version"]

    def inc_version(self):
        self.create_version()
        vers = self.get_version()
        vers["build"] += 1
        self.set_version(vers)

    def macro_def(self):
        opts = []
        vers = self.get_version()
        opts.append("PROJECT_VERSION_MAJOR=" + str(vers["major"]))
        opts.append("PROJECT_VERSION_MINOR=" + str(vers["minor"]))
        opts.append("PROJECT_VERSION_BUILD=" + str(vers["build"]))
        return opts


if __name__ == "__main__":
    main()