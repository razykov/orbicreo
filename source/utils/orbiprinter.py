#!/usr/bin/env python3

import os
import sys

class OrbiPrinter(object):
    file = sys.stdout

    def __init__(self):
        super (OrbiPrinter, self).__init__()

    @staticmethod
    def start(header):
        print("┌─── " + header, file=OrbiPrinter.file)

    @staticmethod
    def add(string):
        print("├ " + string.replace("\n", "\n├ "), file=OrbiPrinter.file)

    @staticmethod
    def add_eq(string):
        print("╞═ " + string.replace("\n", "\n├ "), file=OrbiPrinter.file)

    @staticmethod
    def add_line():
        print("├───", file=OrbiPrinter.file)

    @staticmethod
    def print():
        print("└───", file=OrbiPrinter.file)
