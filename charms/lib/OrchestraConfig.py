#! /usr/bin/env python
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
# Retrieved from:
#   svn co https://claire-et-david.dyndns.org/prog/OSCIED

import logging
from Utilities import json2object, jsonfile2object, object2json


class OrchestraConfig(object):

    def __init__(self, verbose, api_url, root_secret, nodes_secret, mongo_connection,
                 rabbit_connection, storage_ip, storage_fstype, storage_mountpoint,
                 storage_options, storage_path):
        self.verbose = verbose
        self.api_url = api_url
        self.root_secret = root_secret
        self.nodes_secret = nodes_secret
        self.mongo_connection = mongo_connection
        self.rabbit_connection = rabbit_connection
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

    @property
    def transform_queues(self):
        return ('transform_private', 'transform_amazon',)

    @property
    def publisher_queues(self):
        return ('publisher_private', 'publisher_amazon',)

    #def write(self, filename):
    #    with io.open(filename, 'w', encoding='utf-8') as outfile:
    #        json.dump(self, outfile)

    @staticmethod
    def read(filename):
        config = OrchestraConfig(None, None, None, None, None, None, None, None, None, None, None)
        jsonfile2object(filename, config)
        return config

    @staticmethod
    def load(json):
        config = OrchestraConfig(None, None, None, None, None, None, None, None, None, None, None)
        json2object(json, config)
        return config

ORCHESTRA_CONFIG_TEST = OrchestraConfig(True, 'http://127.0.0.1:5000', 'toto', 'abcd', '...', '...',
                                        '10.1.1.2', 'glusterfs', 'medias_volume', '', '/mnt/medias')

# Main ---------------------------------------------------------------------------------------------

if __name__ == '__main__':

    print object2json(ORCHESTRA_CONFIG_TEST, True)
    print ORCHESTRA_CONFIG_TEST.storage_uri
    print str(OrchestraConfig.load(object2json(ORCHESTRA_CONFIG_TEST, False)))
