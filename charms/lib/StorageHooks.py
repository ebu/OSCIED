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

import glob, os, re, shutil
from CharmHooks import CharmHooks, DEFAULT_OS_ENV


class StorageHooks(CharmHooks):

    def __init__(self, metadata, default_config, default_os_env):
        super(StorageHooks, self).__init__(metadata, default_config, default_os_env)
        self.volume_flag = os.path.join(os.getcwd(), 'volume_ok')
        self.volume_infos_regex = re.compile(
            ".*Volume Name:\s*(?P<name>\S+)\s+.*Type:\s*(?P<type>\S+)\s+.*"
            "Status:\s*(?P<status>\S+)\s+.*Transport-type:\s*(?P<transport>\S+).*", re.DOTALL)

    @property
    def brick(self):
        return '%s:/exp%s' % (self.private_address, self.id)

    @property
    def volume(self):
        return 'medias_volume_%s' % self.id

    @property
    def volumes(self):
        return re.findall('Name:\s*(\S*)', self.volume_do('info', volume='')['stdout'])

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
                        (replica - len(bricks), replica, volume))
        elif len(bricks) == replica:
            self.info('Create and start a replica=%s volume %s with %s brick%s' %
                      (replica, volume, len(bricks), 's' if len(bricks) > 1 else ''))
            self.volume_do('create', volume=volume, options=extra)
            self.volume_do('start', volume=volume)
            open(self.volume_flag, 'w').close()
        else:
            vol_bricks = self.volume_infos(volume=volume)['bricks']
            self.debug('Volume bricks: %s' % vol_bricks)
            new_bricks = [b for b in bricks if b not in vol_bricks]
            if len(new_bricks) == replica:
                self.info('Expand replica=%s volume %s with new bricks' % (replica, volume))
                self.volume_do('add-brick', volume=volume, options=' '.join(new_bricks))
                self.volume_do('rebalance', volume=volume, options='start', fail=False)
            else:
                self.remark('Waiting for %s peers to expand replica=%s volume %s' %
                            (replica - len(new_bricks), replica, volume))
        self.info(self.volume_infos(volume=volume))
        self.info(self.volume_do('rebalance', volume=volume, options='status', fail=False)['stdout'])

    def volume_do(self, action, volume=None, options='', input=None, cli_input=None, fail=True):
        if volume is None:
            volume = self.volume
        return self.cmd('gluster volume %s %s %s' % (action, volume, options),
                        input=input, cli_input=cli_input, fail=fail)

    def volume_infos(self, volume=None):
        u"""
        Returns a dictionary containing informations about a volume.

        **Example output**::

            {'name': 'medias_volume_6', 'type': 'Distribute', 'status': 'Started',
             'transport': 'tcp', 'bricks': ['domU-12-31-39-06-6C-E9.compute-1.internal:/exp6']}
        """
        stdout = self.volume_do('info', volume=volume, fail=False)['stdout']
        self.debug('Volume infos stdout: %s' % repr(stdout))
        match = self.volume_infos_regex.match(stdout)
        if match:
            infos = match.groupdict()
            infos['bricks'] = re.findall('Brick[0-9]+:\s*(\S*)', stdout)
            return infos
        return None

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
        self.info('Uninstall prerequisities and remove configuration files & bricks')
        self.hook_stop()
        self.cmd('apt-get -y remove --purge glusterfs-server nfs-common')
        self.cmd('apt-get -y autoremove')
        shutil.rmtree('/etc/glusterd', ignore_errors=True)
        shutil.rmtree('/etc/glusterfs', ignore_errors=True)
        for brick in glob.glob('/exp*'):
            shutil.rmtree(brick, ignore_errors=True)
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
                self.debug(self.volume_infos())
                self.volume_do('stop', options='force', cli_input='y\n')
                self.volume_do('delete', cli_input='y\n', fail=False)  # FIXME temporary hack
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
        port = 24010
        bricks = [self.brick]
        for peer in self.relation_list():
            self.open_port(port, 'TCP')  # Open required
            bricks.append('%s:/exp%s' % (self.relation_get('private-address', peer), self.id))
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
