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
from kitchen.text.converters import to_bytes
from CharmHooks import DEFAULT_OS_ENV
from CharmHooks_Storage import CharmHooks_Storage
from CharmHooks_Subordinate import CharmHooks_Subordinate
from TransformConfig import TransformConfig
from pyutils.py_filesystem import first_that_exist
from pyutils.py_subprocess import screen_launch, screen_list, screen_kill


class TransformHooks(CharmHooks_Storage, CharmHooks_Subordinate):

    PACKAGES = tuple(set(CharmHooks_Storage.PACKAGES + CharmHooks_Subordinate.PACKAGES +
                     (u'ffmpeg', u'ntp', u'x264', u'libavcodec-dev', u'libavformat-dev', u'libavutil-dev',
                      u'libswscale-dev', u'libavdevice-dev', u'libavcodec-extra-53', u'zlib1g-dev')))

    def __init__(self, metadata, default_config, local_config_filename, default_os_env):
        super(TransformHooks, self).__init__(metadata, default_config, default_os_env)
        self.local_config = TransformConfig.read(local_config_filename, store_filename=True)
        self.debug(u'My __dict__ is {0}'.format(self.__dict__))

    # ------------------------------------------------------------------------------------------------------------------

    def hook_install(self):
        self.hook_uninstall()
        self.info(u'Upgrade system and install prerequisites')
        self.cmd(u'apt-add-repository -y ppa:jon-severinsson/ffmpeg')
        self.cmd(u'apt-get -y update', fail=False)
        self.cmd(u'apt-get -y upgrade')
        self.cmd(u'apt-get -y install {0}'.format(u' '.join(TransformHooks.PACKAGES)))
        self.info(u'Restart network time protocol service')
        self.cmd(u'service ntp restart')
        self.info(u'Compile and install GPAC/DashCast')
        shutil.rmtree(u'gpac', ignore_errors=True)
        setuptools.archive_util.unpack_archive(u'gpac.tar.bz2', u'gpac')
        os.chdir(u'gpac')
        self.cmd(u'./configure')
        self.cmd(u'make -j{0}'.format(multiprocessing.cpu_count()))
        self.cmd(u'make install')
        os.chdir(u'..')
        shutil.rmtree(u'gpac')

    def hook_config_changed(self):
        self.storage_remount()
        self.subordinate_register()

    def hook_uninstall(self):
        self.info(u'Uninstall prerequisities, unregister service and load default configuration')
        self.hook_stop()
        self.storage_unregister()
        self.subordinate_unregister()
        if self.config.cleanup:
            self.cmd(u'apt-get -y remove --purge {0}'.format(u' '.join(TransformHooks.PACKAGES)))
            self.cmd(u'apt-get -y autoremove')
        self.local_config.reset()

    def hook_start(self):
        if not self.storage_is_mounted:
            self.remark(u'Do not start transform daemon : No shared storage')
        elif not os.path.exists(self.local_config.celery_config_file):
            self.remark(u'Do not start transform daemon : No celery configuration file')
        elif len(self.rabbit_queues) == 0:
            self.remark(u'Do not start transform daemon : No RabbitMQ queues declared')
        else:
            self.save_local_config()  # Update local configuration file for transform daemon
            if screen_list(u'Transform', log=self.debug) == []:
                screen_launch(u'Transform', [u'celeryd', u'--config', u'celeryconfig', u'-Q', self.rabbit_queues])
            time.sleep(5)
            if screen_list(u'Transform', log=self.debug) == []:
                raise RuntimeError(to_bytes(u'Transform is not ready'))
            else:
                self.remark(u'Transform successfully started')

    def hook_stop(self):
        screen_kill(u'Transform', log=self.debug)

# Main -----------------------------------------------------------------------------------------------------------------

if __name__ == u'__main__':
    from pyutils.py_unicode import configure_unicode
    configure_unicode()
    TransformHooks(first_that_exist(u'metadata.yaml',    u'../oscied-transform/metadata.yaml'),
                   first_that_exist(u'config.yaml',      u'../oscied-transform/config.yaml'),
                   first_that_exist(u'local_config.pkl', u'../oscied-transform/local_config.pkl'),
                   DEFAULT_OS_ENV).trigger()
