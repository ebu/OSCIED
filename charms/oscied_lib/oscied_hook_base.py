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

# Charmhelpers : /usr/share/pyshared/charmhelpers/__init__.py

import os, pymongo.uri_parser, shutil, subprocess, sys, time, yaml
from codecs import open
from kitchen.text.converters import to_bytes
from six import string_types
import pyutils.py_juju as juju
from pyutils.py_filesystem import try_makedirs
from pyutils.py_subprocess import cmd, screen_launch, screen_list, screen_kill


try:
    import charmhelpers
except ImportError:
    subprocess.check_call([u'apt-add-repository', u'-y', u'ppa:juju/pkgs'])
    subprocess.check_call([u'apt-get', u'update'])
    subprocess.check_call([u'apt-get', u'install', u'-y', u'python-charmhelpers'])
    import charmhelpers

from shelltoolbox import command

DEFAULT_OS_ENV = {
    u'APT_LISTCHANGES_FRONTEND': u'none',
    u'CHARM_DIR': u'/var/lib/juju/units/oscied-storage-0/charm',
    u'DEBIAN_FRONTEND': u'noninteractive',
    u'_JUJU_CHARM_FORMAT': u'1',
    u'JUJU_AGENT_SOCKET': u'/var/lib/juju/units/oscied-storage-0/.juju.hookcli.sock',
    u'JUJU_CLIENT_ID': u'constant',
    u'JUJU_ENV_UUID': u'878ca8f623174911960f6fbed84f7bdd',
    u'JUJU_PYTHONPATH': u':/usr/lib/python2.7/dist-packages:/usr/lib/python2.7'
                        u':/usr/lib/python2.7/plat-x86_64-linux-gnu'
                        u':/usr/lib/python2.7/lib-tk'
                        u':/usr/lib/python2.7/lib-old'
                        u':/usr/lib/python2.7/lib-dynload'
                        u':/usr/local/lib/python2.7/dist-packages'
                        u':/usr/lib/pymodules/python2.7',
    u'_': u'/usr/bin/python',
    u'JUJU_UNIT_NAME': u'oscied-storage/0',
    u'PATH': u'/usr/local/sbin:/usr/local/bin:/usr/bin:/usr/sbin:/sbin:/bin',
    u'PWD': u'/var/lib/juju/units/oscied-storage-0/charm',
    u'SHLVL': u'1'
}

__get_ip = None


def get_ip():
    global __get_ip
    if __get_ip is None:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect((u'8.8.8.8', 80))
        __get_ip = s.getsockname()[0]
        s.close()
    return __get_ip


class CharmConfig(object):

    def __init__(self):
        self.verbose = False

    def __repr__(self):
        return unicode(self.__dict__)


