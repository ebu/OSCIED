#!/usr/bin/env python

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : SCRIPTS
#
#  Authors   : David Fischer
#  Contact   : david.fischer.ch@gmail.com
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
# Retrieved from https://github.com/ebu/OSCIED

from __future__ import print_function

import requests
from pprint import pprint
from pyutils.pyutils import object2json


def api_method(args, schema):
    method = 'http://%s:%s/' % (args.host, args.port) + schema.format(**args.__dict__)
    print(method)
    return method

if __name__ == '__main__':
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

    api_args = ArgumentParser(add_help=False)
    api_args.add_argument('--host',     action='store', default=None, required=True)
    api_args.add_argument('--port',     action='store', default=5000)
    api_args.add_argument('--username', action='store', default=None)
    api_args.add_argument('--password', action='store', default=None)
    environment_args = ArgumentParser(add_help=False)
    environment_args.add_argument('environment', action='store')
    #num_units = ArgumentParser(add_help=False)
    #num_units.add_argument('num_units', action='store')

    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter, epilog='''TODO.''')
    subparsers = parser.add_subparsers(dest='arg1')

    environment = subparsers.add_parser('environment')
    environment_sub = environment.add_subparsers(dest='arg2')
    environment_list = environment_sub.add_parser('list', parents=[api_args])
    environment_add = environment_sub.add_parser('add', parents=[api_args])
    environment_add.add_argument('name', action='store')
    environment_add.add_argument('type', action='store')
    environment_add.add_argument('region', action='store')
    environment_add.add_argument('access_key', action='store')
    environment_add.add_argument('secret_key', action='store')
    environment_add.add_argument('control_bucket', action='store')
    environment_remove = environment_sub.add_parser('remove', parents=[api_args])
    environment_remove.add_argument('name', action='store')

    transform = subparsers.add_parser('transform')
    transform_sub = transform.add_subparsers(dest='arg2')
    transform_unit = transform_sub.add_parser('unit')
    transform_unit_sub = transform_unit.add_subparsers(dest='arg3')
    transform_unit_list = transform_unit_sub.add_parser('list', parents=[api_args, environment_args])
    transform_unit_count = transform_unit_sub.add_parser('count', parents=[api_args, environment_args])
    transform_unit_deploy = transform_unit_sub.add_parser('deploy', parents=[api_args, environment_args])
    transform_unit_deploy.add_argument('num_units', action='store')
    transform_unit_remove = transform_unit_sub.add_parser('remove', parents=[api_args, environment_args])
    transform_unit_remove.add_argument('num_units', action='store')

    args = parser.parse_args()
    username = args.username or 'anonymous'
    auth = (args.username, args.password) if args.username and args.password else None
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}

    if args.arg1 == 'environment':
        if args.arg2 == 'count':
            print('Counting environments as %s ...' % username)
            r = requests.get(api_method(args, '{arg1}/{arg2}'), auth=auth)
            pprint(r.json())
        elif args.arg2 == 'list':
            print('Listing environments as %s ...' % username)
            r = requests.get(api_method(args, '{arg1}'), auth=auth)
            pprint(r.json())
        elif args.arg2 == 'add':
            print('Adding a new environment %s as %s ...' % (args.name, username))
            data = object2json(args, False)
            r = requests.post(api_method(args, '{arg1}'), data=data, auth=auth, headers=headers)
            pprint(r.json())
        elif args.arg2 == 'remove':
            print('Removing environment %s as %s ...' % (args.name, username))
            r = requests.delete(api_method(args, '{arg1}/name/{name}'), auth=auth)
            pprint(r.json())
    elif args.arg1 == 'transform':
        if args.arg2 == 'unit':
            if args.arg3 == 'count':
                print('Counting transform units of environment %s as %s ...' % (args.environment, username))
                r = requests.get(api_method(args, '{arg1}/{arg2}/environment/{environment}/{arg3}'), auth=auth)
                pprint(r.json())
            elif args.arg3 == 'list':
                print('Listing transform units of environment %s as %s ...' % (args.environment, username))
                r = requests.get(api_method(args, '{arg1}/{arg2}/environment/{environment}'), auth=auth)
                pprint(r.json())
            elif args.arg3 == 'deploy':
                print('Deploying %s transform units into environment %s as %s ...' %
                      (args.num_units, args.environment, username))
                data = object2json({'num_units': args.num_units}, False)
                r = requests.post(api_method(args, '{arg1}/{arg2}/environment/{environment}'),
                                  data=data, auth=auth, headers=headers)
                pprint(r.json())
            elif args.arg3 == 'remove':
                print('Removing %s transform units from environment %s as %s ...' %
                      (args.num_units, args.environment, username))
                data = object2json({'num_units': args.num_units}, False)
                r = requests.delete(api_method(args, '{arg1}/{arg2}/environment/{environment}'),
                                    data=data, auth=auth, headers=headers)
                pprint(r.json())
