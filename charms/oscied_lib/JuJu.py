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

import yaml
from pyutils.pyutils import cmd


def juju_do(command, environment, options=None):
    # FIXME issue #61 - https://github.com/ebu/OSCIED/issues/61
    command = ['juju', command, '--environment', environment]
    if isinstance(options, list):
        command.extend(options)
    result = cmd(command, fail=False)
    if result['returncode'] != 0:
        raise RuntimeError('Subprocess failed %s : %s.' % (' '.join(command), result['stderr']))
    return yaml.load(result['stdout'])


def add_units(environment, service, num_units):
    return juju_do('add-unit', environment, ['--num-units', str(num_units), service])


def deploy_units(environment, service, num_units, config=None, constraints=None, local=False,
                 release=None, repository=None):
    options = ['--num-units', num_units]
    if config is not None:
        options.extend(['--config', config])
    if constraints is not None:
        options.extend(['--constraints', constraints])
    if release is not None:
        service = '%s/%s' % (release, service)
    if local:
        service = 'local:%s' % service
    if repository is not None:
        options.extend(['--repository', repository])


def get_unit(environment, service, number):
    name = '%s/%s' % (service, number)
    return juju_do('status', environment, [name])['services'][service]['units'][name]


def remove_unit(environment, service, number):
    name = '%s/%s' % (service, number)
    return juju_do('remove-unit', environment, [name])


def get_units(environment, service):
    units = {}
    try:
        units_dict = juju_do('status', environment, [service])['services'][service]['units']
    except KeyError:
        return {}
    for unit in units_dict.iteritems():
        number = unit[0].split('/')[1]
        units[number] = unit[1]
    return units


def get_units_count(environment, service):
    try:
        return len(juju_do('status', environment, [service])['services'][service]['units'].keys())
    except KeyError:
        return 0


def add_or_deploy_units(environment, service, num_units, **kwargs):
    if get_units_count() == 0:
        deploy_units(environment, service, num_units, **kwargs)
    else:
        add_units(environment, service, num_units)
