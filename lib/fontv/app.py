#!/usr/bin/env python
# -*- coding: utf-8 -*-

#     font-v──────────────────────────────────────────────────────────────────┐
#     │                                                                       │
#     │ A font version string reporting and modification tool                 │
#     │                                                                       │
#     │ Copyright 2017 Christopher Simpkins                                   │
#     │ MIT License                                                           │
#     │                                                                       │
#     │ Source: https://github.com/source-foundry/font-v                      │
#     │                                                                       │
#     └───────────────────────────────────────────────────────────────────────┘

from __future__ import unicode_literals

import os
import sys

from fontTools.misc.py23 import tounicode, unicode

from fontv import settings
from fontv.commandlines import Command
from fontv.libfv import FontVersion
from fontv.utilities import file_exists, is_font


def main():
    c = Command()

    if c.does_not_validate_missing_args():
        sys.stderr.write("[font-v] ERROR: Please include a subcommand and appropriate optional arguments in "
                         "your command." + os.linesep)
        sys.exit(1)

    if c.is_help_request():
        print(settings.HELP)
        sys.exit(0)
    elif c.is_version_request():
        print(settings.VERSION)
        sys.exit(0)
    elif c.is_usage_request():
        print(settings.USAGE)
        sys.exit(0)

    if c.subcmd == "report":
        # argument test
        if c.argc < 2:
            sys.stderr.write("[font-v] ERROR: Command is missing necessary arguments. Check "
                             "`font-v --help`." + os.linesep)
            sys.exit(1)

        for arg in c.argv[1:]:
            if is_font(arg):
                font_path = arg
                if file_exists(font_path):
                    fv = FontVersion(font_path)
                    if "--dev" in c.argv:   # --dev switch report prints every version string in name records
                        for key, value in fv._nameID_5_dict.items():
                            devstring = fv.fontpath + " " + str(key) + ":" + os.linesep + fv.get_version_string()
                            print(devstring)
                    else:  # default report handling
                        print(fv.fontpath + ":" + os.linesep + fv.get_version_string())
                else:
                    sys.stderr.write("[font-v] ERROR: " + font_path + " does not appear to be a valid ttf "
                                                                      "or otf font file path." + os.linesep)
                    sys.exit(1)
    elif c.subcmd == "write":
        # argument test
        if c.argc < 2:
            sys.stderr.write("[font-v] ERROR: Command is missing necessary arguments. "
                             "Check `font-v --help`." + os.linesep)
            sys.exit(1)

        # argument parsing flags
        add_sha1 = False
        add_release_string = False
        add_dev_string = False
        add_new_version = False
        fontpath_list = []            # list of font paths that user submits on command line

        # test for mutually exclusive arguments
        # do not refactor this below the level of the argument tests that follow
        if "--rel" in c.argv and "--dev" in c.argv:
            sys.stderr.write("[font-v] ERROR: Please use either --dev or --rel argument, not both." + os.linesep)
            sys.exit(1)

        # Parse command line arguments to determine user request(s)
        for arg in c.argv[1:]:
            if arg == "--sha1":
                add_sha1 = True
            elif arg == "--rel":
                add_release_string = True
            elif arg == "--dev":
                add_dev_string = True
            elif arg[0:6] == "--ver=":
                add_new_version = True
                version_list = arg.split("=")  # split on the = symbol and use second part as definition
                if len(version_list) < 2:
                    sys.stderr.write("[font-v] ERROR: --ver=version argument does not have a valid definition"
                                     " in your command." + os.linesep)
                    sys.exit(1)
                # use fonttools library to cast terminal input from user to fontTools.misc.py23.unicode type (imported)
                # this will be Python 3 str object and Python 2 unicode object
                # try to cast to this type and catch decoding exceptions, handle with error message to user.
                try:
                    version_pre = tounicode(version_list[1], encoding='ascii')
                except UnicodeDecodeError as e:
                    sys.stderr.write("[font-v] ERROR: You appear to have entered a non ASCII character in your"
                                     "version string.  Please try again." + os.linesep)
                    sys.stderr.write("[fontTools library]: error message: " + str(e))
                    sys.exit(1)

                version_pre = version_pre.replace("-", ".")   # specified on command line as 1-000
                version_final = version_pre.replace("_", ".")   # or as 1_000
            elif len(arg) > 4 and (arg[-4:].lower() == ".ttf" or arg[-4:].lower() == ".otf"):
                if file_exists(arg):
                    fontpath_list.append(arg)
                else:
                    sys.stderr.write("[font-v] ERROR: " + arg + " does not appear to be a valid "
                                     "font file path." + os.linesep)
                    sys.exit(1)

        if add_sha1 is False and add_release_string is False and add_dev_string is False and add_new_version is False:
            print("[font-v]  No changes specified.  Nothing to do.")
            sys.exit(0)

        for fontpath in fontpath_list:
            fv = FontVersion(fontpath)

            # define a new version number substring
            if add_new_version is True:
                fv.set_version_number(version_final)

            # define new state +/- status metadata substring
            if add_sha1 is True:
                if add_dev_string is True:
                    fv.set_git_commit_sha1(development=True)
                elif add_release_string is True:
                    fv.set_git_commit_sha1(release=True)
                else:
                    fv.set_git_commit_sha1()
            else:
                # define new status metadata substring only
                if add_dev_string is True:
                    fv.set_development_status()
                elif add_release_string is True:
                    fv.set_release_status()

            fv.write_version_string()

            print("[✓] " + fontpath + " version string was successfully changed "
                  "to:" + os.linesep + fv.get_version_string() + os.linesep)
    else:  # user did not enter an acceptable subcommand
        sys.stderr.write("[font-v] ERROR: Please enter a font-v subcommand with your request." + os.linesep)
        sys.exit(1)


if __name__ == '__main__':
    main()
