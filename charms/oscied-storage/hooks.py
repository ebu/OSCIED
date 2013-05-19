#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : STORAGE
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

import os, re, shutil
from lib.CharmHooks import CharmHooks, DEFAULT_OS_ENV


class StorageHooks(CharmHooks):

    def __init__(self, metadata, default_config, default_os_env):
        super(StorageHooks, self).__init__(metadata, default_config, default_os_env)
        self.volume_flag = os.path.join(os.getcwd(), 'volume_ok')

    @property
    def brick(self):
        return '%s:/exp%s' % (self.private_address, self.id)

    @property
    def volume(self):
        return 'medias_volume_%s' % self.id

    @property
    def volume_bricks(self):
        return re.findall('Brick[0-9]+:\s*(\S*)',
                          self.cmd('gluster volume info %s' % self.volume)['stdout'])

    @property
    def volumes(self):
        return re.findall('Name:\s*(\S*)', self.cmd('gluster volume info')['stdout'])

    # ----------------------------------------------------------------------------------------------

    def peer_probe(self, peer_address, fail=True):
        return self.cmd('gluster peer probe %s' % peer_address)

    def volume_create_or_expand(self, volume=None, bricks=None, replica=None):
        if volume is None:
            volume = self.volume
        if bricks is None:
            bricks = [self.brick]
        if replica is None:
            replica = self.config.replica_count
        extra = (' ' if replica == 1 else ' replica %s transport tcp ' % replica) + ' '.join(bricks)
        if len(bricks) < replica:
            self.remark("Waiting for %s peers to create and start a replica=%s volume %s" %
                        (replica - 1, replica, volume))
        elif len(bricks) == replica:
            self.info('Create and start a replica=%s volume %s with %s brick%s' %
                      (replica, volume, len(bricks), 's' if len(bricks) > 1 else ''))
            self.volume_do('create', volume=volume, options=extra)
            self.volume_do('start', volume=volume)
            open(self.volume_flag, 'w').close()
        elif len(bricks) % replica == 0:
            self.info('Expand replica=%s volume %s with new bricks' % (replica, volume))
            vol_bricks = self.volume_bricks
            self.debug('Volume bricks: %s' % vol_bricks)
            for brick in bricks:  # FIXME remove bricks with set remove ...
                if brick not in vol_bricks:
                    self.info('Add brick %s to volume %s' % (brick, volume))
                    self.volume_do('add-brick', volume=volume, options=brick)
            self.volume_do('rebalance', volume=volume)
        print(self.volume_do('info')['stdout'])

    def volume_do(self, action, volume=None, options='', input=None, cli_input=None, fail=True):
        if volume is None:
            volume = self.volume
        return self.cmd('gluster volume %s %s %s' % (action, volume, options),
                        input=input, cli_input=cli_input, fail=fail)

    # ----------------------------------------------------------------------------------------------

    def hook_install(self):
        self.hook_uninstall()
        self.info('Install prerequisities and upgrade packages')
        self.cmd('apt-get -y install ntp glusterfs-server nfs-common')
        self.cmd('apt-get -y upgrade')
        self.info('Restart network time protocol service')
        self.cmd('service ntp restart')

        # Create medias volume if it is already possible to do so
        self.volume_create_or_expand()

        self.info('Expose GlusterFS Server service')
        self.open_port(111, 'TCP')     # For portmapper, and should have both TCP and UDP open
        self.open_port(24007, 'TCP')   # For the Gluster Daemon
        #open_port(24008, 'TCP')  # Infiniband management (optional unless you are using IB)
        self.open_port(24009, 'TCP')   # We have only 1 storage brick (24009-24009)
        #open_port(38465, 'TCP')  # For NFS (not used)
        #open_port(38466, 'TCP')  # For NFS (not used)
        #open_port(38467, 'TCP')  # For NFS (not used)

    def hook_uninstall(self):
        self.info('Remove prerequisities and created files/folders')
        self.hook_stop()
        self.cmd('apt-get -y remove --purge glusterfs-server nfs-common')
        self.cmd('apt-get -y autoremove')
        shutil.rmtree('/etc/glusterd', ignore_errors=True)
        shutil.rmtree('/etc/glusterfs', ignore_errors=True)
        shutil.rmtree('/exp1', ignore_errors=True)
        try:
            os.remove(self.volume_flag)
        except OSError:
            pass

    def hook_start(self):
        if self.cmd('pgrep glusterd', fail=False)['returncode'] != 0:
            self.cmd('service glusterfs-server start')

    def hook_stop(self):
        if self.cmd('pgrep glusterd', fail=False)['returncode'] == 0:
            self.cmd('service glusterfs-server stop')

    def hook_storage_relation_joined(self):
        # Send file-system type, mount point & options only if volume is created and started
        if os.path.exists(self.volume_flag):
            self.relation_set(fstype='glusterfs', mountpoint=self.volume, options='')
        else:
            self.relation_set(fstype='', mountpoint='', options='')

    def hook_peer_relation_joined(self):
        if not self.is_leader:
            self.info('As slave, stop and delete my own volume %s' % self.volume)
            if self.volume in self.volumes:
                self.volume_do('stop', options='force', cli_input='y\n')
                self.volume_do('delete', cli_input='y\n')
                os.remove(self.volume_flag)

    def hook_peer_relation_changed(self):
        # Get configuration from the relation
        peer_address = self.relation_get('private-address')
        self.info('Peer address is %s' % peer_address)
        if not peer_address:
            self.remark('Waiting for complete setup')
            return

        # FIXME close previously opened ports if some bricks leaved ...
        self.info('Open required ports')
        port = 24009
        bricks = [self.brick]
        for peer in self.relation_list():
            self.open_port(port, 'TCP')  # Open required
            peer_address = self.relation_get('private-address', peer)
            bricks.append('%s:/exp%s' % (peer_address, self.id))
            port += 1

        if self.is_leader:
            self.info('As leader, probe remote peer %s and create or expand volume %s' %
                      (peer_address, self.volume))
            self.peer_probe(peer_address)
            self.volume_create_or_expand(bricks=bricks)

    def hook_peer_relation_broken(self):
        self.remark('FIXME NOT IMPLEMENTED')

if __name__ == '__main__':
    StorageHooks('metadata.yaml', 'config.yaml', DEFAULT_OS_ENV).trigger()
