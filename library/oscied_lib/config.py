#!/usr/bin/env python
# -*- coding: utf-8 -*-

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : COMMON LIBRARY
#
#  Project Manager : Bram Tullemans (tullemans@ebu.ch)
#  Main Developer  : David Fischer (david.fischer.ch@gmail.com)
#  Copyright       : Copyright (c) 2012-2013 EBU. All rights reserved.
#
#**********************************************************************************************************************#
#
# This file is part of EBU Technology & Innovation OSCIED Project.
#
# This project is free software: you can redistribute it and/or modify it under the terms of the EUPL v. 1.1 as provided
# by the European Commission. This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the European Union Public License for more details.
#
# You should have received a copy of the EUPL General Public License along with this project.
# If not, see he EUPL licence v1.1 is available in 22 languages:
#     22-07-2013, <https://joinup.ec.europa.eu/software/page/eupl/licence-eupl>
#
# Retrieved from https://github.com/ebu/OSCIED

from __future__ import absolute_import

import re
from os.path import expanduser, join
from urlparse import urlparse

from .config_base import CharmLocalConfig, CharmLocalConfig_Subordinate, CharmLocalConfig_Storage, MEDIAS_PATH


class OrchestraLocalConfig(CharmLocalConfig_Storage):

    def __init__(self, api_url=u'', root_secret=u'', node_secret=u'', mongo_admin_connection=u'',
                 mongo_node_connection=u'', rabbit_connection=u'', celery_config_file=u'celeryconfig.py',
                 celery_template_file=u'templates/celeryconfig.py.template', mongo_config_file=u'/etc/mongodb.conf',
                 ssh_config_path=u'~/.ssh', ssh_template_path=u'ssh', juju_config_file=u'~/.juju/environments.yaml',
                 juju_template_path=u'juju/', charms_config=u'config.yaml', charms_release=u'raring',
                 charms_repository=u'charms', email_server=u'', email_tls=False, email_username=u'', email_password=u'',
                 email_address=u'', email_ttask_template=u'templates/ttask_mail.template',
                 email_ptask_template=u'templates/ptask_mail.template', plugit_api_url=u'',
                 site_path=u'/etc/apache2/sites-available', site_template_file=u'templates/apache_site.template',
                 **kwargs):
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
        self.plugit_api_url = plugit_api_url
        self.site_path = site_path
        self.site_template_file = site_template_file

    @property
    def charms_default_path(self):
        return join(self.charms_repository, u'default')

    @property
    def charms_release_path(self):
        return join(self.charms_repository, self.charms_release)

    @property
    def transform_queues(self):
        # FIXME ideally the orchestrator will known what are the queues (https://github.com/ebu/OSCIED/issues/56)
        return (u'transform', )

    @property
    def publisher_queues(self):
        # FIXME ideally the orchestrator will known what are the queues (https://github.com/ebu/OSCIED/issues/56)
        return (u'publisher', )

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
        return join(self.charms_release_path, self.transform_service, u'config.yaml')

    @property
    def publisher_service(self):
        return u'oscied-publisher'

    @property
    def publisher_config(self):
        return join(self.charms_release_path, self.publisher_service, u'config.yaml')


class PublisherLocalConfig(CharmLocalConfig_Storage, CharmLocalConfig_Subordinate):

    def __init__(self, proxy_ips=None, apache_config_file=u'/etc/apache2/apache2.conf', www_root_path=u'/mnt',
                 publish_uri=u'', site_template_file=u'templates/default.template',
                 site_file=u'/etc/apache2/sites-available/default',
                 site_ssl_template_file=u'templates/default-ssl.template',
                 site_ssl_file=u'/etc/apache2/sites-available/default-ssl', **kwargs):
        super(PublisherLocalConfig, self).__init__(**kwargs)
        self.proxy_ips = proxy_ips or []
        self.apache_config_file = apache_config_file
        self.www_root_path, self.publish_uri = www_root_path, publish_uri
        self.site_template_file, self.site_file = site_template_file, site_file
        self.site_ssl_template_file, self.site_ssl_file = site_ssl_template_file, site_ssl_file

    @property
    def publish_path(self):
        return join(self.www_root_path, u'www')

    def publish_point(self, media):
        common = join(MEDIAS_PATH, media.user_id, media._id, media.filename)
        return (join(self.publish_path, common), join(self.publish_uri, common))

    def publish_uri_to_path(self, uri):
        u"""Convert a URI to a publication path or None if the URI does not start with self.publish_uri.

        **Example usage**

        >>> import copy
        >>> from .config_test import PUBLISHER_CONFIG_TEST
        >>> config = copy.copy(PUBLISHER_CONFIG_TEST)
        >>> print(config.publish_uri, config.publish_uri_to_path(u'test.mp4'))
        (u'', None)
        >>> config.update_publish_uri(u'my_host.com')
        >>> print(config.publish_uri_to_path(u'http://another_host.com/a_path/a_file.txt'))
        None
        >>> print(config.publish_uri_to_path(u'http://my_host.com/a_path/a_file.txt'))
        /mnt/www/a_path/a_file.txt
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
    from pytoolbox.encoding import configure_unicode
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
