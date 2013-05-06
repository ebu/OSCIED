#!/bin/bash

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : SCRIPTS
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

import sys
from celery.task.control import inspect
import lib.Transform
#from celery.task.sets import TaskSet
from lib.Media import MEDIA_TEST
from lib.TransformProfile import TRANSFORM_PROFILE_TEST
from lib.User import USER_TEST

#def make_pi_tasks():
#    taskset = TaskSet(lib.Publisher.make_pi.subtask((x, )) for x in NUM_CALCS)
#    print "Dispatching tasks"
#    taskset_result = taskset.apply_async()
#    print "Waiting for results"
#    results = taskset_result.join_native()
#    print "Results:"
#    for i in results:
#        print i

raise ValueError('FIXME issue #6')

if __name__ == '__main__':
    user = USER_TEST
    media_in = MEDIA_TEST
    media_out = MEDIA_TEST
    profile = TRANSFORM_PROFILE_TEST
    print 'Launch the transform job'
    result = lib.Transform.transform_job.apply_async(
        args=(user.json(), media_in.json(), media_out.json(), profile.json(),),
        queue='transform_private')
    print result.state
    print result
    i = inspect()
    dump = i.active()
    print dump
    if dump:
        for worker, tasks in dump.iteritems():
            print worker
            for task in tasks:
                if task['name'] == 'Transform.transform_job':
                    for key, value in task.iteritems():
                        print 'key ' + key + ' = ' + str(value)
                    #print 'THE Task ' + str(task)
                    #print 'Arguments ' + str(task['args'])
                    print 'salut'

    sys.exit(0)
#    make_pi_tasks()
