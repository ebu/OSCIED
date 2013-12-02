#!/usr/bin/env python
# -*- coding: utf-8 -*-

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : SCENARIOS
#
#  Project Manager : Bram Tullemans (tullemans@ebu.ch)
#  Main Developer  : David Fischer (david.fischer.ch@gmail.com)
#  Co-Developer    : Dimitri Racordon (dimitri.racordon@gmail.com)
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

import benchmark_one
import benchmark_two

from pytoolbox.encoding import configure_unicode

description = u'OSCIED benchmarking; composed by two scenari'

def choice(question='', choices=[]):
    u"""
    Prompt the user for a choice and return his/her answer.
    
    **Example of usage**
    
    >>choice('What is your favorite color?', ['blue', 'orange', 'red'])
    What is your favourite color? [blue, orange, red]: orange
    orange
    >>choice(['male', 'female'])
    [male, female]? male
    male
    """

    # generate question and choices list
    choices_list = ''.join(s + ', ' for s in choices).rstrip(', ')
    if question is None:
        question = u'[{0}]? '.format(choices_list)
    else:
        question = u'{0} [{1}]: '.format(question, choices_list)

    # loop until an acceptable choice has been answered
    while True:
        ans = raw_input(question)
        if ans in choices:
            return ans
        print(u'Please choose between {0}.'.format(choices_list)) 

if __name__ == '__main__':
    configure_unicode()
    bmk = choice('Which scenario would you like to deploy?', ['one', 'two'])
    if scenario == 'one':
        bmk_one.Benchmark().main(environments=[OsciedEnvironment(u'benchmark', config=CONFIG)])
    elif scenario == 'two':
        bmk_two.Benchmark().main(environments=[OsciedEnvironment(u'benchmark', config=CONFIG)])
