#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : COMMON LIBRARY
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

import pymongo.uri_parser, shutil
from kitchen.text.converters import to_bytes
from CharmHooks import CharmHooks


class CharmHooks_Subordinate(CharmHooks):

    PACKAGES = ()

    def __init__(self, metadata, default_config, default_os_env):
        super(CharmHooks_Subordinate, self).__init__(metadata, default_config, default_os_env)
        self.local_config = None  # Must be set by derived class

    # ------------------------------------------------------------------------------------------------------------------

    @property
    def rabbit_queues(self):
        return u','.join([self.config.rabbit_queues, self.public_address])

    @property
    def subordinate_config_is_enabled(self):
        return self.config.mongo_connection and self.config.rabbit_connection

    # ------------------------------------------------------------------------------------------------------------------

    def subordinate_register(self, mongo=None, rabbit=None):
        if self.subordinate_config_is_enabled:
            self.info(u'Override subordinate parameters with charm configuration')
            mongo = self.config.mongo_connection
            rabbit = self.config.rabbit_connection
            socket = self.config.api_nat_socket
        elif mongo and rabbit:
            self.info(u'Use subordinate parameters from charm relation')
            socket = u''
        else:
            return
        self.info(u'Register the Orchestrator')
        self.local_config.api_nat_socket = socket
        try:
            infos = pymongo.uri_parser.parse_uri(mongo)
            assert(len(infos[u'nodelist']) == 1)
            infos[u'host'], infos[u'port'] = infos[u'nodelist'][0]
            infos[u'rabbit'], infos[u'concurrency'] = rabbit, self.config.concurrency
            del infos[u'nodelist']
            assert(infos[u'host'] and infos[u'port'] and infos[u'username'] and infos[u'password'] and
                   infos[u'database'])
        except:
            raise ValueError(to_bytes(u'Unable to parse MongoDB connection {0}'.format(mongo)))
        self.template2config(self.local_config.celery_template_file, self.local_config.celery_config_file, infos)
        self.remark(u'Orchestrator successfully registered')

    def subordinate_unregister(self):
        self.info(u'Unregister the Orchestrator')
        self.local_config.api_nat_socket = u''
        shutil.rmtree(self.local_config.celery_config_file, ignore_errors=True)

    def subordinate_hook_bypass(self):
        if self.subordinate_config_is_enabled:
            raise RuntimeError(to_bytes(u'Orchestrator is set in config, subordinate relation is disabled'))

    # ------------------------------------------------------------------------------------------------------------------

    def hook_subordinate_relation_joined(self):
        self.subordinate_hook_bypass()

    def hook_subordinate_relation_changed(self):
        self.subordinate_hook_bypass()
        address = self.relation_get(u'private-address')
        mongo = self.relation_get(u'mongo_connection')
        rabbit = self.relation_get(u'rabbit_connection')
        self.debug(u'Orchestra address is {0}, MongoDB is {1}, RabbitMQ is {2}'.format(address, mongo, rabbit))
        if address and mongo and rabbit:
            self.hook_stop()
            self.subordinate_register(mongo, rabbit)
            self.hook_start()
        else:
            self.remark(u'Waiting for complete setup')

    def hook_subordinate_relation_broken(self):
        self.subordinate_hook_bypass()
        self.hook_stop()
        self.subordinate_unregister()
