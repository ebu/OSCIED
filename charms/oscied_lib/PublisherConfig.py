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
from urlparse import urlparse
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

    def publish_uri_to_path(self, uri):
        u"""Convert a URI to a publication path or None if the URI does not start with self.publish_uri.

        **Example usage**:

        >>> import copy
        >>> config = copy.copy(PUBLISHER_CONFIG_TEST)
        >>> print(config.publish_uri, config.publish_uri_to_path(u'test.mp4'))
        (u'', None)
        >>> config.update_publish_uri(u'my_host.com')
        >>> print(config.publish_uri_to_path(u'http://another_host.com/a_path/a_file.txt'))
        None
        >>> print(config.publish_uri_to_path(u'http://my_host.com/a_path/a_file.txt'))
        /var/www/a_path/a_file.txt
        """
        url = urlparse(uri)
        if u'{0}://{1}'.format(url.scheme, url.netloc) != self.publish_uri:
            return None
        return join(self.publish_path, url.path[1:].rstrip('/'))

    def update_publish_uri(self, public_address):
        self.publish_uri = u'http://{0}'.format(public_address)

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
