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

import os, multiprocessing, pymongo.uri_parser, setuptools.archive_util, shutil, time
from CharmHooks import DEFAULT_OS_ENV
from CharmHooks_Storage import CharmHooks_Storage
from TransformConfig import TransformConfig
from pyutils.pyutils import first_that_exist, screen_launch, screen_list, screen_kill


class TransformHooks(CharmHooks_Storage):

    def __init__(self, metadata, default_config, local_config_filename, default_os_env):
        super(TransformHooks, self).__init__(metadata, default_config, default_os_env)
        self.local_config = TransformConfig.read(local_config_filename, store_filename=True)
        self.debug('My __dict__ is %s' % self.__dict__)

    # ----------------------------------------------------------------------------------------------

    @property
    def rabbit_queues(self):
        return ','.join([self.config.rabbit_queues, self.public_address])

    @property
    def transform_config_is_enabled(self):
        return self.config.mongo_connection and self.config.rabbit_connection

    # ----------------------------------------------------------------------------------------------

    def transform_register(self, mongo=None, rabbit=None):
        if self.transform_config_is_enabled:
            self.info('Override transform parameters with charm configuration')
            mongo = self.config.mongo_connection
            rabbit = self.config.rabbit_connection
            socket = self.config.api_nat_socket
        elif mongo and rabbit:
            self.info('Use transform parameters from charm transform relation')
            socket = ''
        else:
            return
        self.info('Register the Orchestrator')
        self.local_config.api_nat_socket = socket
        try:
            infos = pymongo.uri_parser.parse_uri(mongo)
            assert(len(infos['nodelist']) == 1)
            infos['host'], infos['port'] = infos['nodelist'][0]
            infos['rabbit'], infos['concurrency'] = rabbit, self.config.concurrency
            del infos['nodelist']
            assert(infos['host'] and infos['port'] and infos['username'] and infos['password'] and
                   infos['database'])
        except:
            raise ValueError('Unable to parse MongoDB connection %s' % mongo)
        with open(self.local_config.celery_template_file) as celery_template_file:
            data = celery_template_file.read()
            data = data.format(**infos)
            with open(self.local_config.celery_config_file, 'w') as celery_config_file:
                celery_config_file.write(data)
                self.remark('Orchestrator successfully registered')

    def transform_unregister(self):
        self.info('Unregister the Orchestrator')
        self.local_config.api_nat_socket = ''
        shutil.rmtree(self.local_config.celery_config_file, ignore_errors=True)

    def transform_hook_bypass(self):
        if self.transform_config_is_enabled:
            raise RuntimeError('Orchestrator is set in config, transform relation is disabled')

    # ----------------------------------------------------------------------------------------------

    def hook_install(self):
        self.hook_uninstall()
        self.info('Install prerequisites and upgrade packages')
        self.cmd('apt-add-repository -y ppa:jon-severinsson/ffmpeg')
        self.cmd('apt-get -y install ffmpeg ntp glusterfs-client nfs-common x264 libavcodec-dev '
                 'libavformat-dev libavutil-dev libswscale-dev libavdevice-dev libavcodec-extra-53 '
                 'zlib1g-dev')
        self.cmd('apt-get -y upgrade')
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
        # FIXME not necessary, but config-changed may create an infinite loop, so WE call it
        self.hook_config_changed()

    def hook_config_changed(self):
        # FIXME self.hook_stop()
        self.storage_remount()
        self.transform_register()
        # FIXME self.hook_start()

    def hook_uninstall(self):
        self.info('Uninstall prerequisities, unregister service and load default configuration')
        self.hook_stop()
        self.storage_unregister()
        self.transform_unregister()
        self.cmd('apt-get -y remove --purge ffmpeg glusterfs-server nfs-common x264 libavcodec-dev '
                 'libavformat-dev libavutil-dev libswscale-dev libavdevice-dev libavcodec-extra-53 '
                 'zlib1g-dev')
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
            if screen_list('Transform', log=self.debug) == []:
                os.chdir('lib')
                try:
                    screen_launch('Transform',
                                  ['celeryd', '--config', 'celeryconfig', '-Q', self.rabbit_queues])
                finally:
                    os.chdir('..')
            time.sleep(5)
            if screen_list('Transform', log=self.debug) == []:
                raise RuntimeError('Transform is not ready')
            else:
                self.remark('Transform successfully started')

    def hook_stop(self):
        screen_kill('Transform', log=self.debug)

    def hook_transform_relation_joined(self):
        self.transform_hook_bypass()

    def hook_transform_relation_changed(self):
        self.transform_hook_bypass()
        address = self.relation_get('private-address')
        mongo = self.relation_get('mongo_connection')
        rabbit = self.relation_get('rabbit_connection')
        self.debug('Orchestra address is %s, MongoDB is %s, RabbitMQ is %s' %
                   (address, mongo, rabbit))
        if address and mongo and rabbit:
            self.hook_stop()
            self.transform_register(mongo, rabbit)
            self.hook_start()
        else:
            self.remark('Waiting for complete setup')

    def hook_transform_relation_broken(self):
        self.transform_hook_bypass()
        self.hook_stop()
        self.transform_unregister()

    def hooks_footer(self):
        self.info('Save (updated) local configuration %s' % self.local_config)
        self.local_config.write()

if __name__ == '__main__':
    TransformHooks(first_that_exist('metadata.yaml', '../oscied-transform/metadata.yaml'),
                   first_that_exist('config.yaml', '../oscied-transform/config.yaml'),
                   first_that_exist('local_config.pkl', '../oscied-transform/local_config.pkl'),
                   DEFAULT_OS_ENV).trigger()
