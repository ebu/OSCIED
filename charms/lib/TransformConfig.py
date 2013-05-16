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

import logging
from Utilities import json2object, jsonfile2object, object2json


class TransformConfig(object):

    def __init__(self, verbose, public_address, mongo_connection, rabbit_connection, rabbit_queues,
                 api_nat_socket, storage_ip, storage_fstype, storage_mountpoint, storage_options,
                 storage_path):
        self.verbose = verbose
        self.public_address = public_address
        self.mongo_connection = mongo_connection
        self.rabbit_connection = rabbit_connection
        self.rabbit_queues = rabbit_queues
        self.api_nat_socket = api_nat_socket
        self.storage_ip = storage_ip
        self.storage_fstype = storage_fstype
        self.storage_mountpoint = storage_mountpoint
        self.storage_options = storage_options
        self.storage_path = storage_path

    @property
    def log_level(self):
        return logging.DEBUG if self.verbose else logging.INFO

    @property
    def storage_uri(self):
        if self.storage_fstype and self.storage_ip and self.storage_mountpoint:
            return self.storage_fstype + '://' + self.storage_ip + '/' + self.storage_mountpoint
        return None

    @staticmethod
    def read(filename):
        config = TransformConfig(None, None, None, None, None, None, None, None, None, None, None)
        jsonfile2object(filename, config)
        return config

    @staticmethod
    def load(json):
        config = TransformConfig(None, None, None, None, None, None, None, None, None, None, None)
        json2object(json, config)
        return config

TRANSFORM_CONFIG_TEST = TransformConfig(True, 'amazon.blabla.com',
                                        'mongodb://guest:Mongo@10.1.1.3:27017',
                                        'amqp://guest:Alice@10.1.1.3//', 'transform_private',
                                        '129.194.185.47:5000', '10.1.1.2', 'glusterfs',
                                        'medias_volume', '', '/mnt/storage')

# Main ---------------------------------------------------------------------------------------------

if __name__ == '__main__':

    print object2json(TRANSFORM_CONFIG_TEST, True)
    assert TRANSFORM_CONFIG_TEST.storage_uri == 'glusterfs://10.1.1.2/medias_volume'
    print TransformConfig.load(object2json(TRANSFORM_CONFIG_TEST, False))
