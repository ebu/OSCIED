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

from os.path import join
from CharmConfig_Storage import CharmConfig_Storage, MEDIAS_PATH
from CharmConfig_Subordinate import CharmConfig_Subordinate


class PublisherConfig(CharmConfig_Storage, CharmConfig_Subordinate):

    def __init__(self, proxy_ips=[], apache_config_file=u'/etc/apache2/apache2.conf', publish_uri=u'',
                 publish_path=u'/var/www', **kwargs):
        super(PublisherConfig, self).__init__(**kwargs)
        self.proxy_ips = proxy_ips
        self.apache_config_file = apache_config_file
        self.publish_uri = publish_uri
        self.publish_path = publish_path

    def publish_point(self, media):
        common = join(MEDIAS_PATH, media.user_id, media._id, media.filename)
        return (join(self.publish_path, common), join(self.publish_uri, common))

    def update_publish_uri(self, public_address):
        self.publish_uri = u'http://%s' % public_address

PUBLISHER_CONFIG_TEST = PublisherConfig(api_nat_socket=u'129.194.185.47:5000', storage_address=u'10.1.1.2',
                                        storage_fstype=u'glusterfs', storage_mountpoint=u'medias_volume')

# Main -----------------------------------------------------------------------------------------------------------------

if __name__ == u'__main__':
    from pyutils.py_unicode import configure_unicode
    configure_unicode()
    print(u'Test PublisherConfig with doctest')
    import doctest
    assert(doctest.testmod(verbose=False))
    print(u'OK')
    print(u'Write default publisher configuration')
    PublisherConfig().write(u'../oscied-publisher/local_config.pkl')
