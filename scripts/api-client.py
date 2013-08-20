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

if __name__ == '__main__':
    import uuid
    from pprint import pprint
    from oscied_lib.oscied_client import OrchestraAPIClient
    from pyutils.py_unicode import configure_unicode
    configure_unicode()

    client = OrchestraAPIClient(u'ec2-23-20-113-9.compute-1.amazonaws.com', 5000, (u'root', u'5FrvHcm7oyF4WQFW'))

    print(client.about)
    # #print(client.flush())
    david = client.login('d@f.com', 'oscied3D1')

    print(u'There are {0} registered users:'.format(len(client.users)))
    for user in client.users.list():
        print(u'\t{0}'.format(user.name))
    print(u'Our user:\n\t{0}'.format(client.users[client.auth._id].name))
    print(u'\nThere are {0} available media assets:'.format(len(client.medias)))
    for media in client.medias.list(head=True):
        print(u'\t{0} by user with id {1}'.format(media.metadata['title'], media.user_id))
    print(u'\nThere are {0} available environments:'.format(len(client.environments)))
    pprint(client.environments.list(head=True))
    print(u'\nDefault environment:\n\t{0}'.format(client.environments['default']))
    print(u'\nThere are {0} available encoders:'.format(len(client.encoders)))
    for encoder in client.encoders:
        print(u'\t{0}'.format(encoder))
    print(u'\nThere are {0} available transformation profiles:'.format(len(client.transform_profiles)))
    for profile in client.transform_profiles.list():
        print(u'\t{0} - {1}'.format(profile.title, profile.description))
    print(u'\nThere are {0} available transformation units:'.format(len(client.transform_units)))
    for number, unit in client.transform_units.list().iteritems():
         print(u'\t{0}: {1}'.format(number, unit))
    print(u'\nTransformation queues: \n\t{0}'.format(client.transform_queues))
    print(u'\nThere are {0} transformation tasks:'.format(len(client.transform_tasks)))
    for task in client.transform_tasks.list(head=True):
        pprint(task.__dict__)
    print(u'\nPublication queues: \n\t{0}'.format(client.publisher_queues))

def launch_task_mimic():
    task = client.transform_tasks.list(head=True)[0]
    task_id = client.transform_tasks.add({'filename': 'test.mp4', 'media_in_id': task.media_in_id, 'profile_id': task.profile_id, 'metadata': {'title':'test by python'}, 'queue': 'transform_private'})
    del client.transform_tasks[task_id]

def disabled_tests():

    #print(u'\nLaunch 2 new transformation units')
    #print(client.transform_units.add({'num_units': 2}))
    #david = User(first_name='David', last_name='Fischer', mail='d@f.com', secret='oscied3D1', admin_platform=True)
    #print(client.users.add(david))

    #client.transform_units.add(1)
    client.transform_units.remove(1)

    print(client.users.list()[0].first_name)
    #print(david._id in client.users)
    print(str(uuid.uuid4()) in client.users)
    #print(client.user[str(uuid.uuid4())])
    #del client.user[str(uuid.uuid4())]

    #import copy
    #david2 = copy.copy(david)
    #client.users[client.auth._id] = david
    #david2.mail = 'd2@f.com'
    #david2.first_name = 'David 2nd'
    #client.users.add(david2)
    #client.medias.add(Media(user_id=david._id, uri=None, public_uris=None, filename='test.mp4', metadata={'title': 'test import'}))
    #del client.environments['amazon']

    #media = client.medias.list()[0]
    #del client.medias[media._id]

    #del client.transform_profiles[client.transform_profiles.list()[0]._id]
    #client.transform_profiles.add(TransformProfile(title='salut', description='yo', encoder_name='copy'))


# if __name__ == u'__main__':
#     from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
#     from pyutils.py_unicode import configure_unicode

#     configure_unicode()

#     api_args = ArgumentParser(add_help=False)
#     api_args.add_argument(u'--host',     action=u'store', default=None, required=True)
#     api_args.add_argument(u'--port',     action=u'store', default=5000)
#     api_args.add_argument(u'--username', action=u'store', default=None)
#     api_args.add_argument(u'--password', action=u'store', default=None)
#     environment_args = ArgumentParser(add_help=False)
#     environment_args.add_argument(u'environment', action=u'store')
#     #num_units = ArgumentParser(add_help=False)
#     #num_units.add_argument('num_units', action='store')

