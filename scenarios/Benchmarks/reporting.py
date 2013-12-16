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

from library.oscied_lib.models import TransformTask

try:
    import paya.history, paya.reporting
    import argparse, os, pygal, yaml
except:
    cmd(u'pip install git+git://github.com/kyouko-taiga/paya.git[chart]#egg=paya')
    import paya.history, paya.reporting

class TaskStatusReport(object):

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
        chart = pygal.StackedBar()
        chart.title = 'Number of tasks per status every 2 minutes'
        chart.x_labels = [t0.strftime('%y/%m/%d, %H:%m:%S')]
        for status, chart_data in status_count.iteritems():
            if sum(chart_data):
                chart.add(status, [c for i,c in enumerate(chart_data) if i % (120 // interval) == 0])

        if file: chart.render_to_file(file)
        else:    return chart.render()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate a chart reports for tasks monitoring.')
    parser.add_argument('--status-history', help='a task status history')
    parser.add_argument('--activity-history', action='append', help='an activity history')
    parser.add_argument('--activity-profile', help='a yaml file with an activity profile')
    parser.add_argument('--outdir', default=os.getcwd(), help='output directory of generated charts')
    parser.add_argument('--prefix', help='filename prefix of generated charts')
    args = parser.parse_args()

    def _filename(name):
        return args.outdir + args.prefix + name if args.prefix else args.outdir + name

    if args.status_history:
        print('generating chart for tasks status...')
        tsr = TaskStatusReport(paya.history.FileHistory(args.status_history))
        tsr.chart_task_status(file=_filename('status.svg'))

    if args.activity_history:
        if args.activity_profile:
            with open(args.activity_profile, 'r') as f:
                profile = paya.reporting.ActivityProfile(yaml.load(f))
        else: profile = paya.reporting.ActivityProfile()

        mac = paya.reporting.MultiActivityReport(profile=profile)
        for h in args.activity_history:
            mac.add(os.path.basename(h), paya.history.FileHistory(h))

        #if profile['process.number']:
        #    print('generating chart for process number...')
        #    mac.chart_process_number(file=_filename('process-number.svg'))
        #if profile['cpu.times']:
        #    print('generating chart for cpu times..')
        #    mac.chart_cpu_times(file=_filename('cpu-times.svg'))
        #if profile['vmem']:
        #    print('generating chart for virtual memory...')
        #    mac.chart_vmem(file=_filename('vmem.svg'))
        #if profile['swap']:
        #    print('generating chart for swap memory...')
        #    mac.chart_swap(file=_filename('swap.svg'))
        #if profile['disk.usage']:
        #    print('generating chart for disk usage...')
        #    mac.chart_disk_usage(file=_filename('disk-usage.svg'), mount='/')
        if profile['disk.io_counters']:
            print('generating chart for disk io counters...')
            mac.chart_disk_io_counters(file=_filename('disk-io-counters.svg'), counter='write_bytes')
        if profile['network.io_counters']:
            print('generating chart for network io counters...')
            mac.chart_network_io_counters(file=_filename('network-io-counters.svg'), counter='bytes_sent')
