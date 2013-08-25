#!/usr/bin/env python
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
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    from pprint import pprint
    from library.oscied_lib.oscied_api import OrchestraAPIClient
    from library.pyutils.py_unicode import configure_unicode

    configure_unicode()

    # Gather arguments
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter,
                            epilog=u'''Show interesting informations about a running orchestrator.''')
    parser.add_argument(u'host',   action=u'store', default=None)
    parser.add_argument(u'port',   action=u'store', default=5000)
    parser.add_argument(u'mail',   action=u'store', default=None)
    parser.add_argument(u'secret', action=u'store', default=None)
    args = parser.parse_args()

    client = OrchestraAPIClient(args.host, args.port)
    print(client.about)
    david = client.login(args.mail, args.secret)

    print(u'There are {0} registered users:'.format(len(client.users)))
    for user in client.users.list():
        print(u'\t{0}'.format(user.name))
    print(u'Our user:\n\t{0}'.format(client.users[client.auth._id].name))
    print(u'\nThere are {0} available media assets:'.format(len(client.medias)))
    for media in client.medias.list(head=True):
        print(u'\t{0} by user with id {1}'.format(media.metadata['title'], media.user_id))
    print(u'\nThere are {0} available environments:'.format(len(client.environments)))
    for environment in client.environments.list(head=True)['environments']:
        print(u'\t{0}'.format(environment))
    print(u'\nStatus of default environment:\n\t{0}'.format(client.environments['default']))
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

    #print(u'\nLaunch 2 new transformation units')
    #print(client.transform_units.add(num_units=2))
    #david = User(first_name='David', last_name='Fischer', mail='d@f.com', secret='oscied3D1', admin_platform=True)
    #print(client.users.add(david))

    #client.transform_units.add(1)
    #client.transform_units.remove(1)

    #print(client.users.list()[0].first_name)
    #print(david._id in client.users)
    #print(str(uuid.uuid4()) in client.users)
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
