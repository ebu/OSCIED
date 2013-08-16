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

from CharmConfig import CharmConfig


class CharmConfig_Subordinate(CharmConfig):

    def __init__(self, verbose=None, api_nat_socket=u'', celery_config_file=u'celeryconfig.py',
                 celery_template_file=u'templates/celeryconfig.py.template', **kwargs):
        super(CharmConfig_Subordinate, self).__init__(verbose=verbose)
        self.api_nat_socket = api_nat_socket
        self.celery_config_file = celery_config_file
        self.celery_template_file = celery_template_file
