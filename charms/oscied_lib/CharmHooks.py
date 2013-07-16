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

# Charmhelpers : /usr/share/pyshared/charmhelpers/__init__.py

import os, subprocess, sys, yaml
from six import string_types
import pyutils.juju as juju
from pyutils.pyutils import cmd

try:
    import charmhelpers
except ImportError:
    subprocess.check_call(['apt-add-repository', '-y', 'ppa:juju/pkgs'])
    subprocess.check_call(['apt-get', 'install', '-y', 'python-charmhelpers'])
    import charmhelpers

from shelltoolbox import command

DEFAULT_OS_ENV = {
    'APT_LISTCHANGES_FRONTEND': 'none',
    'CHARM_DIR': '/var/lib/juju/units/oscied-storage-0/charm',
    'DEBIAN_FRONTEND': 'noninteractive',
    '_JUJU_CHARM_FORMAT': '1',
    'JUJU_AGENT_SOCKET': '/var/lib/juju/units/oscied-storage-0/.juju.hookcli.sock',
    'JUJU_CLIENT_ID': 'constant',
    'JUJU_ENV_UUID': '878ca8f623174911960f6fbed84f7bdd',
    'JUJU_PYTHONPATH': ':/usr/lib/python2.7/dist-packages:/usr/lib/python2.7'
                       ':/usr/lib/python2.7/plat-x86_64-linux-gnu'
                       ':/usr/lib/python2.7/lib-tk'
                       ':/usr/lib/python2.7/lib-old'
                       ':/usr/lib/python2.7/lib-dynload'
                       ':/usr/local/lib/python2.7/dist-packages'
                       ':/usr/lib/pymodules/python2.7',
    '_': '/usr/bin/python',
    'JUJU_UNIT_NAME': 'oscied-storage/0',
    'PATH': '/usr/local/sbin:/usr/local/bin:/usr/bin:/usr/sbin:/sbin:/bin',
    'PWD': '/var/lib/juju/units/oscied-storage-0/charm',
    'SHLVL': '1'
}

__get_ip = None


def get_ip():
    global __get_ip
    if __get_ip is None:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        __get_ip = s.getsockname()[0]
        s.close()
    return __get_ip


class CharmConfig(object):

    def __init__(self):
        self.verbose = False

    def __repr__(self):
        return str(self.__dict__)


