#!/usr/bin/env python
# -*- coding: utf-8 -*-

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : COMMON LIBRARY
#
#  Project Manager : Bram Tullemans (tullemans@ebu.ch)
#  Main Developer  : David Fischer (david.fischer.ch@gmail.com)
#  Copyright       : Copyright (c) 2012-2013 EBU. All rights reserved.
#
#**********************************************************************************************************************#
#
# This file is part of EBU Technology & Innovation OSCIED Project.
#
# This project is free software: you can redistribute it and/or modify it under the terms of the EUPL v. 1.1 as provided
# by the European Commission. This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the European Union Public License for more details.
#
# You should have received a copy of the EUPL General Public License along with this project.
# If not, see he EUPL licence v1.1 is available in 22 languages:
#     22-07-2013, <https://joinup.ec.europa.eu/software/page/eupl/licence-eupl>
#
# Retrieved from https://github.com/ebu/OSCIED

ENVIRONMENT_TO_LABEL = {u'amazon': u'Public Cloud', u'maas': u'Private Cluster'}
ENVIRONMENT_TO_TYPE  = {u'amazon': u'public', u'maas': u'private'}
SERVICE_TO_LABEL     = {u'oscied-transform': u'encoding',        u'oscied-publisher': u'distribution'}
SERVICE_TO_UNITS_API = {u'oscied-transform': u'transform_units', u'oscied-publisher': u'publisher_units'}
SERVICE_TO_TASKS_API = {u'oscied-transform': u'transform_tasks', u'oscied-publisher': u'publisher_tasks'}
