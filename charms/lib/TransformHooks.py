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

import os, pymongo.uri_parser, re, shutil, time
from CharmHooks import CharmHooks, DEFAULT_OS_ENV
from TransformConfig import TransformConfig
from pyutils.pyutils import first_that_exist, screen_launch, screen_list, screen_kill, try_makedirs


class TransformHooks(CharmHooks):

    def __init__(self, metadata, default_config, local_config_filename, default_os_env):
        super(TransformHooks, self).__init__(metadata, default_config, default_os_env)
        self.local_config = TransformConfig.read(local_config_filename, store_filename=True)
        self.debug('My __dict__ is %s' % self.__dict__)

    # ----------------------------------------------------------------------------------------------

    @property
    def rabbit_queues(self):
        return ','.join([self.config.rabbit_queues, self.public_address])

    @property
    def storage_config_is_enabled(self):
        c = self.config
        return c.storage_address and c.storage_fstype and c.storage_mountpoint

    @property
    def storage_is_mounted(self):
        return os.path.ismount(self.local_config.storage_path)

    @property
    def transform_config_is_enabled(self):
        return self.config.mongo_connection and self.config.rabbit_connection

    # ----------------------------------------------------------------------------------------------

    def storage_remount(self, address=None, fstype=None, mountpoint=None, options=''):
        if self.storage_config_is_enabled:
            self.info('Override storage parameters with charm configuration')
            address = self.config.storage_address
            nat_address = self.config.storage_nat_address
            fstype = self.config.storage_fstype
            mountpoint = self.config.storage_mountpoint
            options = self.config.storage_options
        elif address and fstype and mountpoint:
            self.info('Use storage parameters from charm storage relation')
            nat_address = ''
        else:
            return
        if nat_address:
            self.info('Update hosts file to map storage internal address %s to %s' %
                      (address, nat_address))
            nat_line = '%s %s' % (nat_address, address)
            with open(self.local_config.hosts_file, 'rw') as hosts_file:
                data = hosts_file.read()
                re.sub(re.escape(nat_address) + r' .*', nat_line, data)
                if nat_line not in data:
                    data.append(nat_line)
                # FIXME maybe a better idea to write to a temporary file then rename it /etc/hosts
                hosts_file.f.seek(0)
                hosts_file.f.truncate()
                hosts_file.write()
        # FIXME avoid unregistering storage if it does not change ...
        self.storage_unregister()
        self.debug("Mount shared storage [%s] %s:%s type %s options '%s' -> %s" % (nat_address,
                  address, mountpoint, fstype, options, self.local_config.storage_path))
        try_makedirs(self.local_config.storage_path)
        # FIXME try 5 times, a better way to handle failure
        for i in range(5):
            if self.storage_is_mounted:
                break
            mount_address = '%s:/%s' % (nat_address or address, mountpoint)
            mount_path = self.local_config.storage_path
            if options:
                self.cmd(['mount', '-t', fstype, '-o', options, mount_address, mount_path])
            else:
                self.cmd(['mount', '-t', fstype, mount_address, mount_path])
            time.sleep(5)
        if self.storage_is_mounted:
            # FIXME update /etc/fstab (?)
            self.local_config.storage_address = address
            self.local_config.storage_nat_address = nat_address
            self.local_config.storage_fstype = fstype
            self.local_config.storage_mountpoint = mountpoint
            self.local_config.storage_options = options
            self.remark('Shared storage successfully registered')
        else:
            raise IOError('Unable to mount shared storage')

    def storage_unregister(self):
        self.info('Unregister shared storage')
        self.local_config.storage_address = ''
        self.local_config.storage_fstype = ''
        self.local_config.storage_mountpoint = ''
        self.local_config.storage_options = ''
        if self.storage_is_mounted:
            # FIXME update /etc/fstab (?)
            self.remark('Unmount shared storage (is mounted)')
            self.cmd(['umount', self.local_config.storage_path])
        else:
            self.remark('Shared storage already unmounted')

    def storage_hook_bypass(self):
        if self.storage_config_is_enabled:
            raise RuntimeError('Shared storage is set in config, storage relation is disabled')

    # ----------------------------------------------------------------------------------------------

    def transform_register(self, mongo=None, rabbit=None, socket=''):
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
            host, port = infos['nodelist'][0]
            username = infos['username']
            password = infos['password']
            database = infos['database']
            assert(len(infos['nodelist']) == 1)
            assert(host and port and username and password and database)
        except:
            raise ValueError('Unable to parse MongoDB connection %s' % mongo)
        with open(self.local_config.celery_template_file) as celery_template_file:
            data = celery_template_file.read()
            data.replace('RABBIT_CONNECTION', rabbit)
            data.replace('MONGO_HOST', host)
            data.replace('MONGO_PORT', port)
            data.replace('MONGO_USER', username)
            data.replace('MONGO_PASSWORD', password)
            data.replace('MONGO_DATABASE', database)
            data.replace('THE_CONCURRENCY', self.config.concurrency)
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
        self.cmd('apt-get -y install ffmpeg ntp glusterfs-client nfs-common x264')
        self.cmd('apt-get -y upgrade')
        self.info('Restart network time protocol service')
        self.cmd('service ntp restart')
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
        self.cmd('apt-get -y remove --purge ffmpeg glusterfs-server nfs-common x264')
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
                screen_launch('Transform',
                              ['celeryd', '--config', 'celeryconfig', '-Q', self.rabbit_queues])
            time.sleep(5)
            if screen_list('Transform', log=self.debug) == []:
                raise RuntimeError('Transform is not ready')
            else:
                self.remark('Transform successfully started')

    def hook_stop(self):
        screen_kill('Transform', log=self.debug)

    def hook_storage_relation_joined(self):
        self.storage_hook_bypass()

    def hook_storage_relation_changed(self):
        self.storage_hook_bypass()
        address = self.relation_get('private-address')
        fstype = self.relation_get('fstype')
        mountpoint = self.relation_get('mountpoint')
        options = self.relation_get('options')
        self.debug('Storage address is %s, fstype: %s, mountpoint: %s, options: %s' %
                  (address, fstype, mountpoint, options))
        if address and fstype and mountpoint:
            self.hook_stop()
            self.storage_remount(address, fstype, mountpoint, options)
            self.hook_start()
        else:
            self.remark('Waiting for complete setup')

    def hook_storage_relation_broken(self):
        self.storage_hook_bypass()
        self.hook_stop()
        self.storage_remount()

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