class CharmHooks(object):
    u"""
    TODO

    **Example usage**:

    >>> print('TODO')
    TODO
    """
    def __init__(self, metadata, default_config, default_os_env):
        self.config = CharmConfig()
        try:
            self.juju_ok = True
            self.juju_log = command('juju-log')
            self.load_config(charmhelpers.get_config())
            self.env_uuid = os.environ['JUJU_ENV_UUID']
            self.name = os.environ['JUJU_UNIT_NAME']
            self.private_address = charmhelpers.unit_get('private-address')
            self.public_address = charmhelpers.unit_get('public-address')
        except (subprocess.CalledProcessError, OSError):
            self.juju_ok = False
            self.juju_log = command('echo')
            if default_config is not None:
                self.load_config(default_config)
            self.env_uuid = default_os_env['JUJU_ENV_UUID']
            self.name = default_os_env['JUJU_UNIT_NAME']
            self.private_address = self.public_address = get_ip()
        self.load_metadata(metadata)

    # ----------------------------------------------------------------------------------------------

    @property
    def id(self):
        u"""
        Returns the id extracted from the unit's name.

        **Example usage**:

        >>> hooks = CharmHooks(None, None, DEFAULT_OS_ENV)
        >>> hooks.name = 'oscied-storage/3'
        >>> hooks.id
        3
        """
        return int(self.name.split('/')[1])

    @property
    def is_leader(self):
        u"""
        Returns True if current unit is the leader of the peer-relation.

        By convention, the leader is the unit with the *smallest* id (the *oldest* unit).
        """
        try:
            ids = [int(i.split('/')[1]) for i in self.relation_list(None)]
            self.debug('id=%s ids=%s' % (self.id, ids))
            return len(ids) == 0 or self.id <= min(ids)
        except Exception as e:
            self.debug('Bug during leader detection: %s' % repr(e))
            return True

    # Maps calls to charm helpers methods and replace them if called in standalone -----------------

    def log(self, message):
        if self.juju_ok:
            return charmhelpers.log(message, self.juju_log)
        print(message)
        return None

    def open_port(self, port, protocol='TCP'):
        if self.juju_ok:
            charmhelpers.open_port(port, protocol)
        else:
            self.debug('Open port %s (%s)' % (port, protocol))

    def close_port(self, port, protocol='TCP'):
        if self.juju_ok:
            charmhelpers.close_port(port, protocol)
        else:
            self.debug('Close port %s (%s)' % (port, protocol))

    def unit_get(self, attribute):
        if self.juju_ok:
            return charmhelpers.unit_get(attribute)
        raise NotImplementedError('FIXME unit_get not yet implemented')

    def relation_get(self, attribute=None, unit=None, rid=None):
        if self.juju_ok:
            return charmhelpers.relation_get(attribute, unit, rid)
        raise NotImplementedError('FIXME relation_get not yet implemented')

    def relation_ids(self, relation_name):
        if self.juju_ok:
            return [int(id) for id in charmhelpers.relation_ids(relation_name)]
        raise NotImplementedError('FIXME relation_ids not yet implemented')

    def relation_list(self, rid=None):
        if self.juju_ok:
            return charmhelpers.relation_list(rid)
        raise NotImplementedError('FIXME relation_list not yet implemented')

    def relation_set(self, **kwargs):
        if self.juju_ok:
            charmhelpers.relation_set(**kwargs)
        else:
            raise NotImplementedError('FIXME relation_set not yet implemented')

    # Convenience methods for logging --------------------------------------------------------------

    def debug(self, message):
        u"""
        Convenience method for logging a debug-related message.
        """
        if self.config.verbose:
            return self.log('[DEBUG] %s' % message)

    def info(self, message):
        u"""
        Convenience method for logging a standard message.
        """
        return self.log('[INFO] %s' % message)

    def hook(self, message):
        u"""
        Convenience method for logging the triggering of a hook.
        """
        return self.log('[HOOK] %s' % message)

    def remark(self, message):
        u"""
        Convenience method for logging an important remark.
        """
        return self.log('[REMARK] %s !' % message)

    # ----------------------------------------------------------------------------------------------

    def load_config(self, config):
        u"""
        Updates ``config`` attribute with given configuration.

        **Example usage**:

        >>> hooks = CharmHooks(None, None, DEFAULT_OS_ENV)
        >>> hasattr(hooks.config, 'pingu') or hasattr(hooks.config, 'rabbit_password')
        False
        >>> hooks.load_config({'pingu': 'bi bi'})
        >>> print(hooks.config.pingu)
        bi bi
        >>> hooks.config.verbose = True
        >>> hooks.load_config('../oscied-orchestra/config.yaml')  # doctest: +ELLIPSIS
        [DEBUG] Load config from file ../oscied-orchestra/config.yaml
        [DEBUG] Convert boolean option verbose true -> True
        >>> hasattr(hooks.config, 'rabbit_password')
        True
        """
        self.config.__dict__.update(juju.load_unit_config(config, log=self.debug))

    def save_local_config(self):
        u"""
        Save or update local configuration file only if this instance has the attribute
        ``local_config``.
        """
        if hasattr(self, 'local_config'):
            self.info('Save (updated) local configuration %s' % self.local_config)
            self.local_config.write()

    def load_metadata(self, metadata):
        u"""
        Set ``metadata`` attribute with given metadatas, ``metadata`` can be:

        * The filename of a charm metadata file (e.g. ``metadata.yaml``)
        * A dictionary containing the metadatas.

        **Example usage**:

        >>> hooks = CharmHooks(None, None, DEFAULT_OS_ENV)
        >>> hooks.metadata
        >>> hooks.load_metadata({'ensemble': 'oscied'})
        >>> hooks.metadata
        {'ensemble': 'oscied'}
        >>> hooks.config.verbose = True
        >>> hooks.load_metadata('../oscied-orchestra/metadata.yaml')  # doctest: +ELLIPSIS
        [DEBUG] Load metadatas from file ../oscied-orchestra/metadata.yaml
        >>> print(hooks.metadata['maintainer'])
        OSCIED Main Developper <david.fischer.ch@gmail.com>
        """
        if isinstance(metadata, string_types):
            self.debug('Load metadatas from file %s' % metadata)
            with open(metadata) as f:
                metadata = yaml.load(f)
        self.metadata = metadata

    # ----------------------------------------------------------------------------------------------

    def cmd(self, command, input=None, cli_input=None, fail=True):
        u"""
        Calls the ``command`` and returns a dictionary with stdout, stderr, and the returncode.

        .. seealso:: :mod:`pyutils`
        """
        return cmd(command, input=input, cli_input=cli_input, fail=fail, log=self.debug)

    def template2config(self, template, config, values):
        with open(template) as template_file:
            data = template_file.read()
            data = data.format(**values)
            with open(config, 'w') as config_file:
                config_file.write(data)
                self.remark('File %s successfully generated' % config)

    # ----------------------------------------------------------------------------------------------

    def trigger(self, hook_name=None):
        u"""
        Triggers a hook specified in ``hook_name``, defaults to ``sys.argv[1]``.

        Hook's name is the nice hook name that one can find in official juju documentation.
        For example if ``config-changed`` is mapped to a call to ``self.hook_config_changed()``.

        A ``ValueError`` containing a usage string is raised if a bad number of argument is given.
        """
        if hook_name is None:
            if len(sys.argv) != 2:
                raise ValueError('Usage %s hook_name (e.g. config-changed)' % sys.argv[0])
            hook_name = sys.argv[1]

        if self.juju_ok:
            charmhelpers.log_entry()
        try:  # Call the function hooks_...
            self.hook('Execute %s hook %s' % (self.__class__.__name__, hook_name))
            getattr(self, 'hook_%s' % hook_name.replace('-', '_'))()
            self.save_local_config()
        except subprocess.CalledProcessError as e:
            self.log('Exception caught:')
            self.log(e.output)
            raise
        finally:
            if self.juju_ok:
                charmhelpers.log_exit()

# Main ---------------------------------------------------------------------------------------------

if __name__ == '__main__':
    print('Testing CharmHooks with doctest')
    import doctest
    assert(doctest.testmod(verbose=False))
    print ('OK')
