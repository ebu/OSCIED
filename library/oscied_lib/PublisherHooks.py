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

import os, multiprocessing, setuptools.archive_util, shutil
from codecs import open
from pytoolbox.filesystem import chown, first_that_exist
from pytoolbox.juju import DEFAULT_OS_ENV

from .config import PublisherLocalConfig
from .hooks_base import CharmHooks_Storage, CharmHooks_Subordinate, CharmHooks_Website


class PublisherHooks(CharmHooks_Storage, CharmHooks_Subordinate, CharmHooks_Website):

    PACKAGES = tuple(set(
        CharmHooks_Storage.PACKAGES + CharmHooks_Subordinate.PACKAGES +
        CharmHooks_Website.PACKAGES + (u'apache2', u'apache2-threaded-dev', u'make', u'ntp')))

    def __init__(self, metadata, default_config, local_config_filename, default_os_env):
        super(PublisherHooks, self).__init__(metadata, default_config, default_os_env)
        self.local_config = PublisherLocalConfig.read(local_config_filename, store_filename=True)
        self.local_config.update_publish_uri(self.public_address)
        self.debug(u'My __dict__ is {0}'.format(self.__dict__))

    # ------------------------------------------------------------------------------------------------------------------

    @property
    def publish_path(self):
        return os.path.join(self.config.www_root_path, 'www')

    # ------------------------------------------------------------------------------------------------------------------

    def hook_install(self):
        self.hook_uninstall()
        self.info(u'Generate locales if missing')
        self.cmd(u'locale-gen fr_CH.UTF-8')
        self.cmd(u'dpkg-reconfigure locales')
        self.info(u'Upgrade system and install prerequisites')
        self.cmd(u'apt-add-repository -y ppa:jon-severinsson/ffmpeg')
        self.cmd(u'apt-get -y update', fail=False)
        self.cmd(u'apt-get -y -f install')  # May recover problems with upgrade !
        self.cmd(u'apt-get -y upgrade')
        self.cmd(u'apt-get -y install {0}'.format(u' '.join(PublisherHooks.PACKAGES)))
        self.info(u'Restart network time protocol service')
        self.cmd(u'service ntp restart')
        self.info(u'Compile and install Apache H.264 streaming module')
        mod_streaming = u'mod_h264_streaming-2.2.7'
        shutil.rmtree(mod_streaming, ignore_errors=True)
        setuptools.archive_util.unpack_archive(u'apache_{0}.tar.gz'.format(mod_streaming), '.')
        os.chdir(mod_streaming)
        self.cmd(u'./configure --with-apxs={0}'.format(self.cmd('which apxs2')['stdout']))
        self.cmd(u'make -j{0}'.format(multiprocessing.cpu_count()))
        self.cmd(u'make install')
        os.chdir(u'..')
        shutil.rmtree(mod_streaming)
        self.info(u'Expose Apache 2 service')
        self.open_port(80, u'TCP')

    def hook_config_changed(self):
        self.info(u'Configure Apache 2')
        self.info(u'{0} Apache H.264 streaming module'.format('Enable' if self.config.mod_streaming else 'Disable'))
        mods = (u'LoadModule h264_streaming_module /usr/lib/apache2/modules/mod_h264_streaming.so',
                u'AddHandler h264-streaming.extensions .mp4')
        lines = filter(lambda l: l not in mods, open(self.local_config.apache_config_file, u'r', u'utf-8'))
        if self.config.mod_streaming:
            lines += u'\n'.join(mods) + u'\n'
        open(self.local_config.apache_config_file, u'w', u'utf-8').write(u''.join(lines))
        infos = {u'publish_path': self.publish_path}
        self.template2config(self.local_config.site_template_file, self.local_config.site_file, infos)
        self.template2config(self.local_config.site_ssl_template_file, self.local_config.site_ssl_file, infos)
        self.local_config.www_root_path = self.config.www_root_path
        self.storage_remount()
        self.subordinate_register()

    def hook_uninstall(self):
        self.info(u'Uninstall prerequisities, unregister service and load default configuration')
        self.hook_stop()
        self.storage_unregister()
        self.subordinate_unregister()
        if self.config.cleanup:
            self.cmd(u'apt-get -y remove --purge {0}'.format(u' '.join(PublisherHooks.PACKAGES)))
            self.cmd(u'apt-get -y remove --purge apache2.2-common', fail=False)  # Fixes some problems
            self.cmd(u'apt-get -y autoremove')
            shutil.rmtree('/etc/apache2/',      ignore_errors=True)
            shutil.rmtree(u'/var/log/apache2/', ignore_errors=True)
        shutil.rmtree(self.publish_path, ignore_errors=True)
        os.makedirs(self.publish_path)
        chown(self.publish_path, u'www-data', u'www-data', recursive=True)
        self.local_config.reset()
        self.local_config.update_publish_uri(self.public_address)

    def hook_start(self):
        if not self.storage_is_mounted:
            self.remark(u'Do not start publisher daemon : No shared storage')
        elif not os.path.exists(self.local_config.celery_config_file):
            self.remark(u'Do not start publisher daemon : No celery configuration file')
        elif len(self.rabbit_queues) == 0:
            self.remark(u'Do not start publisher daemon : No RabbitMQ queues declared')
        else:
            self.save_local_config()  # Update local configuration file for publisher daemon
            self.cmd(u'service apache2 start')
            self.start_celeryd()

    def hook_stop(self):
        self.stop_celeryd()
        self.cmd(u'service apache2 stop', fail=False)

# Main -----------------------------------------------------------------------------------------------------------------

if __name__ == u'__main__':
    from pytoolbox.encoding import configure_unicode
    configure_unicode()
    PublisherHooks(first_that_exist(u'metadata.yaml',    u'../../charms/oscied-publisher/metadata.yaml'),
                   first_that_exist(u'config.yaml',      u'../../charms/oscied-publisher/config.yaml'),
                   first_that_exist(u'local_config.pkl', u'../../charms/oscied-publisher/local_config.pkl'),
                   DEFAULT_OS_ENV).trigger()