#     parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter, epilog=u'''TODO.''')
#     subparsers = parser.add_subparsers(dest=u'arg1')

#     environment = subparsers.add_parser(u'environment')
#     environment_sub = environment.add_subparsers(dest=u'arg2')
#     environment_list = environment_sub.add_parser(u'list', parents=[api_args])
#     environment_add = environment_sub.add_parser(u'add',   parents=[api_args])
#     environment_add.add_argument(u'name',           action=u'store')
#     environment_add.add_argument(u'type',           action=u'store')
#     environment_add.add_argument(u'region',         action=u'store')
#     environment_add.add_argument(u'access_key',     action=u'store')
#     environment_add.add_argument(u'secret_key',     action=u'store')
#     environment_add.add_argument(u'control_bucket', action='store')
#     environment_remove = environment_sub.add_parser(u'remove', parents=[api_args])
#     environment_remove.add_argument(u'name', action=u'store')

#     transform = subparsers.add_parser(u'transform')
#     transform_sub = transform.add_subparsers(dest=u'arg2')
#     transform_unit = transform_sub.add_parser(u'unit')
#     transform_unit_sub = transform_unit.add_subparsers(dest=u'arg3')
#     transform_unit_list = transform_unit_sub.add_parser(u'list',     parents=[api_args, environment_args])
#     transform_unit_count = transform_unit_sub.add_parser(u'count',   parents=[api_args, environment_args])
#     transform_unit_deploy = transform_unit_sub.add_parser(u'deploy', parents=[api_args, environment_args])
#     transform_unit_deploy.add_argument(u'num_units', action=u'store')
#     transform_unit_remove = transform_unit_sub.add_parser(u'remove', parents=[api_args, environment_args])
#     transform_unit_remove.add_argument(u'num_units', action=u'store')

#     args = parser.parse_args()
#     username = args.username or u'anonymous'
#     auth = (args.username, args.password) if args.username and args.password else None
#     headers = {u'Content-type': u'application/json', u'Accept': u'application/json'}

#     if args.arg1 == u'environment':
#         if args.arg2 == u'count':
#             print(u'Counting environments as {0} ...'.format(username))
#             r = requests.get(api_method(args, u'{arg1}/{arg2}'), auth=auth)
#             pprint(r.json())
#         elif args.arg2 == u'list':
#             print(u'Listing environments as {0} ...'.format(username))
#             r = requests.get(api_method(args, u'{arg1}'), auth=auth)
#             pprint(r.json())
#         elif args.arg2 == 'add':
#             print(u'Adding a new environment {0} as {1} ...'.format(args.name, username))
#             data = object2json(args, False)
#             r = requests.post(api_method(args, u'{arg1}'), data=data, auth=auth, headers=headers)
#             pprint(r.json())
#         elif args.arg2 == u'remove':
#             print(u'Removing environment {0} as {1} ...'.format(args.name, username))
#             r = requests.delete(api_method(args, u'{arg1}/name/{name}'), auth=auth)
#             pprint(r.json())
#     elif args.arg1 == u'transform':
#         if args.arg2 == u'unit':
#             if args.arg3 == u'count':
#                 print(u'Counting transform units of environment {0} as {1} ...'.format(args.environment, username))
#                 r = requests.get(api_method(args, u'{arg1}/{arg2}/environment/{environment}/{arg3}'), auth=auth)
#                 pprint(r.json())
#             elif args.arg3 == u'list':
#                 print(u'Listing transform units of environment {0} as {1} ...'.format(args.environment, username))
#                 r = requests.get(api_method(args, u'{arg1}/{arg2}/environment/{environment}'), auth=auth)
#                 pprint(r.json())
#             elif args.arg3 == u'deploy':
#                 print(u'Deploying {0} transform units into environment {1} as {2} ...'.format(
#                       args.num_units, args.environment, username))
#                 data = object2json({u'num_units': args.num_units}, False)
#                 r = requests.post(api_method(args, u'{arg1}/{arg2}/environment/{environment}'),
#                                   data=data, auth=auth, headers=headers)
#                 pprint(r.json())
#             elif args.arg3 == u'remove':
#                 print(u'Removing %s transform units from environment {0} as {1} ...'.format(
#                       args.num_units, args.environment, username))
#                 data = object2json({u'num_units': args.num_units}, False)
#                 r = requests.delete(api_method(args, u'{arg1}/{arg2}/environment/{environment}'),
#                                     data=data, auth=auth, headers=headers)
#                 pprint(r.json())
