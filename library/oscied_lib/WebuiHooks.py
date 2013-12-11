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

from __future__ import absolute_import, division, print_function, unicode_literals

import shutil, socket, string
from codecs import open
from os.path import abspath, dirname, join
from pytoolbox.encoding import to_bytes
from pytoolbox.filesystem import chown, first_that_exist, try_makedirs, try_symlink
from pytoolbox.juju import  CONFIG_FILENAME, METADATA_FILENAME, DEFAULT_OS_ENV
from pytoolbox.serialization import object2dict
from pytoolbox.subprocess import rsync
from random import choice

from .config import WebuiLocalConfig
from .constants import  MEDIAS_PATH, UPLOADS_PATH, DAEMON_USER, DAEMON_GROUP, LOCAL_CONFIG_FILENAME
from .hooks_base import CharmHooks_Storage, CharmHooks_Website


class WebuiHooks(CharmHooks_Storage, CharmHooks_Website):

    PACKAGES = tuple(set(CharmHooks_Storage.PACKAGES + CharmHooks_Website.PACKAGES + (u'mysql-server', u'apache2',
                     u'php5', u'php5-cli', u'php5-curl', u'php5-gd', u'php5-mysql', u'libapache2-mod-auth-mysql',
                     u'ntp')))
    FIX_PACKAGES = (u'apache2.2-common', u'mysql-client-5.5', u'mysql-client-core-5.5', u'mysql-common',
                    u'mysql-server', u'mysql-server-5.1', u'mysql-server-5.5', u'mysql-server-core-5.5')

    def __init__(self, metadata, default_config, local_config_filename, default_os_env):
        super(WebuiHooks, self).__init__(metadata, default_config, default_os_env, local_config_filename,
                                         WebuiLocalConfig)

    # ------------------------------------------------------------------------------------------------------------------

    def mysql_do(self, action=None, cli_input=None, fail=True):
        command = [u'mysql', u'-uroot', u'-p{0}'.format(self.config.mysql_root_password)]
        if action:
            command.extend([u'-e', action])
        return self.cmd(command=command, cli_input=cli_input, fail=fail)

    @staticmethod
    def randpass(length):
        chars = string.letters + string.digits
        return u''.join([choice(chars) for i in xrange(length)])

    # ------------------------------------------------------------------------------------------------------------------

    @property
    def api_config_is_enabled(self):
        return self.config.api_url

    def api_hook_bypass(self):
        if self.api_config_is_enabled:
            raise RuntimeError(to_bytes(u'Orchestrator is set in config, api relation is disabled'))

    def api_register(self, api_url=None):
        if self.api_config_is_enabled:
            self.info(u'Override api parameters with charm configuration')
            self.local_config.api_url = self.config.api_url
        elif api_url:
            self.info(u'Use storage parameters from charm api relation')
            self.local_config.api_url = api_url

    def api_unregister(self):
        self.info(u'Unregister the Orchestrator')
        self.local_config.api_url = u''

    # ------------------------------------------------------------------------------------------------------------------

    def hook_api_relation_joined(self):
        self.api_hook_bypass()

    def hook_api_relation_changed(self):
        self.api_hook_bypass()
        # Get configuration from the relation
        api_url = self.relation_get(u'api_url')
        if not api_url:
            self.remark(u'Waiting for complete setup')
        else:
            self.hook_stop()
            self.api_register(api_url)
            self.hook_config_changed()
            self.hook_start()

    def hook_api_relation_broken(self):
        self.api_hook_bypass()
        self.hook_stop()
        self.api_unregister()
        self.hook_config_changed()

    # ------------------------------------------------------------------------------------------------------------------

    def hook_install(self):
        cfg = self.config
        self.hook_uninstall()
        self.generate_locales((u'fr_CH.UTF-8',))
        try_makedirs(u'/etc/mysql')
        debconf, mysql = u'debconf-set-selections', u'mysql-server mysql-server'
        # Tip : http://ubuntuforums.org/showthread.php?t=981801
        self.cmd(debconf, input=u'{0}/root_password select {1}'.format(mysql, cfg.mysql_root_password))
        self.cmd(debconf, input=u'{0}/root_password_again select {1}'.format(mysql, cfg.mysql_root_password))
        self.install_packages(WebuiHooks.PACKAGES)
        self.restart_ntp()
        self.info(u'Import Web UI database and create user')
        hostname = socket.gethostname()
        self.cmd(u'service mysql start', fail=False)
        self.mysql_do(u"DROP USER ''@'localhost'; DROP USER ''@'{0}';".format(hostname), fail=False)
        self.mysql_do(u"GRANT ALL PRIVILEGES ON *.* TO 'root'@'%%' WITH GRANT OPTION;")
        self.mysql_do(u'DROP DATABASE IF EXISTS webui')
        self.mysql_do(cli_input=open(self.local_config.site_database_file, u'r', u'utf-8').read())
        self.mysql_do(u"GRANT ALL ON webui.* TO 'webui'@'%%' IDENTIFIED BY '{0}';".format(cfg.mysql_user_password))
        self.info(u'Configure Apache 2')
        self.cmd(u'a2enmod rewrite')
        self.info(u'Copy and pre-configure Web UI')
        rsync(u'www/', self.local_config.site_directory, archive=True, delete=True, exclude_vcs=True, recursive=True)
        chown(self.local_config.site_directory, DAEMON_USER, DAEMON_GROUP, recursive=True)
        self.local_config.encryption_key = WebuiHooks.randpass(32)
        self.info(u'Expose Apache 2 service')
        self.open_port(80, u'TCP')

    def hook_config_changed(self):
        local_cfg = self.local_config

        self.info(u'Configure Apache 2')
        self.template2config(local_cfg.site_template_file, join(local_cfg.sites_available_path, self.name_slug), {
            u'directory': local_cfg.site_directory, u'domain': self.public_address
        })
        self.cmd(u'a2dissite default')
        self.cmd(u'a2ensite {0}'.format(self.name_slug))

        self.info(u'Configure CodeIgniter the PHP framework')
        self.storage_remount()
        self.api_register()
        infos = object2dict(self.config, include_properties=True)
        infos.update(object2dict(local_cfg, include_properties=True))
        infos[u'proxy_ips'] = self.proxy_ips_string
        infos[u'medias_uri'] = local_cfg.storage_uri(path=MEDIAS_PATH) or u''
        infos[u'uploads_uri'] = local_cfg.storage_uri(path=UPLOADS_PATH) or u''
        self.template2config(local_cfg.general_template_file,  local_cfg.general_config_file,  infos)
        self.template2config(local_cfg.database_template_file, local_cfg.database_config_file, infos)
        self.template2config(local_cfg.htaccess_template_file, local_cfg.htaccess_config_file, infos)
        if self.storage_is_mounted:
            self.info(u'Symlink shared storage for the web daemon')
            try_symlink(local_cfg.storage_medias_path(), local_cfg.medias_path)
            try_symlink(local_cfg.storage_uploads_path,  local_cfg.uploads_path)

    def hook_uninstall(self):
        self.info(u'Uninstall prerequisities, unregister service and load default configuration')
        self.hook_stop()
        self.storage_unregister()
        if self.config.cleanup:
            self.cmd(u'apt-get -y remove --purge {0}'.format(u' '.join(WebuiHooks.PACKAGES)))
            self.cmd(u'apt-get -y remove --purge {0}'.format(u' '.join(WebuiHooks.FIX_PACKAGES)), fail=False)
            self.cmd(u'apt-get -y autoremove')
            shutil.rmtree(u'/etc/apache2/',     ignore_errors=True)
            shutil.rmtree(u'/var/log/apache2/', ignore_errors=True)
            shutil.rmtree(u'/etc/mysql/',       ignore_errors=True)
            shutil.rmtree(u'/var/lib/mysql/',   ignore_errors=True)
            shutil.rmtree(u'/var/log/mysql/',   ignore_errors=True)
        shutil.rmtree(self.local_config.site_directory, ignore_errors=True)
        self.local_config.reset()

    def hook_start(self):
        if not self.storage_is_mounted:
            self.remark(u'Do not start web user interface : No shared storage')
        elif not self.local_config.api_url:
            self.remark(u'Do not start web user interface : No orchestrator api')
        else:
            self.start_paya()  # Start paya monitoring (if paya_config_string set in config.yaml)
            self.cmd(u'service mysql start')
            self.cmd(u'service apache2 start')
            self.remark(u'Web user interface successfully started')

    def hook_stop(self):
        self.cmd(u'service apache2 stop', fail=False)
        self.cmd(u'service mysql stop',   fail=False)

# Main -----------------------------------------------------------------------------------------------------------------

if __name__ == u'__main__':
    from pytoolbox.encoding import configure_unicode
    configure_unicode()
    webui_hooks = abspath(join(dirname(__file__), u'../../charms/oscied-webui'))
    WebuiHooks(first_that_exist(METADATA_FILENAME,     join(webui_hooks, METADATA_FILENAME)),
               first_that_exist(CONFIG_FILENAME,       join(webui_hooks, CONFIG_FILENAME)),
               first_that_exist(LOCAL_CONFIG_FILENAME, join(webui_hooks, LOCAL_CONFIG_FILENAME)),
               DEFAULT_OS_ENV).trigger()
