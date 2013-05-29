#!/usr/bin/env python2
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
# Retrieved from https://github.com/EBU-TI/OSCIED

from __future__ import absolute_import

import os, multiprocessing, setuptools.archive_util, shutil, time
from .CharmHooks import DEFAULT_OS_ENV
from .CharmHooks_Storage import CharmHooks_Storage
from .CharmHooks_Subordinate import CharmHooks_Subordinate
from .CharmHooks_Website import CharmHooks_Website
from .PublisherConfig import PublisherConfig
from .pyutils.pyutils import first_that_exist, screen_launch, screen_list, screen_kill


class PublisherHooks(CharmHooks_Storage, CharmHooks_Subordinate, CharmHooks_Website):

    PACKAGES = tuple(set(CharmHooks_Storage.PACKAGES + CharmHooks_Subordinate.PACKAGES +
                    ('apache2', 'apache2-threaded-dev', 'make', 'ntp')))

    def __init__(self, metadata, default_config, local_config_filename, default_os_env):
        super(PublisherHooks, self).__init__(metadata, default_config, default_os_env)
        self.local_config = PublisherConfig.read(local_config_filename, store_filename=True)
        self.local_config.update_publish_uri(self.public_address)
        self.debug('My __dict__ is %s' % self.__dict__)

    # ----------------------------------------------------------------------------------------------

    def hook_install(self):
        self.hook_uninstall()
        self.info('Upgrade system and install prerequisites')
        self.cmd('apt-add-repository -y ppa:jon-severinsson/ffmpeg')
        self.cmd('apt-get -y update', fail=False)
        self.cmd('apt-get -y upgrade')
        self.cmd('apt-get -y install %s' % ' '.join(PublisherHooks.PACKAGES))
        self.info('Restart network time protocol service')
        self.cmd('service ntp restart')
        self.info('Compile and install Apache H.264 streaming module')
        mod_streaming = 'mod_h264_streaming-2.2.7'
        shutil.rmtree(mod_streaming, ignore_errors=True)
        setuptools.archive_util.unpack_archive('apache_%s.tar.gz' % mod_streaming, '.')
        os.chdir(mod_streaming)
        self.cmd('./configure --with-apxs=%s' % self.cmd('which apxs2')['stdout'])
        self.cmd('make -j%s' % multiprocessing.cpu_count())
        self.cmd('make install')
        os.chdir('..')
        shutil.rmtree(mod_streaming)
        self.info('Register Apache H.264 streaming module')
        mods = ('LoadModule h264_streaming_module /usr/lib/apache2/modules/mod_h264_streaming.so',
                'AddHandler h264-streaming.extensions .mp4')
        lines = filter(lambda l: l not in mods, open(self.local_config.apache_config_file))
        lines += '\n'.join(mods) + '\n'
        open(self.local_config.apache_config_file, 'w').write(''.join(lines))
        self.info('Expose Apache 2 service')
        self.open_port(80, 'TCP')

    def hook_config_changed(self):
        self.storage_remount()
        self.subordinate_register()

    def hook_uninstall(self):
        self.info('Uninstall prerequisities, unregister service and load default configuration')
        self.hook_stop()
        self.storage_unregister()
        self.subordinate_unregister()
        self.cmd('apt-get -y remove --purge %s' % ' '.join(PublisherHooks.PACKAGES))
        self.cmd('apt-get -y remove --purge apache2.2-common', fail=False)  # Fixes some problems
        self.cmd('apt-get -y autoremove')
        shutil.rmtree('/etc/apache2/', ignore_errors=True)
        shutil.rmtree(self.local_config.publish_path, ignore_errors=True)
        shutil.rmtree('/var/log/apache2/', ignore_errors=True)
        os.makedirs(self.local_config.publish_path)
        self.local_config.reset(reset_publish_uri=False)

    def hook_start(self):
        if not self.storage_is_mounted:
            self.remark('Do not start publisher daemon : No shared storage')
        elif not os.path.exists(self.local_config.celery_config_file):
            self.remark('Do not start publisher daemon : No celery configuration file')
        elif len(self.rabbit_queues) == 0:
            self.remark('Do not start publisher daemon : No RabbitMQ queues declared')
        else:
            self.cmd('service apache2 start')
            if screen_list('Publisher', log=self.debug) == []:
                os.chdir('oscied_lib')
                try:
                    screen_launch('Publisher',
                                  ['celeryd', '--config', 'celeryconfig', '-Q', self.rabbit_queues])
                finally:
                    os.chdir('..')
            time.sleep(5)
            if screen_list('Publisher', log=self.debug) == []:
                raise RuntimeError('Publisher is not ready')
            else:
                self.remark('Publisher successfully started')

    def hook_stop(self):
        screen_kill('Publisher', log=self.debug)
        self.cmd('service apache2 stop', fail=False)

    def hooks_footer(self):
        self.info('Save (updated) local configuration %s' % self.local_config)
        self.local_config.write()

if __name__ == '__main__':
    PublisherHooks(first_that_exist('metadata.yaml', '../oscied-publisher/metadata.yaml'),
                   first_that_exist('config.yaml', '../oscied-publisher/config.yaml'),
                   first_that_exist('local_config.pkl', '../oscied-publisher/local_config.pkl'),
                   DEFAULT_OS_ENV).trigger()
