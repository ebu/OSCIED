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

# FIXME handle SIGTERM to save state

import uuid, time
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from nose.tools import assert_raises
from oscied_lib.oscied_models import User
from oscied_lib.oscied_client import OrchestraAPIClient
from pyutils.py_datetime import datetime_now
from pyutils.py_exception import assert_raises_item
from pyutils.py_unicode import configure_unicode

EVENTS_TIMETABLE = {1: '0', 59: 'time'}


def main():
    configure_unicode()
    # Gather arguments
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter,
                            epilog=u'''Live-test security and functionalities of a running orchestrator.''')
    parser.add_argument(u'host',        action=u'store', default=None)
    parser.add_argument(u'port',        action=u'store', default=5000)
    parser.add_argument(u'root_secret', action=u'store', default=None)
    args = parser.parse_args()
    root = (u'root', args.root)
    client = OrchestraAPIClient(args.host, args.port, root)
    print(client.about)
    # print(u'Flush the database')
    # print(client.flush())
    print(u'Register an administrator')
    admin = User(first_name=u'Admin', last_name=u'Demo', mail=u'admin.demo@oscied.org', secret='big_secret_to_sav3',
                 admin_platform=True)
    admin = client.login_or_add(admin, root)
    events_loop(None, root, admin)


def events_loop(client, root, admin):
    old_index = None
    while True:
        # Get current time to retrieve state
        index = datetime_now(format=None).minute
        if index != old_index:
            old_index = index
            event = EVENTS_TIMETABLE.get(index, None)
            if event:
                handle_event(index, event)
            else:
                print(u'No event scheduled for minute {0}.'.format(index))
        else:
            print(u'Skip already consumed event for minute {0}.'.format(index))
        print(u'Sleep 10 seconds ...')
        time.sleep(10)


def handle_event(index, event):
    print(u'Handle scheduled event for minute {0} = {1}.'.format(index, event))
    pass

if __name__ == '__main__':
    main()
