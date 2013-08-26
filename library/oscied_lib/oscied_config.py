#!/usr/bin/env python
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

import re
from os.path import expanduser, join
from urlparse import urlparse
from oscied_config_base import CharmLocalConfig, CharmLocalConfig_Subordinate, CharmLocalConfig_Storage, MEDIAS_PATH


class OrchestraLocalConfig(CharmLocalConfig_Storage):

    def __init__(self, api_url=u'', root_secret=u'', node_secret=u'', mongo_admin_connection=u'',
                 mongo_node_connection=u'', rabbit_connection=u'',
                 celery_config_file=u'celeryconfig.py',
                 celery_template_file=u'templates/celeryconfig.py.template',
                 mongo_config_file=u'/etc/mongodb.conf', ssh_config_path=u'~/.ssh',
                 ssh_template_path=u'ssh', juju_config_file=u'~/.juju/environments.yaml',
                 juju_template_path=u'juju/', charms_config=u'config.yaml',
                 charms_release=u'raring', charms_repository=u'charms', email_server=u'', email_tls=False,
                 email_username=u'', email_password=u'', email_address=u'',
                 email_ttask_template=u'templates/ttask_mail.template',
                 email_ptask_template=u'templates/ptask_mail.template', **kwargs):
        super(OrchestraLocalConfig, self).__init__(**kwargs)
        self.api_url = api_url
        self.root_secret = root_secret
        self.node_secret = node_secret
        self.mongo_admin_connection = mongo_admin_connection
        self.mongo_node_connection = mongo_node_connection
        self.rabbit_connection = rabbit_connection
        self.celery_config_file = celery_config_file
        self.celery_template_file = celery_template_file
        self.mongo_config_file = mongo_config_file
        self.ssh_config_path = expanduser(ssh_config_path)
        self.ssh_template_path = ssh_template_path
        self.juju_config_file = expanduser(juju_config_file)
        self.juju_template_path = juju_template_path
        self.charms_config = charms_config
        self.charms_release = charms_release
        self.charms_repository = charms_repository
        self.email_server = email_server
        self.email_tls = email_tls
        self.email_address = email_address
        self.email_username = email_username
        self.email_password = email_password
        self.email_ttask_template = email_ttask_template
        self.email_ptask_template = email_ptask_template

    @property
    def transform_queues(self):
        return (u'transform_private', u'transform_amazon',)

    @property
    def publisher_queues(self):
        return (u'publisher_private', u'publisher_amazon',)

    @property
    def orchestra_service(self):
        return u'oscied-orchestra'

    @property
    def storage_service(self):
        return u'oscied-storage'

    @property
    def transform_service(self):
        return u'oscied-transform'

    @property
    def transform_config(self):
        return join(self.charms_repository, self.charms_release, self.transform_service, u'config.yaml')


class PublisherLocalConfig(CharmLocalConfig_Storage, CharmLocalConfig_Subordinate):

    def __init__(self, proxy_ips=None, apache_config_file=u'/etc/apache2/apache2.conf', publish_uri=u'',
                 publish_path=u'/var/www', **kwargs):
        super(PublisherLocalConfig, self).__init__(**kwargs)
        self.proxy_ips = proxy_ips or []
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
        >>> from oscied_config_test import PUBLISHER_CONFIG_TEST
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


class StorageLocalConfig(CharmLocalConfig):

    def __init__(self, allowed_ips=None, volume_flag=False, **kwargs):
        super(StorageLocalConfig, self).__init__(**kwargs)
        self.allowed_ips = allowed_ips or []
        self.volume_flag = volume_flag
        self.volume_infos_regex = re.compile(
            r".*Volume Name:\s*(?P<name>\S+)\s+.*Type:\s*(?P<type>\S+)\s+.*"
            r"Status:\s*(?P<status>\S+)\s+.*Transport-type:\s*(?P<transport>\S+).*", re.DOTALL)


class TransformLocalConfig(CharmLocalConfig_Storage, CharmLocalConfig_Subordinate):

    def __init__(self, **kwargs):
        super(TransformLocalConfig, self).__init__(**kwargs)


class WebuiLocalConfig(CharmLocalConfig_Storage):

    def __init__(self, api_url=u'', encryption_key=u'', proxy_ips=None,
                 sites_enabled_path=u'/etc/apache2/sites-enabled', site_database_file=u'webui-db.sql',
                 site_template_file=u'templates/000-default', htaccess_template_file=u'templates/htaccess.template',
                 general_template_file=u'templates/config.php.template',
                 database_template_file=u'templates/database.php.template', htaccess_config_file=u'/var/www/.htaccess',
                 general_config_file=u'/var/www/application/config/config.php',
                 database_config_file=u'/var/www/application/config/database.php', www_root_path=u'/var/www',
                 www_medias_path=u'/var/www/medias', www_uploads_path=u'/var/www/uploads', **kwargs):
        super(WebuiLocalConfig, self).__init__(**kwargs)
        self.api_url = api_url
        self.encryption_key = encryption_key
        self.proxy_ips = proxy_ips or []
        self.sites_enabled_path = sites_enabled_path
        self.site_database_file = site_database_file
        self.site_template_file = site_template_file
        self.htaccess_template_file = htaccess_template_file
        self.general_template_file = general_template_file
        self.database_template_file = database_template_file
        self.htaccess_config_file = htaccess_config_file
        self.general_config_file = general_config_file
        self.database_config_file = database_config_file
        self.www_root_path = www_root_path
        self.www_medias_path = www_medias_path
        self.www_uploads_path = www_uploads_path


# Main -----------------------------------------------------------------------------------------------------------------

if __name__ == u'__main__':
    from pyutils.py_unicode import configure_unicode
    configure_unicode()
    print(u'Test configuration module with doctest')
    import doctest
    assert(doctest.testmod(verbose=False))
    print(u'OK')
    print(u'Write default orchestra local configuration')
    OrchestraLocalConfig().write(u'../../charms/oscied-orchestra/local_config.pkl')
    print(u'Write default publisher local configuration')
    PublisherLocalConfig().write(u'../../charms/oscied-publisher/local_config.pkl')
    print(u'Write default storage local configuration')
    StorageLocalConfig().write(u'../../charms/oscied-storage/local_config.pkl')
    print(u'Write default transform local configuration')
    TransformLocalConfig().write(u'../../charms/oscied-transform/local_config.pkl')
    print('Write default web user interface local configuration')
    WebuiLocalConfig().write('../../charms/oscied-webui/local_config.pkl')
