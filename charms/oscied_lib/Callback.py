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

from __future__ import absolute_import

import requests
from urlparse import urlparse, ParseResult
from pyutils.pyutils import json2object, object2json


class Callback(object):

    def __init__(self, url, username, password):
        self.url = url
        self.username = username
        self.password = password

    def is_valid(self, raise_exception):
        # FIXME check fields
        return True

    def replace_netloc(self, netloc):
        url = urlparse(self.url)
        url = ParseResult(url.scheme, netloc, url.path, url.params, url.query, url.fragment)
        self.url = url.geturl()

    def post(self, data_json):
#       return requests.post(self.url, data_json, auth=(self.username, self.password))
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        return requests.post(self.url, headers=headers, data=data_json,
                             auth=(self.username, self.password))

    @staticmethod
    def load(json):
        callback = Callback(None, None, None)
        json2object(json, callback)
        return callback

CALLBACK_TEST = Callback('http://127.0.0.1:5000/media', 'toto', '1234')

# --------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    print object2json(CALLBACK_TEST, True)
    CALLBACK_TEST.is_valid(True)
    print CALLBACK_TEST.url
    CALLBACK_TEST.replace_netloc('129.194.185.47:5003')
    assert CALLBACK_TEST.url == 'http://129.194.185.47:5003/media'
    print str(Callback.load(object2json(CALLBACK_TEST, False)))
