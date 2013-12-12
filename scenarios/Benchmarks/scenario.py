#!/usr/bin/env python
# -*- coding: utf-8 -*-

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : SCENARIOS
#
#  Project Manager : Bram Tullemans (tullemans@ebu.ch)
#  Main Developer  : Dimitri Racordon (dimitri.racordon@gmail.com)
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

import bmk_one
import bmk_two
import sys

from library.oscied_lib.juju import OsciedEnvironment
from pytoolbox.console import choice
from pytoolbox.encoding import configure_unicode

description = u'OSCIED benchmarking; composed by two scenari'

if __name__ == '__main__':
    configure_unicode()

    # get selected benchmark from console arguments or prompt user for it
    try:
        idx = sys.argv.index(u'--benchmark') + 1
        bmk = sys.argv[idx]
    except:
        bmk = choice(u'Which scenario would you like to deploy?', [u'one', u'two'])

    # deploy the selected benchmark
    if bmk == u'one':
        bmk_one.Benchmark(environments=[OsciedEnvironment(u'dev', config=bmk_one.CONFIG)]).run()
    elif bmk == u'two':
        bmk_two.Benchmark(environments=[OsciedEnvironment(u'dev', config=bmk_two.CONFIG)]).run()
    else:
        print(u'unknown benchmark name: {0}'.format(bmk))
