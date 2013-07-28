#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : COMMON LIBRARY
#
#  Authors   : David Fischer
#  Contact   : david.fischer.ch@gmail.com
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
# Retrieved from https://github.com/ebu/OSCIED

import os, multiprocessing, setuptools.archive_util, shutil, time
from CharmHooks import DEFAULT_OS_ENV
from CharmHooks_Storage import CharmHooks_Storage
from CharmHooks_Subordinate import CharmHooks_Subordinate
from TransformConfig import TransformConfig
from pyutils.py_filesystem import first_that_exist
from pyutils.py_subprocess import screen_launch, screen_list, screen_kill


class TransformHooks(CharmHooks_Storage, CharmHooks_Subordinate):

    PACKAGES = tuple(set(CharmHooks_Storage.PACKAGES + CharmHooks_Subordinate.PACKAGES +
                    ('ffmpeg', 'ntp', 'x264', 'libavcodec-dev', 'libavformat-dev', 'libavutil-dev',
                     'libswscale-dev', 'libavdevice-dev', 'libavcodec-extra-53', 'zlib1g-dev')))

    def __init__(self, metadata, default_config, local_config_filename, default_os_env):
        super(TransformHooks, self).__init__(metadata, default_config, default_os_env)
        self.local_config = TransformConfig.read(local_config_filename, store_filename=True)
        self.debug('My __dict__ is %s' % self.__dict__)

    # ----------------------------------------------------------------------------------------------

    def hook_install(self):
        self.hook_uninstall()
        self.info('Upgrade system and install prerequisites')
        self.cmd('apt-add-repository -y ppa:jon-severinsson/ffmpeg')
        self.cmd('apt-get -y update', fail=False)
        self.cmd('apt-get -y upgrade')
        self.cmd('apt-get -y install %s' % ' '.join(TransformHooks.PACKAGES))
        self.info('Restart network time protocol service')
        self.cmd('service ntp restart')
        self.info('Compile and install GPAC/DashCast')
        shutil.rmtree('gpac', ignore_errors=True)
        setuptools.archive_util.unpack_archive('gpac.tar.bz2', 'gpac')
        os.chdir('gpac')
        self.cmd('./configure')
        self.cmd('make -j%s' % multiprocessing.cpu_count())
        self.cmd('make install')
        os.chdir('..')
        shutil.rmtree('gpac')

    def hook_config_changed(self):
        self.storage_remount()
        self.subordinate_register()

    def hook_uninstall(self):
        self.info('Uninstall prerequisities, unregister service and load default configuration')
        self.hook_stop()
        self.storage_unregister()
        self.subordinate_unregister()
        self.cmd('apt-get -y remove --purge %s' % ' '.join(TransformHooks.PACKAGES))
        self.cmd('apt-get -y autoremove')
        self.local_config.reset()

    def hook_start(self):
        if not self.storage_is_mounted:
            self.remark('Do not start transform daemon : No shared storage')
        elif not os.path.exists(self.local_config.celery_config_file):
            self.remark('Do not start transform daemon : No celery configuration file')
        elif len(self.rabbit_queues) == 0:
            self.remark('Do not start transform daemon : No RabbitMQ queues declared')
        else:
            self.save_local_config()  # Update local configuration file for transform daemon
            if screen_list('Transform', log=self.debug) == []:
                screen_launch(
                    'Transform', ['celeryd', '--config', 'celeryconfig', '-Q', self.rabbit_queues])
            time.sleep(5)
            if screen_list('Transform', log=self.debug) == []:
                raise RuntimeError('Transform is not ready')
            else:
                self.remark('Transform successfully started')

    def hook_stop(self):
        screen_kill('Transform', log=self.debug)

# Main ---------------------------------------------------------------------------------------------

if __name__ == '__main__':
    TransformHooks(first_that_exist('metadata.yaml',    '../oscied-transform/metadata.yaml'),
                   first_that_exist('config.yaml',      '../oscied-transform/config.yaml'),
                   first_that_exist('local_config.pkl', '../oscied-transform/local_config.pkl'),
                   DEFAULT_OS_ENV).trigger()