class CharmHooks(object):
    u"""
    TODO

    **Example usage**:

    >>> print(u'TODO')
    TODO
    """
    def __init__(self, metadata, default_config, default_os_env):
        self.config = CharmConfig()
        try:
            self.juju_ok = True
            self.juju_log = command(u'juju-log')
            self.load_config(charmhelpers.get_config())
            self.env_uuid = os.environ.get(u'JUJU_ENV_UUID')
            self.name = os.environ[u'JUJU_UNIT_NAME']
            self.private_address = charmhelpers.unit_get(u'private-address')
            self.public_address = charmhelpers.unit_get(u'public-address')
        except (subprocess.CalledProcessError, OSError):
            self.juju_ok = False
            self.juju_log = command(u'echo')
            if default_config is not None:
                self.load_config(default_config)
            self.env_uuid = default_os_env[u'JUJU_ENV_UUID']
            self.name = default_os_env[u'JUJU_UNIT_NAME']
            self.private_address = self.public_address = get_ip()
        self.load_metadata(metadata)

    # ------------------------------------------------------------------------------------------------------------------

    @property
    def id(self):
        u"""
        Returns the id extracted from the unit's name.

        **Example usage**:

        >>> hooks = CharmHooks(None, None, DEFAULT_OS_ENV)
        >>> hooks.name = u'oscied-storage/3'
        >>> hooks.id
        3
        """
        return int(self.name.split(u'/')[1])

    @property
    def is_leader(self):
        u"""
        Returns True if current unit is the leader of the peer-relation.

        By convention, the leader is the unit with the *smallest* id (the *oldest* unit).
        """
        try:
            ids = [int(i.split(u'/')[1]) for i in self.relation_list(None)]
            self.debug(u'id={0} ids={1}'.format(self.id, ids))
            return len(ids) == 0 or self.id <= min(ids)
        except Exception as e:
            self.debug(u'Bug during leader detection: {0}'.format(repr(e)))
            return True

    # Maps calls to charm helpers methods and replace them if called in standalone -------------------------------------

    def log(self, message):
        if self.juju_ok:
            return charmhelpers.log(message, self.juju_log)
        print(message)
        return None

    def open_port(self, port, protocol=u'TCP'):
        if self.juju_ok:
            charmhelpers.open_port(port, protocol)
        else:
            self.debug(u'Open port {0} ({1})'.format(port, protocol))

    def close_port(self, port, protocol=u'TCP'):
        if self.juju_ok:
            charmhelpers.close_port(port, protocol)
        else:
            self.debug(u'Close port {0} ({1})'.format(port, protocol))

    def unit_get(self, attribute):
        if self.juju_ok:
            return charmhelpers.unit_get(attribute)
        raise NotImplementedError(to_bytes(u'FIXME unit_get not yet implemented'))

    def relation_get(self, attribute=None, unit=None, rid=None):
        if self.juju_ok:
            return charmhelpers.relation_get(attribute, unit, rid)
        raise NotImplementedError(to_bytes(u'FIXME relation_get not yet implemented'))

    def relation_ids(self, relation_name):
        if self.juju_ok:
            return [int(id) for id in charmhelpers.relation_ids(relation_name)]
        raise NotImplementedError(to_bytes(u'FIXME relation_ids not yet implemented'))

    def relation_list(self, rid=None):
        if self.juju_ok:
            return charmhelpers.relation_list(rid)
        raise NotImplementedError(to_bytes(u'FIXME relation_list not yet implemented'))

    def relation_set(self, **kwargs):
        if self.juju_ok:
            charmhelpers.relation_set(**kwargs)
        else:
            raise NotImplementedError(to_bytes(u'FIXME relation_set not yet implemented'))

    # Convenience methods for logging ----------------------------------------------------------------------------------

    def debug(self, message):
        u"""
        Convenience method for logging a debug-related message.
        """
        if self.config.verbose:
            return self.log(u'[DEBUG] {0}'.format(message))

    def info(self, message):
        u"""
        Convenience method for logging a standard message.
        """
        return self.log(u'[INFO] {0}'.format(message))

    def hook(self, message):
        u"""
        Convenience method for logging the triggering of a hook.
        """
        return self.log(u'[HOOK] {0}'.format(message))

    def remark(self, message):
        u"""
        Convenience method for logging an important remark.
        """
        return self.log(u'[REMARK] {0} !'.format(message))

    # ------------------------------------------------------------------------------------------------------------------

    def load_config(self, config):
        u"""
        Updates ``config`` attribute with given configuration.

        **Example usage**:

        >>> hooks = CharmHooks(None, None, DEFAULT_OS_ENV)
        >>> hasattr(hooks.config, u'pingu') or hasattr(hooks.config, u'rabbit_password')
        False
        >>> hooks.load_config({u'pingu': u'bi bi'})
        >>> print(hooks.config.pingu)
        bi bi
        >>> hooks.config.verbose = True
        >>> hooks.load_config(u'../oscied-orchestra/config.yaml')  # doctest: +ELLIPSIS
        [DEBUG] Load config from file ../oscied-orchestra/config.yaml
        [DEBUG] Convert boolean option verbose true -> True
        >>> hasattr(hooks.config, u'rabbit_password')
        True
        """
        self.config.__dict__.update(juju.load_unit_config(config, log=self.debug))

    def save_local_config(self):
        u"""
        Save or update local configuration file only if this instance has the attribute
        ``local_config``.
        """
        if hasattr(self, u'local_config'):
            self.debug(u'Save (updated) local configuration {0}'.format(self.local_config))
            self.local_config.write()

    def load_metadata(self, metadata):
        u"""
        Set ``metadata`` attribute with given metadatas, ``metadata`` can be:

        * The filename of a charm metadata file (e.g. ``metadata.yaml``)
        * A dictionary containing the metadatas.

        **Example usage**:

        >>> hooks = CharmHooks(None, None, DEFAULT_OS_ENV)
        >>> hooks.metadata
        >>> hooks.load_metadata({u'ensemble': u'oscied'})
        >>> hooks.metadata
        {u'ensemble': u'oscied'}
        >>> hooks.config.verbose = True
        >>> hooks.load_metadata(u'../oscied-orchestra/metadata.yaml')  # doctest: +ELLIPSIS
        [DEBUG] Load metadatas from file ../oscied-orchestra/metadata.yaml
        >>> print(hooks.metadata[u'maintainer'])
        OSCIED Main Developper <david.fischer.ch@gmail.com>
        """
        if isinstance(metadata, string_types):
            self.debug(u'Load metadatas from file {0}'.format(metadata))
            with open(metadata, u'r', u'utf-8') as f:
                metadata = yaml.load(f)
        self.metadata = metadata

    # ------------------------------------------------------------------------------------------------------------------

    def cmd(self, command, input=None, cli_input=None, fail=True):
        u"""
        Calls the ``command`` and returns a dictionary with stdout, stderr, and the returncode.

        .. seealso:: :mod:`pyutils`
        """
        return cmd(command, input=input, cli_input=cli_input, fail=fail, log=self.debug)

    def template2config(self, template, config, values):
        with open(template, u'r', u'utf-8') as template_file:
            data = template_file.read()
            data = data.format(**values)
            with open(config, u'w', u'utf-8') as config_file:
                config_file.write(data)
                self.remark(u'File {0} successfully generated'.format(config))

    # ------------------------------------------------------------------------------------------------------------------

    def trigger(self, hook_name=None):
        u"""
        Triggers a hook specified in ``hook_name``, defaults to ``sys.argv[1]``.

        Hook's name is the nice hook name that one can find in official juju documentation.
        For example if ``config-changed`` is mapped to a call to ``self.hook_config_changed()``.

        A ``ValueError`` containing a usage string is raised if a bad number of argument is given.
        """
        if hook_name is None:
            if len(sys.argv) != 2:
                raise ValueError(to_bytes(u'Usage {0} hook_name (e.g. config-changed)'.format(sys.argv[0])))
            hook_name = sys.argv[1]

        if self.juju_ok:
            charmhelpers.log_entry()
        try:  # Call the function hooks_...
            self.hook(u'Execute {0} hook {1}'.format(self.__class__.__name__, hook_name))
            getattr(self, u'hook_{0}'.format(hook_name.replace(u'-', u'_')))()
            self.save_local_config()
        except subprocess.CalledProcessError as e:
            self.log(u'Exception caught:')
            self.log(e.output)
            raise
        finally:
            if self.juju_ok:
                charmhelpers.log_exit()


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


