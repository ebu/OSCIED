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

from library.oscied_lib.models import TransformTask

try:
    import paya.history, paya.reporting
    import pygal
except:
    cmd(u'pip install git+git://github.com/kyouko-taiga/paya.git[chart]#egg=paya')
    import paya.history, paya.reporting

class TaskReport(object):

    def __init__(self, history):
        self.history = history

    def chart_task_status(self, file=None):
        # find history interval
        g  = iter(self.history)
        t0 = paya.reporting.iso_to_datetime(g.next())
        t1 = paya.reporting.iso_to_datetime(g.next())
        interval = round((t1 - t0).total_seconds())
        
        # generate chart data
        status_count = {unicode(s): [0 for _ in self.history] for s in TransformTask.ALL_STATUS}
        for i, (_, tasks) in enumerate(self.history.iteritems()):
            for _, task in tasks.iteritems():
                status_count[unicode(task['status'])][i] += 1

        # create graph
        chart = pygal.Line()
        chart.title = 'Number of tasks per status every {0} second(s)'.format(interval)
        chart.x_labels = [t0.strftime('%y/%m/%d, %H:%m:%S')]
        for status, chart_data in status_count.iteritems():
            if sum(chart_data):
                chart.add(status, chart_data)

        if file: chart.render_to_file(file)
        else:    return chart.render()
