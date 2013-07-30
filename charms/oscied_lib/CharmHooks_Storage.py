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

import os, time
from codecs import open
from kitchen.text.converters import to_bytes
from CharmHooks import CharmHooks
from pyutils.py_filesystem import try_makedirs


class CharmHooks_Storage(CharmHooks):

    PACKAGES = (u'glusterfs-client', u'nfs-common')

    def __init__(self, metadata, default_config, default_os_env):
        super(CharmHooks_Storage, self).__init__(metadata, default_config, default_os_env)
        self.local_config = None  # Must be set by derived class

    # ------------------------------------------------------------------------------------------------------------------

    @property
    def storage_config_is_enabled(self):
        c = self.config
        return c.storage_address and c.storage_fstype and c.storage_mountpoint

    @property
    def storage_is_mounted(self):
        return os.path.ismount(self.local_config.storage_path)

    # ------------------------------------------------------------------------------------------------------------------

    def storage_remount(self, address=None, fstype=None, mountpoint=None, options=u''):
        if self.storage_config_is_enabled:
            self.info(u'Override storage parameters with charm configuration')
            address = self.config.storage_address
            nat_address = self.config.storage_nat_address
            fstype = self.config.storage_fstype
            mountpoint = self.config.storage_mountpoint
            options = self.config.storage_options
        elif address and fstype and mountpoint:
            self.info(u'Use storage parameters from charm storage relation')
            nat_address = u''
        else:
            return
        if nat_address:
            self.info(u'Update hosts file to map storage internal address {0} to {1}'.format(address, nat_address))
            lines = filter(lambda l: nat_address not in l, open(self.local_config.hosts_file, u'r', u'utf-8'))
            lines += u'{0} {1}\n'.format(nat_address, address)
            open(self.local_config.hosts_file, u'w', u'utf-8').write(u''.join(lines))
        # Avoid unregistering and registering storage if it does not change ...
        if (address == self.local_config.storage_address and nat_address == self.local_config.storage_nat_address and
            fstype == self.local_config.storage_fstype and mountpoint == self.local_config.storage_mountpoint and
            options == self.local_config.storage_options):
            self.remark(u'Skip remount already mounted shared storage')
        else:
            self.storage_unregister()
            self.debug(u"Mount shared storage [{0}] {1}:{2} type {3} options '{4}' -> {5}".format(nat_address, address,
                       mountpoint, fstype, options, self.local_config.storage_path))
            try_makedirs(self.local_config.storage_path)
            # FIXME try X times, a better way to handle failure
            for i in range(self.local_config.storage_mount_max_retry):
                if self.storage_is_mounted:
                    break
                mount_address = u'{0}:/{1}'.format(nat_address or address, mountpoint)
                mount_path = self.local_config.storage_path
                if options:
                    self.cmd([u'mount', u'-t', fstype, u'-o', options, mount_address, mount_path])
                else:
                    self.cmd([u'mount', u'-t', fstype, mount_address, mount_path])
                time.sleep(self.local_config.storage_mount_sleep_delay)
            if self.storage_is_mounted:
                # FIXME update /etc/fstab (?)
                self.local_config.storage_address = address
                self.local_config.storage_nat_address = nat_address
                self.local_config.storage_fstype = fstype
                self.local_config.storage_mountpoint = mountpoint
                self.local_config.storage_options = options
                self.remark(u'Shared storage successfully registered')
            else:
                raise IOError(to_bytes(u'Unable to mount shared storage'))

    def storage_unregister(self):
        self.info(u'Unregister shared storage')
        self.local_config.storage_address = u''
        self.local_config.storage_fstype = u''
        self.local_config.storage_mountpoint = u''
        self.local_config.storage_options = u''
        if self.storage_is_mounted:
            # FIXME update /etc/fstab (?)
            self.remark(u'Unmount shared storage (is mounted)')
            self.cmd([u'umount', self.local_config.storage_path])
        else:
            self.remark(u'Shared storage already unmounted')

    def storage_hook_bypass(self):
        if self.storage_config_is_enabled:
            raise RuntimeError(to_bytes(u'Shared storage is set in config, storage relation is disabled'))

    # ------------------------------------------------------------------------------------------------------------------

    def hook_storage_relation_joined(self):
        self.storage_hook_bypass()

    def hook_storage_relation_changed(self):
        self.storage_hook_bypass()
        address = self.relation_get(u'private-address')
        fstype = self.relation_get(u'fstype')
        mountpoint = self.relation_get(u'mountpoint')
        options = self.relation_get(u'options')
        self.debug(u'Storage address is {0}, fstype: {1}, mountpoint: {2}, options: {3}'.format(
                   address, fstype, mountpoint, options))
        if address and fstype and mountpoint:
            self.hook_stop()
            self.storage_remount(address, fstype, mountpoint, options)
            self.hook_start()
        else:
            self.remark(u'Waiting for complete setup')

    def hook_storage_relation_broken(self):
        self.storage_hook_bypass()
        self.hook_stop()
        self.storage_remount()
