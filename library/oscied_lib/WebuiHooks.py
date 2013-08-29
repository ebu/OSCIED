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

import os, shutil, socket, string
from codecs import open
from kitchen.text.converters import to_bytes
from random import choice
from oscied_config import WebuiLocalConfig
from oscied_config_base import MEDIAS_PATH, UPLOADS_PATH
from oscied_hook_base import CharmHooks_Storage, CharmHooks_Website, DEFAULT_OS_ENV
from pyutils.py_filesystem import chown, first_that_exist, try_makedirs, try_symlink
from pyutils.py_subprocess import rsync


class WebuiHooks(CharmHooks_Storage, CharmHooks_Website):

    PACKAGES = tuple(set(CharmHooks_Storage.PACKAGES + CharmHooks_Website.PACKAGES + (u'mysql-server', u'apache2',
                     u'php5', u'php5-cli', u'php5-curl', u'php5-gd', u'php5-mysql', u'libapache2-mod-auth-mysql',
                     u'ntp')))
    FIX_PACKAGES = (u'apache2.2-common', u'mysql-client-5.5', u'mysql-client-core-5.5', u'mysql-common',
                    u'mysql-server', u'mysql-server-5.1', u'mysql-server-5.5', u'mysql-server-core-5.5')

    def __init__(self, metadata, default_config, local_config_filename, default_os_env):
        super(WebuiHooks, self).__init__(metadata, default_config, default_os_env)
        self.local_config = WebuiLocalConfig.read(local_config_filename, store_filename=True)
        self.debug(u'My __dict__ is {0}'.format(self.__dict__))

    # ------------------------------------------------------------------------------------------------------------------

    def mysql_do(self, action=None, cli_input=None, fail=True):
        command = [u'mysql', u'-uroot', u'-p{0}'.format(self.config.mysql_root_password)]
        if action:
            command.extend([u'-e', action])
        return self.cmd(command=command, cli_input=cli_input, fail=fail)

    @staticmethod
    def randpass(length):
        chars = string.letters + string.digits
        return u''.join([choice(chars) for i in range(length)])

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
        self.hook_uninstall()
        self.info(u'Upgrade system, pre-configure and install prerequisites')
        self.cmd(u'apt-get -y update', fail=False)
        self.cmd(u'apt-get -y upgrade')
        try_makedirs(u'/etc/mysql')
        debconf, mysql = u'debconf-set-selections', u'mysql-server mysql-server'
        mysql_root_pass = self.config.mysql_root_password
        # Tip : http://ubuntuforums.org/showthread.php?t=981801
        self.cmd(debconf, input=u'{0}/root_password select {1}'.format(mysql, mysql_root_pass))
        self.cmd(debconf, input=u'{0}/root_password_again select {1}'.format(mysql, mysql_root_pass))
        self.cmd(u'apt-get -y install {0}'.format(u' '.join(WebuiHooks.PACKAGES)))
        self.info(u'Restart network time protocol service')
        self.cmd(u'service ntp restart')
        self.info(u'Import Web UI database and create user')
        hostname = socket.gethostname()
        self.cmd(u'service mysql start', fail=False)
        self.mysql_do(u"DROP USER ''@'localhost'; DROP USER ''@'{0}';".format(hostname), fail=False)
        self.mysql_do(u"GRANT ALL PRIVILEGES ON *.* TO 'root'@'%%' WITH GRANT OPTION;")
        self.mysql_do(u'DROP DATABASE IF EXISTS webui')
        self.mysql_do(cli_input=open(self.local_config.site_database_file, u'r', u'utf-8').read())
        self.mysql_do(u"GRANT ALL ON webui.* TO 'webui'@'%%' IDENTIFIED BY '{0}';".format(
                      self.config.mysql_user_password))
        self.info(u'Configure Apache 2')
        self.cmd(u'a2enmod rewrite')
        self.info(u'Copy and pre-configure Web UI')
        shutil.copy(self.local_config.site_template_file, self.local_config.sites_enabled_path)
        rsync(u'www/', self.local_config.www_root_path, archive=True, delete=True, exclude_vcs=True, recursive=True)
        chown(self.local_config.www_root_path, u'www-data', u'www-data', recursive=True)
        self.local_config.encryption_key = WebuiHooks.randpass(32)
        self.info(u'Expose Apache 2 service')
        self.open_port(80, u'TCP')

    def hook_config_changed(self):
        self.storage_remount()
        self.api_register()
        infos = self.config.__dict__
        infos.update(self.local_config.__dict__)
        infos[u'proxy_ips'] = self.proxy_ips_string
        infos[u'www_medias_uri'] = self.local_config.storage_uri(path=MEDIAS_PATH) or u''
        infos[u'www_uploads_uri'] = self.local_config.storage_uri(path=UPLOADS_PATH) or u''
        self.template2config(self.local_config.general_template_file,  self.local_config.general_config_file,  infos)
        self.template2config(self.local_config.database_template_file, self.local_config.database_config_file, infos)
        self.template2config(self.local_config.htaccess_template_file, self.local_config.htaccess_config_file, infos)
        if self.storage_is_mounted:
            self.info(u'Create uploads directory and symlink storage')
            try_makedirs(self.local_config.storage_uploads_path)
            chown(self.local_config.storage_uploads_path, u'www-data', u'www-data', recursive=True)
            try_symlink(self.local_config.storage_medias_path(), self.local_config.www_medias_path)
            try_symlink(self.local_config.storage_uploads_path, self.local_config.www_uploads_path)

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
        shutil.rmtree(self.local_config.www_root_path, ignore_errors=True)
        os.makedirs(self.local_config.www_root_path)
        self.local_config.reset()

    def hook_start(self):
        if not self.storage_is_mounted:
            self.remark(u'Do not start web user interface : No shared storage')
        elif not self.local_config.api_url:
            self.remark(u'Do not start web user interface : No orchestrator api')
        else:
            self.cmd(u'service mysql start')
            self.cmd(u'service apache2 start')
            self.remark(u'Web user interface successfully started')

    def hook_stop(self):
        self.cmd(u'service apache2 stop', fail=False)
        self.cmd(u'service mysql stop',   fail=False)

# Main -----------------------------------------------------------------------------------------------------------------

if __name__ == u'__main__':
    from pyutils.py_unicode import configure_unicode
    configure_unicode()
    WebuiHooks(first_that_exist(u'metadata.yaml',    u'../../charms/oscied-webui/metadata.yaml'),
               first_that_exist(u'config.yaml',      u'../../charms/oscied-webui/config.yaml'),
               first_that_exist(u'local_config.pkl', u'../../charms/oscied-webui/local_config.pkl'),
               DEFAULT_OS_ENV).trigger()
