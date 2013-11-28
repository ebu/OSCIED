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

import os
from pytoolbox.filesystem import first_that_exist
from pytoolbox.juju import DEFAULT_OS_ENV
from pytoolbox.subprocess import make

from .config import TransformLocalConfig
from .hooks_base import CharmHooks_Storage, CharmHooks_Subordinate


class TransformHooks(CharmHooks_Storage, CharmHooks_Subordinate):

    FF_BIN_PACKAGES = (u'libgnutls28', u'libass4', u'libbluray1', u'libmp3lame0', u'libvorbis0a', u'libvorbisenc2',
                       u'libvorbisfile3', u'libvpx1', u'libxvidcore4')
    FF_DEV_PACKAGES = (u'libgnutls28-dev', u'libass-dev', u'libbluray-dev', u'libmp3lame-dev',
                       u'libtheora-dev', u'libvorbis-dev', u'libvpx-dev', u'libxvidcore-dev', u'zlib1g-dev')
    FF_CPL_PACKAGES = (u'autoconf', u'automake', u'build-essential', u'checkinstall', u'libtool', u'pkg-config',
                       u'texi2html', u'yasm', u'zlib1g-dev')
    FF_RMV_PACKAGES = (u'libgpac2', u'libgpac-dev')
    FF_ALL_PACKAGES = tuple(set(FF_BIN_PACKAGES + FF_DEV_PACKAGES + FF_CPL_PACKAGES))
    FF_LIBS = (u'gnutls', u'libass', u'libbluray', u'libmp3lame', u'libvorbis', u'libvpx', u'libx264', u'libxvid')
    FF_CONFIGURE_OPTIONS = u'--enable-gpl ' + u' '.join(u'--enable-{0}'.format(library) for library in FF_LIBS)

    PACKAGES = tuple(set(CharmHooks_Storage.PACKAGES + CharmHooks_Subordinate.PACKAGES + (u'ntp',)))


    def __init__(self, metadata, default_config, local_config_filename, default_os_env):
        super(TransformHooks, self).__init__(metadata, default_config, default_os_env)
        self.local_config = TransformLocalConfig.read(local_config_filename, store_filename=True)
        self.debug(u'My __dict__ is {0}'.format(self.__dict__))

    # ------------------------------------------------------------------------------------------------------------------

    def hook_install(self):
        self.hook_uninstall()
        self.info(u'Generate locales if missing')
        self.cmd(u'locale-gen fr_CH.UTF-8')
        self.cmd(u'dpkg-reconfigure locales')
        self.info(u'Upgrade system and install prerequisites')
        if 'ppa:' in self.config.ffmpeg_origin:
            self.cmd(u'apt-add-repository -y {0}'.format(self.config.ffmpeg_origin))
        self.cmd(u'apt-get -y update', fail=False)
        self.cmd(u'apt-get -y -f install')  # May recover problems with upgrade !
        self.cmd(u'apt-get -y upgrade')
        self.cmd(u'apt-get -y install {0}'.format(u' '.join(TransformHooks.PACKAGES)))
        self.info(u'Restart network time protocol service')
        self.cmd(u'service ntp restart')
        # FIXME Compile and install openSVCDecoder
        if 'tar.bz2' in self.config.open_hevc_origin:
            self.info(u'Compile and install openHEVC from archive {0}'.format(self.config.open_hevc_origin))
            self.cmd(u'apt-get -y install cmake')
            self.debug(make(self.config.open_hevc_origin, with_cmake=True, log=self.debug)['cmake'])
        if 'tar.bz2' in self.config.x264_origin:
            self.info(u'Compile and install x264')
            self.cmd(u'apt-get -y build-dep x264')
            self.debug(make(self.config.x264_origin, configure_options=u'--enable-shared', log=self.debug)['configure'])
        else:
            self.info(u'Install x264')
            self.cmd(u'apt-get -y install x264')
        if 'tar.bz2' in self.config.ffmpeg_origin:
            self.info(u'Compile and install ffmpeg from archive {0}'.format(self.config.ffmpeg_origin))
            self.cmd(u'apt-get -y install {0}'.format(u' '.join(TransformHooks.FF_ALL_PACKAGES)))
            self.cmd(u'apt-get -y remove {0}'.format(u' '.join(TransformHooks.FF_RMV_PACKAGES)))
            self.debug(make(self.config.ffmpeg_origin, configure_options=TransformHooks.FF_CONFIGURE_OPTIONS,
                       log=self.debug)['configure'])
        else:
            self.info(u'Install ffmpeg')
            self.cmd(u'apt-get -y install ffmpeg')
        if 'tar.bz2' in self.config.gpac_origin:
            self.info(u'Compile and install GPAC/DashCast from archive {0}'.format(self.config.gpac_origin))
            self.cmd(u'apt-get -y build-dep gpac')
            self.debug(make(u'gpac.tar.bz2', log=self.debug)['configure'])
        elif 'deb' in self.config.gpac_origin:
            self.info(u'Install GPAC/DashCast from debian package {0}'.format(self.config.gpac_origin))
            self.cmd(u'dpkg -i {0}'.format(self.config.gpac_origin), fail=False)
            self.cmd(u'apt-get -y -f install')
            self.cmd(u'dpkg -i {0}'.format(self.config.gpac_origin), fail=False)  # Reinstall package if removed !
        else:
            self.info(u'Install GPAC/DashCast')
            self.cmd(u'apt-get -y install gpac')

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
    from pytoolbox.encoding import configure_unicode
    configure_unicode()
    TransformHooks(first_that_exist(u'metadata.yaml',    u'../../charms/oscied-transform/metadata.yaml'),
                   first_that_exist(u'config.yaml',      u'../../charms/oscied-transform/config.yaml'),
                   first_that_exist(u'local_config.pkl', u'../../charms/oscied-transform/local_config.pkl'),
                   DEFAULT_OS_ENV).trigger()
