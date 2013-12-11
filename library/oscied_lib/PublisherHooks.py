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

import os, shutil
from codecs import open
from os.path import abspath, dirname, exists, join
from pytoolbox.filesystem import chown, first_that_exist
from pytoolbox.juju import  CONFIG_FILENAME, METADATA_FILENAME, DEFAULT_OS_ENV
from pytoolbox.subprocess import make

from .config import PublisherLocalConfig
from .constants import DAEMON_GROUP, DAEMON_USER, LOCAL_CONFIG_FILENAME
from .hooks_base import CharmHooks_Storage, CharmHooks_Subordinate, CharmHooks_Website

class PublisherHooks(CharmHooks_Storage, CharmHooks_Subordinate, CharmHooks_Website):

    PPAS = (u'ppa:jon-severinsson/ffmpeg',)
    PACKAGES = tuple(set(
        CharmHooks_Storage.PACKAGES + CharmHooks_Subordinate.PACKAGES +
        CharmHooks_Website.PACKAGES + (u'apache2', u'apache2-threaded-dev', u'make', u'ntp')))
    FIX_PACKAGES = (u'apache2.2-common',)

    def __init__(self, metadata, default_config, local_config_filename, default_os_env):
        super(PublisherHooks, self).__init__(metadata, default_config, default_os_env, local_config_filename,
                                             PublisherLocalConfig)

    # ------------------------------------------------------------------------------------------------------------------

    @property
    def publish_path(self):
        return join(self.config.www_root_path, u'www')

    # ------------------------------------------------------------------------------------------------------------------

    def hook_install(self):
        self.hook_uninstall()
        self.generate_locales((u'fr_CH.UTF-8',))
        self.install_packages(PublisherHooks.PACKAGES, ppas=PublisherHooks.PPAS)
        self.restart_ntp()
        self.info(u'Expose Apache 2 service')
        self.open_port(80, u'TCP')

    def hook_config_changed(self):
        cfg, local_cfg = self.config, self.local_config

        self.info(u'Configure Apache 2')
        self.info(u'{0} Apache H.264 streaming module'.format(u'Enable' if cfg.mod_streaming else u'Disable'))
        mods = (u'LoadModule h264_streaming_module /usr/lib/apache2/modules/mod_h264_streaming.so',
                u'AddHandler h264-streaming.extensions .mp4')
        lines = filter(lambda l: l not in mods, open(local_cfg.apache_config_file, u'r', u'utf-8'))
        if cfg.mod_streaming:
            lines += u'\n'.join(mods) + u'\n'
            if not local_cfg.mod_streaming_installed:
                self.info(u'Compile and install Apache H.264 streaming module')
                mod = u'mod_h264_streaming-2.2.7'
                apxs2 = self.cmd(u'which apxs2')[u'stdout']
                make(u'apache_{0}.tar.gz'.format(mod), path=mod, configure_options=u'--with-apxs={0}'.format(apxs2),
                     install=True, remove_temporary=True, log=self.debug)
                local_cfg.mod_streaming_installed = True
        open(local_cfg.apache_config_file, u'w', u'utf-8').write(u''.join(lines))

        infos = {u'publish_path': self.publish_path}
        self.template2config(local_cfg.site_template_file,     local_cfg.site_file, infos)
        self.template2config(local_cfg.site_ssl_template_file, local_cfg.site_ssl_file, infos)
        local_cfg.www_root_path = cfg.www_root_path
        self.storage_remount()
        self.subordinate_register()

    def hook_uninstall(self):
        self.info(u'Uninstall prerequisities, unregister service and load default configuration')
        self.hook_stop()
        self.storage_unregister()
        self.subordinate_unregister()
        if self.config.cleanup:
            self.cmd(u'apt-get -y remove --purge {0}'.format(u' '.join(PublisherHooks.PACKAGES)))
            self.cmd(u'apt-get -y remove --purge {0}'.format(u' '.join(PublisherHooks.FIX_PACKAGES)), fail=False)
            self.cmd(u'apt-get -y autoremove')
            shutil.rmtree(u'/etc/apache2/',     ignore_errors=True)
            shutil.rmtree(u'/var/log/apache2/', ignore_errors=True)
        shutil.rmtree(self.publish_path, ignore_errors=True)
        os.makedirs(self.publish_path)
        chown(self.publish_path, DAEMON_USER, DAEMON_GROUP, recursive=True)
        self.local_config.reset()
        self.local_config.update_publish_uri(self.public_address)

    def hook_start(self):
        if not self.storage_is_mounted:
            self.remark(u'Do not start publisher daemon : No shared storage')
        elif not exists(self.local_config.celery_config_file):
            self.remark(u'Do not start publisher daemon : No celery configuration file')
        elif len(self.rabbit_queues) == 0:
            self.remark(u'Do not start publisher daemon : No RabbitMQ queues declared')
        else:
            self.save_local_config()  # Update local configuration file for publisher daemon
            self.start_paya()  # Start paya monitoring (if paya_config_string set in config.yaml)
            self.cmd(u'service apache2 start')
            self.start_celeryd()

    def hook_stop(self):
        self.stop_celeryd()
        self.cmd(u'service apache2 stop', fail=False)

# Main -----------------------------------------------------------------------------------------------------------------

if __name__ == u'__main__':
    from pytoolbox.encoding import configure_unicode
    configure_unicode()
    publisher_path = abspath(join(dirname(__file__), u'../../charms/oscied-publisher'))
    PublisherHooks(first_that_exist(METADATA_FILENAME,     join(publisher_path, METADATA_FILENAME)),
                   first_that_exist(CONFIG_FILENAME,       join(publisher_path, CONFIG_FILENAME)),
                   first_that_exist(LOCAL_CONFIG_FILENAME, join(publisher_path, LOCAL_CONFIG_FILENAME)),
                   DEFAULT_OS_ENV).trigger()
