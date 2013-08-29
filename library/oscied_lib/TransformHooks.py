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

import os, multiprocessing, setuptools.archive_util, shutil
from oscied_config import TransformLocalConfig
from oscied_hook_base import CharmHooks_Storage, CharmHooks_Subordinate, DEFAULT_OS_ENV
from pyutils.py_filesystem import first_that_exist, try_makedirs


class TransformHooks(CharmHooks_Storage, CharmHooks_Subordinate):

    PACKAGES = tuple(set(CharmHooks_Storage.PACKAGES + CharmHooks_Subordinate.PACKAGES +
                     (u'cmake',  u'ntp')))
    # u'libavcodec-dev', u'libavformat-dev', u'libavutil-dev',
    # u'libswscale-dev', u'libavdevice-dev', u'libavcodec-extra-53', u'zlib1g-dev'

    def __init__(self, metadata, default_config, local_config_filename, default_os_env):
        super(TransformHooks, self).__init__(metadata, default_config, default_os_env)
        self.local_config = TransformLocalConfig.read(local_config_filename, store_filename=True)
        self.debug(u'My __dict__ is {0}'.format(self.__dict__))

    # ------------------------------------------------------------------------------------------------------------------

    def hook_install(self):
        self.hook_uninstall()
        self.info(u'Upgrade system and install prerequisites')
        self.cmd(u'apt-add-repository -y ppa:jon-severinsson/ffmpeg')
        self.cmd(u'apt-get -y update', fail=False)
        self.cmd(u'apt-get -y upgrade')
        self.cmd(u'apt-get -y install {0}'.format(u' '.join(TransformHooks.PACKAGES)))
        self.cmd(u'apt-get -y build-dep gpac x264')
        self.info(u'Restart network time protocol service')
        self.cmd(u'service ntp restart')
        # FIXME Compile and install openSVCDecoder
        self.info(u'Compile and install openHEVC')
        shutil.rmtree(u'openHEVC', ignore_errors=True)
        setuptools.archive_util.unpack_archive(u'openHEVC.tar.bz2', u'openHEVC')
        os.chdir(u'openHEVC')
        try_makedirs(u'build')
        os.chdir(u'build')
        self.cmd(u'cmake -DCMAKE_BUILD_TYPE=RELEASE ..')
        self.cmd(u'make -j{0}'.format(multiprocessing.cpu_count()))
        self.cmd(u'make install')
        os.chdir(u'..')
        self.info(u'Compile and install GPAC/DashCast')
        shutil.rmtree(u'gpac', ignore_errors=True)
        setuptools.archive_util.unpack_archive(u'gpac.tar.bz2', u'gpac')
        os.chdir(u'gpac')
        self.cmd(u'./configure')
        self.cmd(u'make -j{0}'.format(multiprocessing.cpu_count()))
        self.cmd(u'make install')
        os.chdir(u'..')
        shutil.rmtree(u'gpac')
        self.info(u'Compile and install x264')
        shutil.rmtree(u'x264', ignore_errors=True)
        setuptools.archive_util.unpack_archive(u'x264.tar.bz2', u'x264')
        os.chdir(u'x264')
        self.cmd(u'./configure --enable-shared')
        self.cmd(u'make -j{0}'.format(multiprocessing.cpu_count()))
        self.cmd(u'make install')
        os.chdir(u'..')
        shutil.rmtree(u'x264')
        # FIXME Compile and install ffmpeg
        # http://ffmpeg.org/trac/ffmpeg/wiki/UbuntuCompilationGuide

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
            self.start_celeryd()

    def hook_stop(self):
        self.stop_celeryd()

# Main -----------------------------------------------------------------------------------------------------------------

if __name__ == u'__main__':
    from pyutils.py_unicode import configure_unicode
    configure_unicode()
    TransformHooks(first_that_exist(u'metadata.yaml',    u'../../charms/oscied-transform/metadata.yaml'),
                   first_that_exist(u'config.yaml',      u'../../charms/oscied-transform/config.yaml'),
                   first_that_exist(u'local_config.pkl', u'../../charms/oscied-transform/local_config.pkl'),
                   DEFAULT_OS_ENV).trigger()
