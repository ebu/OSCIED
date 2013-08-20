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

import sys
from os.path import abspath, dirname, join
sys.path.append(abspath(dirname(dirname(__file__))))
sys.path.append(abspath(join(dirname(dirname(__file__)), u'pyutils')))

from nose.tools import assert_equal
from oscied_lib.oscied_client import CRUDMapper


class TestCRUDMapper(object):

    def setup(self):
        self.mapper = CRUDMapper(None, 'http://test.com:5000', None, id_prefix='id')

    def test_mapper_without_environment(self):
        self.mapper.environment = None
        assert_equal(self.mapper.get_url(), u'http://test.com:5000')
        assert_equal(self.mapper.get_url(extra='/extra_value'), u'http://test.com:5000/extra_value')
        assert_equal(self.mapper.get_url(index='index_value'), u'http://test.com:5000/id/index_value')
        assert_equal(self.mapper.get_url(index='index_value', extra='/extra_value'),
                     u'http://test.com:5000/id/index_value/extra_value')

    def test_mapper_with_environment(self):
        self.mapper.environment = 'maas'
        assert_equal(self.mapper.get_url(), u'http://test.com:5000/environment/maas')
        assert_equal(self.mapper.get_url(extra='/extra_value'), u'http://test.com:5000/environment/maas/extra_value')
        assert_equal(self.mapper.get_url(index='index_value'), u'http://test.com:5000/environment/maas/id/index_value')
        assert_equal(self.mapper.get_url(index='index_value', extra='/extra_value'),
                     u'http://test.com:5000/environment/maas/id/index_value/extra_value')

if __name__ == u'__main__':
    import nose
    nose.runmodule(argv=[__file__], exit=False)
