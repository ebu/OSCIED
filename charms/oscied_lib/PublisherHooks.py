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

import os, multiprocessing, setuptools.archive_util, shutil, time
from codecs import open
from kitchen.text.converters import to_bytes
from CharmHooks import DEFAULT_OS_ENV
from CharmHooks_Storage import CharmHooks_Storage
from CharmHooks_Subordinate import CharmHooks_Subordinate
from CharmHooks_Website import CharmHooks_Website
from PublisherConfig import PublisherConfig
from pyutils.py_filesystem import first_that_exist
from pyutils.py_subprocess import screen_launch, screen_list, screen_kill


class PublisherHooks(CharmHooks_Storage, CharmHooks_Subordinate, CharmHooks_Website):

    PACKAGES = tuple(set(
        CharmHooks_Storage.PACKAGES + CharmHooks_Subordinate.PACKAGES +
        CharmHooks_Website.PACKAGES + (u'apache2', u'apache2-threaded-dev', u'make', u'ntp')))

    def __init__(self, metadata, default_config, local_config_filename, default_os_env):
        super(PublisherHooks, self).__init__(metadata, default_config, default_os_env)
        self.local_config = PublisherConfig.read(local_config_filename, store_filename=True)
        self.local_config.update_publish_uri(self.public_address)
        self.debug(u'My __dict__ is {0}'.format(self.__dict__))

    # ------------------------------------------------------------------------------------------------------------------

    def hook_install(self):
        self.hook_uninstall()
        self.info(u'Upgrade system and install prerequisites')
        self.cmd(u'apt-add-repository -y ppa:jon-severinsson/ffmpeg')
        self.cmd(u'apt-get -y update', fail=False)
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
        self.info(u'{0} Apache H.264 streaming module'.format('Enable' if self.mod_streaming else 'Disable'))
        mods = (u'LoadModule h264_streaming_module /usr/lib/apache2/modules/mod_h264_streaming.so',
                u'AddHandler h264-streaming.extensions .mp4')
        lines = filter(lambda l: l not in mods, open(self.local_config.apache_config_file, u'r', u'utf-8'))
        if self.mod_streaming:
            lines += u'\n'.join(mods) + u'\n'
        open(self.local_config.apache_config_file, u'w', u'utf-8').write(u''.join(lines))
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
        shutil.rmtree(self.local_config.publish_path, ignore_errors=True)
        os.makedirs(self.local_config.publish_path)
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
            if screen_list(u'Publisher', log=self.debug) == []:
                screen_launch(u'Publisher', [u'celeryd', u'--config', u'celeryconfig', u'-Q', self.rabbit_queues])
            time.sleep(5)
            if screen_list(u'Publisher', log=self.debug) == []:
                raise RuntimeError(to_bytes(u'Publisher is not ready'))
            else:
                self.remark(u'Publisher successfully started')

    def hook_stop(self):
        screen_kill(u'Publisher', log=self.debug)
        self.cmd(u'service apache2 stop', fail=False)

# Main -----------------------------------------------------------------------------------------------------------------

if __name__ == u'__main__':
    from pyutils.py_unicode import configure_unicode
    configure_unicode()
    PublisherHooks(first_that_exist(u'metadata.yaml',    u'../oscied-publisher/metadata.yaml'),
                   first_that_exist(u'config.yaml',      u'../oscied-publisher/config.yaml'),
                   first_that_exist(u'local_config.pkl', u'../oscied-publisher/local_config.pkl'),
                   DEFAULT_OS_ENV).trigger()
