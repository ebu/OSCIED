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

import os, subprocess, sys, yaml
from codecs import open
from kitchen.text.converters import to_bytes
from six import string_types
import pyutils.py_juju as juju
from pyutils.py_subprocess import cmd

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