class CharmHooks_Subordinate(CharmHooks):

    PACKAGES = ()

    def __init__(self, metadata, default_config, default_os_env):
        super(CharmHooks_Subordinate, self).__init__(metadata, default_config, default_os_env)
        self.local_config = None  # Must be set by derived class

    # ------------------------------------------------------------------------------------------------------------------

    @property
    def screen_name(self):
        return self.__class__.__name__.lower().replace('hooks', '')

    @property
    def rabbit_hostname(self):
        return u'{0}_{1}'.format(self.screen_name, self.public_address)

    @property
    def rabbit_queues(self):
        return u','.join([self.config.rabbit_queues, self.rabbit_hostname])

    @property
    def subordinate_config_is_enabled(self):
        return self.config.mongo_connection and self.config.rabbit_connection

    # ------------------------------------------------------------------------------------------------------------------

    def subordinate_register(self, mongo=None, rabbit=None):
        if self.subordinate_config_is_enabled:
            self.info(u'Override subordinate parameters with charm configuration')
            mongo = self.config.mongo_connection
            rabbit = self.config.rabbit_connection
            socket = self.config.api_nat_socket
        elif mongo and rabbit:
            self.info(u'Use subordinate parameters from charm relation')
            socket = u''
        else:
            return
        self.info(u'Register the Orchestrator')
        self.local_config.api_nat_socket = socket
        try:
            infos = pymongo.uri_parser.parse_uri(mongo)
            assert(len(infos[u'nodelist']) == 1)
            infos[u'host'], infos[u'port'] = infos[u'nodelist'][0]
            infos[u'rabbit'], infos[u'concurrency'] = rabbit, self.config.concurrency
            del infos[u'nodelist']
            assert(infos[u'host'] and infos[u'port'] and infos[u'username'] and infos[u'password'] and
                   infos[u'database'])
        except:
            raise ValueError(to_bytes(u'Unable to parse MongoDB connection {0}'.format(mongo)))
        self.template2config(self.local_config.celery_template_file, self.local_config.celery_config_file, infos)
        self.remark(u'Orchestrator successfully registered')

    def subordinate_unregister(self):
        self.info(u'Unregister the Orchestrator')
        self.local_config.api_nat_socket = u''
        shutil.rmtree(self.local_config.celery_config_file, ignore_errors=True)

    def subordinate_hook_bypass(self):
        if self.subordinate_config_is_enabled:
            raise RuntimeError(to_bytes(u'Orchestrator is set in config, subordinate relation is disabled'))

    def start_celeryd(self, retry_count=15, retry_delay=1):
        if screen_list(self.screen_name, log=self.debug) == []:
            screen_launch(self.screen_name, [u'celeryd', u'--config', u'celeryconfig',
                                             u'--hostname', self.rabbit_hostname, u'-Q', self.rabbit_queues])
        for start_delay in range(retry_count):
            time.sleep(retry_delay)
            if screen_list(self.screen_name, log=self.debug) != []:
                start_time = start_delay * retry_delay
                self.remark(u'{0} successfully started in {1} seconds'.format(self.screen_name, start_time))
                return
        raise RuntimeError(to_bytes(u'Worker {0} is not ready'.format(self.screen_name)))

    def stop_celeryd(self):
        screen_kill(self.screen_name, log=self.debug)

    # ------------------------------------------------------------------------------------------------------------------

    def hook_subordinate_relation_joined(self):
        self.subordinate_hook_bypass()

    def hook_subordinate_relation_changed(self):
        self.subordinate_hook_bypass()
        address = self.relation_get(u'private-address')
        mongo = self.relation_get(u'mongo_connection')
        rabbit = self.relation_get(u'rabbit_connection')
        self.debug(u'Orchestra address is {0}, MongoDB is {1}, RabbitMQ is {2}'.format(address, mongo, rabbit))
        if address and mongo and rabbit:
            self.hook_stop()
            self.subordinate_register(mongo, rabbit)
            self.hook_start()
        else:
            self.remark(u'Waiting for complete setup')

    def hook_subordinate_relation_broken(self):
        self.subordinate_hook_bypass()
        self.hook_stop()
        self.subordinate_unregister()


