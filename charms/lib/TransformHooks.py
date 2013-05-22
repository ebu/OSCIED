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

import os, shutil, time
from CharmHooks import CharmHooks, DEFAULT_OS_ENV
from TransformConfig import TransformConfig
from pyutils.pyutils import first_that_exist, screen_launch, screen_list, screen_kill, try_makedirs


class TransformHooks(CharmHooks):

    def __init__(self, metadata, default_config, local_config_filename, default_os_env):
        super(TransformHooks, self).__init__(metadata, default_config, default_os_env)
        self.local_config = TransformConfig.read(local_config_filename, store_filename=True)
        self.celery_config_file = 'celeryconfig.py'
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

    def storage_remount(self, address=None, fstype=None, mountpoint=None, options=None):
        if self.storage_config_is_enabled:
            self.info('Override storage parameters with charm configuration')
            address = self.config.storage_address
            nat_address = self.config.storage_nat_address
            fstype = self.config.storage_fstype
            mountpoint = self.config.storage_mountpoint
            options = self.config.storage_options
        elif address is None or fstype is None or mountpoint is None or options is None:
            return
        else:
            self.info('Use storage parameters from charm storage relation')
            nat_address = ''

        if nat_address:
            self.info('Update hosts file to map storage internal address %s to %s' %
                      (address, nat_address))
            with open('/etc/hosts', 'rw') as f:
                lines = f.readlines()
                #for line in lines:
                #    print('line %s' % line)
                #    if address in line:
            #if grep -q "$ip" /etc/hosts:
            #    sed -i "s<$nat_ip .*<$nat_ip $ip<" /etc/hosts
            #else:
            #    echo "$nat_ip $ip" >> /etc/hosts
            #else:
            #    nat_ip=$ip

        self.storage_umount()

        self.info("Mount shared storage [%s] %s:%s type %s options '%s' -> %s" % (nat_address,
                  address, mountpoint, fstype, options, self.local_config.storage_path))
        try_makedirs(self.local_config.storage_path)

        # FIXME try 5 times, a better way to handle failure
        for i in range(5):
            if self.storage_is_mounted:
                break
            self.cmd(['mount', '-t', fstype, '-o', options, '%s:%s' % (nat_address, mountpoint),
                      self.local_config.storage_path])
            time.sleep(5)

        if self.storage_is_mounted:
            # FIXME update /etc/fstab (?)
            self.info('Update configuration : Register shared storage')
            self.local_config.storage_address = address
            self.local_config.storage_fstype = fstype
            self.local_config.storage_mountpoint = mountpoint
            self.local_config.storage_options = options
        else:
            raise IOError('Unable to mount shared storage')

    def storage_umount(self):
        self.info('Update configuration : Unregister shared storage')
        self.local_config.storage_address = ''
        self.local_config.storage_fstype = ''
        self.local_config.storage_mountpoint = ''
        self.local_config.storage_options = ''
        if self.storage_is_mounted:
            # FIXME update /etc/fstab (?)
            self.info('Unmount shared storage (is actually mounted)')
            self.cmd(['umount', self.local_config.storage_path])
            self.remark('Shared storage successfully unmounted')
        else:
            self.remark('Shared storage already unmounted')

    def storage_hook_bypass(self):
        if self.storage_config_is_enabled:
            raise RuntimeError('Shared storage is set in config, storage relation is disabled')

    def transform_hook_bypass(self):
        if self.transform_config_is_enabled:
            raise RuntimeError('Orchestrator is set in config, transform relation is disabled')

    def transform_register(self):
        pass
      # Overrides transform parameters with charm configuration
      # if transform_config_is_enabled; then # if transform options are set
      #   mongo=$MONGO_CONNECTION
      #   rabbit=$RABBIT_CONNECTION
      #   socket=$API_NAT_SOCKET
      # # Or uses transform parameters from charm transform relation
      # elif [ $# -eq 2 ]; then # if function parameters are set
      #   mongo=$1
      #   rabbit=$2
      #   socket=''
      # elif [ $# -eq 0 ]; then
      #   return
      # else
      #   xecho "Usage: $(basename $0).transform_register mongo rabbit"
      # fi

      # pecho 'Configure Transform : Register the Orchestrator'
      # setSettingJSON_STRING "$CONFIG_FILE" 'mongo_connection'  "$mongo"  || xecho 'Config' 1
      # setSettingJSON_STRING "$CONFIG_FILE" 'rabbit_connection' "$rabbit" || xecho 'Config' 2
      # setSettingJSON_STRING "$CONFIG_FILE" 'api_nat_socket'    "$socket" || xecho 'Config' 3

      # host=$(expr match "$mongo" '.*mongodb://[^:]*:[^@]*@\([^:]*\):[0-9]*/[a-z]*.*')
      # port=$(expr match "$mongo" '.*mongodb://[^:]*:[^@]*@[^:]*:\([0-9]*\)/[a-z]*.*')
      # user=$(expr match "$mongo" '.*mongodb://\([^:]*\):[^@]*@[^:]*:[0-9]*/[a-z]*.*')
      # password=$(expr match "$mongo" '.*mongodb://[^:]*:\([^@]*\)@[^:]*:[0-9]*/[a-z]*.*')
      # database=$(expr match "$mongo" '.*mongodb://[^:]*:[^@]*@[^:]*:[0-9]*/\([a-z]*\).*')
      # mecho "MongoDB host=$host, port=$port, user=$user, password=$password, database=$database"
      # if [ ! "$host" -o ! "$port" -o ! "$user" -o ! "$password" -o ! "$database" ]; then
      #   xecho 'Unable to parse MongoDB connection' 3
      # fi

      # a="s<RABBIT_CONNECTION<$rabbit<g"
      # b="s<MONGO_HOST<$host<g"
      # c="s<MONGO_PORT<$port<g"
      # d="s<MONGO_USER<$user<g"
      # e="s<MONGO_PASSWORD<$password<g"
      # f="s<MONGO_DATABASE<$database<g"
      # g="s<THE_CONCURRENCY<$THE_CONCURRENCY<g"
      # sed "$a;$b;$c;$d;$e;$f;$g" "$CELERY_TEMPL_FILE" > "$CELERY_CONFIG_FILE" || xecho 'Config' 4
      # recho "Orchestrator successfully registered, it's time to wake-up"

    def transform_unregister(self):
        self.info('Update configuration : Unregister the Orchestrator')
        self.local_config.api_nat_socket = ''
        shutil.rmtree(self.celery_config_file, ignore_errors=True)
        self.remark('Orchestrator successfully unregistered')

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
        # FIXME infinite loop is used as config-changed hook !
        self.hook_stop()
        self.storage_remount()
        self.transform_register()
        self.hook_start()

    def hook_uninstall(self):
        self.info('Uninstall prerequisities')
        self.hook_stop()
        self.cmd('apt-get -y remove --purge ffmpeg glusterfs-server nfs-common x264')
        self.cmd('apt-get -y autoremove')

    def hook_start(self):
        if not self.storage_is_mounted():
            self.remark('Do not start transform daemon : No shared storage')
        if not os.path.exists(self.celery_config_file):
            self.remark('Do not start transform daemon : No celery configuration file')
        if len(self.rabbit_queues) == 0:
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
        self.info('Storage address is %s, fstype: %s, mountpoint: %s, options: %s' %
                  (address, fstype, mountpoint, options))
        if not address or not fstype or not mountpoint:
            self.remark('Waiting for complete setup')
            return
        self.hook_stop()
        self.storage_remount(address, fstype, mountpoint, options)
        self.hook_start()

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
        self.info('Orchestra address is %s, MongoDB is %s, RabbitMQ is %s' %
                  (address, mongo, rabbit))
        if not address or not mongo or not rabbit:
            self.remark('Waiting for complete setup')
            return
        self.hook_stop()
        self.transform_register(mongo, rabbit)
        self.hook_start()

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
