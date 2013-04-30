#! /usr/bin/env python
# -*- coding: utf-8 -*-

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : COMMON LIBRARY
#
#  Authors   : David Fischer
#  Contact   : david.fischer.ch@gmail.com / david.fischer@hesge.ch
#  Project   : OSCIED (OS Cloud Infrastructure for Encoding and Distribution)
#  Copyright : 2012 OSCIED Team. All rights reserved.
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
# Retrieved from:
#   svn co https://claire-et-david.dyndns.org/prog/OSCIED

import datetime
import inspect
from ipaddr import IPAddress
import json
import logging
import logging.handlers
import re
import uuid
from bson.json_util import dumps, loads


class ForbiddenError(Exception):
    pass


def datetime_now():
    return datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


## http://stackoverflow.com/questions/6255387/mongodb-object-serialized-as-json
class SmartJSONEncoderV1(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, '__dict__'):
            return obj.__dict__
        return super(SmartJSONEncoderV1, self).default(obj)


class SmartJSONEncoderV2(json.JSONEncoder):
    def default(self, obj):
        attributes = {}
        for a in inspect.getmembers(obj):
            if inspect.isroutine(a[1]) or inspect.isbuiltin(a[1]) or a[0].startswith('__'):
                continue
            attributes[a[0]] = a[1]
        return attributes


def json2object(json, something):
    something.__dict__ = loads(json)


def jsonfile2object(filename, something):
    something.__dict__ = json.load(open(filename))


def object2json(something, include_properties):
    if not include_properties:
        return dumps(something, cls=SmartJSONEncoderV1)
    else:
        return dumps(something, cls=SmartJSONEncoderV2)


def duration2secs(duration):
    hours, minutes, seconds = duration.split(':')
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)


def valid_mail(mail):
    try:
        return re.match(r'[^@]+@[^@]+\.[^@]+', mail)
    except:
        return False


def valid_filename(filename):
    try:
        return re.match(r'[^\.]+\.[^\.]+', filename)
    except:
        return False


def valid_secret(secret):
    try:
        return re.match(r'[A-Za-z0-9@#$%^&+=]{8,}', secret)
    except:
        return False


def valid_ip(ip):
    try:
        IPAddress(ip)
        return True
    except:
        return False


def valid_port(port):
    if not port:
        return False
    return True  # FIXME TODO


def valid_uuid(id, none_allowed):
    if not id and none_allowed:
        return True
    try:
        uuid.UUID('{' + str(id) + '}')
    except ValueError:
        return False
    return True


def setup_logging(filename, level, format='%(asctime)s %(levelname)-8s - %(message)s',
                  datefmt='%d/%m/%Y %H:%M:%S'):
    logging.basicConfig(filename=filename, level=level, format=format, datefmt=datefmt)
    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(logging.Formatter(format))
    logging.getLogger('').addHandler(console)

UUID_ZERO = str(uuid.UUID('{00000000-0000-0000-0000-000000000000}'))
