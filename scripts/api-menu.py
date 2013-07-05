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

import requests
from pyutils.pyutils import object2json
#import glob, re, shutil, os
#from os.path import basename, dirname, join, splitext
#from common import (
#    REPORT_TOOLS_PLANTUML_BINARY, DAVID_REPORT_PATH, DAVID_REPORT_BUILD_PATH,
#    DAVID_REPORT_RELEASE_PATH, DAVID_REPORT_SOURCE_PATH, DAVID_REPORT_UML_PATH,
#    DAVID_REPORT_COMMON_FILE, DAVID_REPORT_REFERENCES_FILE, DAVID_REPORT_LINKS_FILE,
#    WIKI_BUILD_PATH, WIKI_SOURCE_PATH, xprint
#)
#from pyutils.pyutils import cmd, try_makedirs, try_remove

def api_method(args):
    arg3 = '/%s' % args.arg3 if args.arg3 != 'list' else ''
    env = '/environment/%s' % args.environment if hasattr(args, 'environment') else ''
    num_units = '/%s' % args.num_units if hasattr(args, 'num_units') else ''
    return 'http://%s:%s/%s/%s%s%s%s' % (args.host, args.port, args.arg1, args.arg2, env, arg3, num_units)

if __name__ == '__main__':
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    api = ArgumentParser(add_help=False)
    api.add_argument('--host',     action='store', default=None, required=True)
    api.add_argument('--port',     action='store', default=5000)
    api.add_argument('--username', action='store', default=None)
    api.add_argument('--password', action='store', default=None)
    environment = ArgumentParser(add_help=False)
    environment.add_argument('environment', action='store')

    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter, epilog='''TODO.''')
    subparsers = parser.add_subparsers(dest='arg1')
    transform_parser = subparsers.add_parser('transform')
    transform_subparsers = transform_parser.add_subparsers(dest='arg2')
    transform_unit_parser = transform_subparsers.add_parser('unit')
    transform_unit_subparsers = transform_unit_parser.add_subparsers(dest='arg3')
    transform_unit_list_parser = transform_unit_subparsers.add_parser('list', parents=[api, environment])
    transform_unit_count_parser = transform_unit_subparsers.add_parser('count', parents=[api, environment])
    transform_unit_deploy_parser = transform_unit_subparsers.add_parser('deploy', parents=[api, environment])
    transform_unit_deploy_parser.add_argument('num_units', action='store', default=None)

    args = parser.parse_args()
    username = args.username or 'anonymous'
    auth = (args.username, args.password) if args.username and args.password else None
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

    print(api_method(args))

    if args.arg1 == 'transform':
        if args.arg2 == 'unit':
            if args.arg3 == 'list':
                print('Listing transform units of environment %s as %s ...' % (args.environment, username))
                r = requests.get(api_method(args), auth=auth)
                print(r.json())
            elif args.arg3 == 'count':
                print('Counting transform units of environment %s as %s ...' % (args.environment, username))
                r = requests.get(api_method(args), auth=auth)
                print(r.json())
            elif args.arg3 == 'deploy':
                print('Deploy %s transform units into environment %s as %s ...' % (args.num_units, args.environment, username))
                r = requests.post(api_method(args), data=object2json({'salut': 1}, False), auth=auth, headers=headers)
                print(r)
                print(r.json())
