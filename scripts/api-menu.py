#!/usr/bin/env python

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : SCRIPTS
#
#  Authors   : David Fischer
#  Contact   : david.fischer.ch@gmail.com / david.fischer@hesge.ch
#  Project   : OSCIED (OS Cloud Infrastructure for Encoding and Distribution)
#  Copyright : 2012-2013 OSCIED Team. All rights reserved.
#**************************************************************************************************#
#
# This file is part of EBU/UER OSCIED Project.
#
# This project is free software: you can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without
# even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this project.
# If not, see <http://www.gnu.org/licenses/>
#
# Retrieved from https://github.com/EBU-TI/OSCIED

from __future__ import print_function

#import glob, re, shutil, os
#from os.path import basename, dirname, join, splitext
#from common import (
#    REPORT_TOOLS_PLANTUML_BINARY, DAVID_REPORT_PATH, DAVID_REPORT_BUILD_PATH,
#    DAVID_REPORT_RELEASE_PATH, DAVID_REPORT_SOURCE_PATH, DAVID_REPORT_UML_PATH,
#    DAVID_REPORT_COMMON_FILE, DAVID_REPORT_REFERENCES_FILE, DAVID_REPORT_LINKS_FILE,
#    WIKI_BUILD_PATH, WIKI_SOURCE_PATH, xprint
#)
#from pyutils.pyutils import cmd, try_makedirs, try_remove

VALID_ACTIONS = ('deploy_transform')

if __name__ == '__main__':
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    parser = ArgumentParser(add_help=False,
        formatter_class=ArgumentDefaultsHelpFormatter,
        epilog='''TODO.''')
    parser.add_argument('--username', action='store', default=None)
    parser.add_argument('--password', action='store', default=None)
    subparsers = parser.add_subparsers(dest='arg1')
    transform_parser = subparsers.add_parser('transform', parents=[parser])
    transform_subparsers = transform_parser.add_subparsers(dest='arg2')
    transform_unit_parser = transform_subparsers.add_parser('unit')
    transform_unit_subparsers = transform_unit_parser.add_subparsers(dest='arg3')
    transform_unit_list_parser = transform_unit_subparsers.add_parser('list')
    transform_unit_list_parser.add_argument('environment', action='store')
    transform_unit_count_parser = transform_unit_subparsers.add_parser('count')
    transform_unit_count_parser.add_argument('environment', action='store')

    args = parser.parse_args()

    print(args)

    if args.arg1 == 'transform':
        if args.arg2 == 'unit':
            if args.arg3 == 'list':
                print('list env ' + args.environment)
            elif args.arg3 == 'count':
                print('count env ' + args.environment)
