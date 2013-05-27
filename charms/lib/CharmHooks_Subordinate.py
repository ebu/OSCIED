#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : COMMON LIBRARY
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

import pymongo.uri_parser, shutil
from CharmHooks import CharmHooks


class CharmHooks_Subordinate(CharmHooks):

    PACKAGES = ()

    def __init__(self, metadata, default_config, default_os_env):
        super(CharmHooks_Subordinate, self).__init__(metadata, default_config, default_os_env)
        self.local_config = None  # Must be set by derived class

    # ----------------------------------------------------------------------------------------------

    @property
    def rabbit_queues(self):
        return ','.join([self.config.rabbit_queues, self.public_address])

    @property
    def subordinate_config_is_enabled(self):
        return self.config.mongo_connection and self.config.rabbit_connection

    # ----------------------------------------------------------------------------------------------

    def subordinate_register(self, relation_name, mongo=None, rabbit=None):
        if self.subordinate_config_is_enabled:
            self.info('Override %s parameters with charm configuration' % relation_name)
            mongo = self.config.mongo_connection
            rabbit = self.config.rabbit_connection
            socket = self.config.api_nat_socket
        elif mongo and rabbit:
            self.info('Use %s parameters from charm %s relation' % relation_name)
            socket = ''
        else:
            return
        self.info('Register the Orchestrator')
        self.local_config.api_nat_socket = socket
        try:
            infos = pymongo.uri_parser.parse_uri(mongo)
            assert(len(infos['nodelist']) == 1)
            infos['host'], infos['port'] = infos['nodelist'][0]
            infos['rabbit'], infos['concurrency'] = rabbit, self.config.concurrency
            del infos['nodelist']
            assert(infos['host'] and infos['port'] and infos['username'] and infos['password'] and
                   infos['database'])
        except:
            raise ValueError('Unable to parse MongoDB connection %s' % mongo)
        with open(self.local_config.celery_template_file) as celery_template_file:
            data = celery_template_file.read()
            data = data.format(**infos)
            with open(self.local_config.celery_config_file, 'w') as celery_config_file:
                celery_config_file.write(data)
                self.remark('Orchestrator successfully registered')

    def subordinate_unregister(self):
        self.info('Unregister the Orchestrator')
        self.local_config.api_nat_socket = ''
        shutil.rmtree(self.local_config.celery_config_file, ignore_errors=True)

    def subordinate_hook_bypass(self, relation_name):
        if self.subordinate_config_is_enabled:
            raise RuntimeError(
                'Orchestrator is set in config, %s relation is disabled' % relation_name)

    # ----------------------------------------------------------------------------------------------

    def hook_subordinate_relation_joined(self):
        self.subordinate_hook_bypass()

    def hook_subordinate_relation_changed(self):
        self.subordinate_hook_bypass()
        address = self.relation_get('private-address')
        mongo = self.relation_get('mongo_connection')
        rabbit = self.relation_get('rabbit_connection')
        self.debug('Orchestra address is %s, MongoDB is %s, RabbitMQ is %s' %
                   (address, mongo, rabbit))
        if address and mongo and rabbit:
            self.hook_stop()
            self.subordinate_register(mongo, rabbit)
            self.hook_start()
        else:
            self.remark('Waiting for complete setup')

    def hook_subordinate_relation_broken(self):
        self.subordinate_hook_bypass()
        self.hook_stop()
        self.subordinate_unregister()
