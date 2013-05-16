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

import subprocess
try:
    import charmhelpers
except ImportError:
    subprocess.check_call(['apt-add-repository', '-y', 'ppa:juju/pkgs'])
    subprocess.check_call(['apt-get', 'install', '-y', 'python-charmhelpers'])

from charmhelpers import log, log_entry, log_exit
from shelltoolbox import command


def logd(message, juju_log=command('juju-log')):
    return log('[DEBUG] %s !' % message, juju_log)


def logm(message, juju_log=command('juju-log')):
    return log('[MESSAGE] %s' % message, juju_log)


def logp(message, juju_log=command('juju-log')):
    return log('[PARAGRAPH] %s' % message, juju_log)


def logr(message, juju_log=command('juju-log')):
    return log('[REMARK] %s !' % message, juju_log)


def logt(message, juju_log=command('juju-log')):
    return log('[TITLE] %s' % message, juju_log)


def peer_i_am_leader():
    return True  # FIXME not implemented


def main(hook_name):
    log_entry()
    try:
        hook_name()
    except subprocess.CalledProcessError as e:
        log('Exception caught:')
        log(e.output)
        raise
    finally:
        log_exit()
