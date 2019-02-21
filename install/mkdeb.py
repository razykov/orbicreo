#!/usr/bin/env python3

import os
import shutil
import subprocess

PROJECT = "orbicreo"
TMPDIR  = "/tmp/" + PROJECT + "/" + PROJECT

def main():
    crd = os.getcwd()

    if not os.path.isdir(TMPDIR):
        os.makedirs(TMPDIR)

    shutil.rmtree(TMPDIR + "/")
    shutil.copytree("./install/deb", TMPDIR)

    shutil.copytree("./source/", TMPDIR + "/usr/bin/" + PROJECT)

    os.chdir(TMPDIR + "/../")
    subprocess.run(["fakeroot", "dpkg-deb", "--build", PROJECT])
    shutil.copy(PROJECT + ".deb", crd)

if __name__ == "__main__":
    main()