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

import subprocess
try:
    import charmhelpers
except ImportError:
    subprocess.check_call(['apt-add-repository', '-y', 'ppa:juju/pkgs'])
    subprocess.check_call(['apt-get', 'install', '-y', 'python-charmhelpers'])

import shlex
import sys
import charmhelpers  # This is not unused, this import is necessary
from shelltoolbox import command

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


class CharmHooks(object):

    def __init__(self, default_config):
        try:
            self.__dict__.update(charmhelpers.get_config())
            self.juju_ok = True
            self.unit_id = 0  # FIXME
            self.private_address = '127.0.0.1'  # FIXME
            self.juju_log = command('juju-log')
        except subprocess.CalledProcessError:
            if default_config is not None:
                self.__dict__.update(default_config)
            self.juju_ok = False
            self.unit_id = 0
            self.private_address = get_ip()
            self.juju_log = command('echo')

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

    def relation_list(self, rid=None):
        if self.juju_ok:
            return charmhelpers.relation_list
        raise NotImplementedError('FIXME relation_list not yet implemented')

    def relation_set(self, **kwargs):
        if self.juju_ok:
            charmhelpers.relation_set(kwargs)
        else:
            raise NotImplementedError('FIXME relation_set not yet implemented')

    def peer_i_am_leader(self):
        return True  # FIXME not implemented

    # Convenience methods for logging --------------------------------------------------------------

    def debug(self, message):
        u"""
        Convenience method for logging a debug-related message.
        """
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

    # A simple tool to call an external process quite easily ---------------------------------------

    def cmd(self, command, input=None, cli_input=None, fail=True):
        u"""
        Calls the ``command`` and returns a dictionary with stdout, stderr, and the returncode.

        * Pipe some content to the command with ``input``.
        * Answer to interactive CLI questions with ``cli_input``.
        * Set ``fail`` to False to avoid the exception ``subprocess.CalledProcessError``.

        **Example usage**:

        >>> hooks = CharmHooks(None)
        >>> print(hooks.cmd(['echo', 'it seem to work'])['stdout'])
        it seem to work
        <BLANKLINE>

        >>> assert(hooks.cmd('cat missing_file', fail=False)['returncode'] != 0)

        >>> hooks.cmd('my.funny.missing.script.sh')
        Traceback (most recent call last):
        ...
        OSError: [Errno 2] No such file or directory

        >>> result = hooks.cmd('cat CharmHooks.py')
        >>> print(result['stdout'].splitlines()[0])
        #!/usr/bin/env python2
        """
        args = command
        if isinstance(command, str):
            args = shlex.split(command)
        process = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        if cli_input is not None:
            process.stdin.write(cli_input)
        stdout, stderr = process.communicate(input=input)
        result = {'stdout': stdout, 'stderr': stderr, 'returncode': process.returncode}
        if fail and process.returncode != 0:
            self.debug(result)
            raise subprocess.CalledProcessError(process.returncode, command, stderr)
        return result

    # A sort of main -------------------------------------------------------------------------------

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
        except subprocess.CalledProcessError as e:
            self.log('Exception caught:')
            self.log(e.output)
            raise
        finally:
            if self.juju_ok:
                charmhelpers.log_exit()

if __name__ == '__main__':
    print('Testing CharmHooks with doctest')
    import doctest
    doctest.testmod(verbose=False)
    print ('OK')
