#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : SCRIPTS
#
#  Authors   : David Fischer
#  Contact   : david.fischer.ch@gmail.com
#  Project   : OSCIED (OS Cloud Infrastructure for Encoding and Distribution)
#  Copyright : 2012-2013 OSCIED Team. All rights reserved.
#**********************************************************************************************************************#
#
# This file is part of EBU/UER OSCIED Project.
#
# This project is free software: you can redistribute it and/or modify it under the terms of the GNU General Public
# License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with this project.
# If not, see <http://www.gnu.org/licenses/>
#
# Retrieved from https://github.com/ebu/OSCIED

import requests
from pprint import pprint
from pyutils.py_serialization import object2json


def api_method(args, schema):
    method = u'http://{0}:{1}/'.format((args.host, args.port)) + schema.format(**args.__dict__)
    print(method)
    return method

if __name__ == u'__main__':
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    from pyutils.py_unicode import configure_unicode

    configure_unicode()

    api_args = ArgumentParser(add_help=False)
    api_args.add_argument(u'--host',     action=u'store', default=None, required=True)
    api_args.add_argument(u'--port',     action=u'store', default=5000)
    api_args.add_argument(u'--username', action=u'store', default=None)
    api_args.add_argument(u'--password', action=u'store', default=None)
    environment_args = ArgumentParser(add_help=False)
    environment_args.add_argument(u'environment', action=u'store')
    #num_units = ArgumentParser(add_help=False)
    #num_units.add_argument('num_units', action='store')

    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter, epilog=u'''TODO.''')
    subparsers = parser.add_subparsers(dest=u'arg1')

    environment = subparsers.add_parser(u'environment')
    environment_sub = environment.add_subparsers(dest=u'arg2')
    environment_list = environment_sub.add_parser(u'list', parents=[api_args])
    environment_add = environment_sub.add_parser(u'add',   parents=[api_args])
    environment_add.add_argument(u'name',           action=u'store')
    environment_add.add_argument(u'type',           action=u'store')
    environment_add.add_argument(u'region',         action=u'store')
    environment_add.add_argument(u'access_key',     action=u'store')
    environment_add.add_argument(u'secret_key',     action=u'store')
    environment_add.add_argument(u'control_bucket', action='store')
    environment_remove = environment_sub.add_parser(u'remove', parents=[api_args])
    environment_remove.add_argument(u'name', action=u'store')

    transform = subparsers.add_parser(u'transform')
    transform_sub = transform.add_subparsers(dest=u'arg2')
    transform_unit = transform_sub.add_parser(u'unit')
    transform_unit_sub = transform_unit.add_subparsers(dest=u'arg3')
    transform_unit_list = transform_unit_sub.add_parser(u'list',     parents=[api_args, environment_args])
    transform_unit_count = transform_unit_sub.add_parser(u'count',   parents=[api_args, environment_args])
    transform_unit_deploy = transform_unit_sub.add_parser(u'deploy', parents=[api_args, environment_args])
    transform_unit_deploy.add_argument(u'num_units', action=u'store')
    transform_unit_remove = transform_unit_sub.add_parser(u'remove', parents=[api_args, environment_args])
    transform_unit_remove.add_argument(u'num_units', action=u'store')

    args = parser.parse_args()
    username = args.username or u'anonymous'
    auth = (args.username, args.password) if args.username and args.password else None
    headers = {u'Content-type': u'application/json', u'Accept': u'application/json'}

    if args.arg1 == u'environment':
        if args.arg2 == u'count':
            print(u'Counting environments as {0} ...'.format(username))
            r = requests.get(api_method(args, u'{arg1}/{arg2}'), auth=auth)
            pprint(r.json())
        elif args.arg2 == u'list':
            print(u'Listing environments as {0} ...'.format(username))
            r = requests.get(api_method(args, u'{arg1}'), auth=auth)
            pprint(r.json())
        elif args.arg2 == 'add':
            print(u'Adding a new environment {0} as {1} ...'.format(args.name, username))
            data = object2json(args, False)
            r = requests.post(api_method(args, u'{arg1}'), data=data, auth=auth, headers=headers)
            pprint(r.json())
        elif args.arg2 == u'remove':
            print(u'Removing environment {0} as {1} ...'.format(args.name, username))
            r = requests.delete(api_method(args, u'{arg1}/name/{name}'), auth=auth)
            pprint(r.json())
    elif args.arg1 == u'transform':
        if args.arg2 == u'unit':
            if args.arg3 == u'count':
                print(u'Counting transform units of environment {0} as {1} ...'.format(args.environment, username))
                r = requests.get(api_method(args, u'{arg1}/{arg2}/environment/{environment}/{arg3}'), auth=auth)
                pprint(r.json())
            elif args.arg3 == u'list':
                print(u'Listing transform units of environment {0} as {1} ...'.format(args.environment, username))
                r = requests.get(api_method(args, u'{arg1}/{arg2}/environment/{environment}'), auth=auth)
                pprint(r.json())
            elif args.arg3 == u'deploy':
                print(u'Deploying {0} transform units into environment {1} as {2} ...'.format(
                      args.num_units, args.environment, username))
                data = object2json({u'num_units': args.num_units}, False)
                r = requests.post(api_method(args, u'{arg1}/{arg2}/environment/{environment}'),
                                  data=data, auth=auth, headers=headers)
                pprint(r.json())
            elif args.arg3 == u'remove':
                print(u'Removing %s transform units from environment {0} as {1} ...'.format(
                      args.num_units, args.environment, username))
                data = object2json({u'num_units': args.num_units}, False)
                r = requests.delete(api_method(args, u'{arg1}/{arg2}/environment/{environment}'),
                                    data=data, auth=auth, headers=headers)
                pprint(r.json())