class CharmHooks_Website(CharmHooks):

    PACKAGES = ()

    def __init__(self, metadata, default_config, default_os_env):
        super(CharmHooks_Website, self).__init__(metadata, default_config, default_os_env)
        self.local_config = None  # Must be set by derived class

    # ------------------------------------------------------------------------------------------------------------------

    @property
    def proxy_ips_string(self):
        try:
            proxy_ips = self.config.proxy_ips.split(u',')
        except:
            proxy_ips = [self.config.proxy_ips]
        return u','.join(list(filter(None, self.local_config.proxy_ips + proxy_ips)))

    # ------------------------------------------------------------------------------------------------------------------

    def hook_website_relation_joined(self):
        self.relation_set(port=u'80', hostname=self.cmd(u'hostname -f'))

    def hook_website_relation_changed(self):
        # Get configuration from the relation
        proxy_address = self.relation_get(u'private-address')
        self.info(u'Proxy address is {0}'.format(proxy_address))
        if not proxy_address:
            self.remark(u'Waiting for complete setup')
        elif not proxy_address in self.local_config.proxy_ips:
            self.info(u'Add {0} to allowed proxy IPs'.format(proxy_address))
            self.hook_stop()
            self.local_config.proxy_ips.append(proxy_address)
            self.save_local_config()
            self.hook_config_changed()
            self.hook_start()

    def hook_website_relation_departed(self):
        # Get configuration from the relation
        proxy_address = self.relation_get(u'private-address')
        if not proxy_address:
            self.remark(u'Waiting for complete setup')
        elif proxy_address in self.local_config.proxy_ips:
            self.info(u'Remove {0} from allowed proxy IPs'.format(proxy_address))
            self.hook_stop()
            self.local_config.proxy_ips.remove(proxy_address)
            self.save_local_config()
            self.hook_config_changed()
            self.hook_start()

    def hook_website_relation_broken(self):
        self.info(u'Cleanup allowed proxy IPs')
        self.hook_stop()
        self.local_config.proxy_ips = []
        self.hook_config_changed()
        self.hook_start()
