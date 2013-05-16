#!/usr/bin/env python2
# -*- coding: utf-8 -*-

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : ORCHESTRA
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

import puka, sys
from TransformJob import TransformJob

class TransformQueueClient:

    def __init__(self, rabbit_url):
        # connect to our message broker : RabbitMQ
        self.client = puka.Client(rabbit_url)
        promise = self.client.connect()
        self.client.wait(promise)
        # declare the transformation queue
        promise = self.client.queue_declare(queue='transform_queue', durable=True)
        self.transform_queue = self.client.wait(promise)['queue']
        # declare the transformation callback queue
        promise = self.client.queue_declare(queue='transform_callback_queue', durable=True)
        self.callback_queue = self.client.wait(promise)['queue']

    def send_transform_sync(self, transform_job):
        # parameters validation
        if not isinstance(transform_job, TransformJob):
            raise TypeError('transform_job is not an instance of TransformJob')
        # send job to transformation queue
        promise = self.client.basic_publish(exchange='', routing_key=self.transform_queue, body=transform_job.json(), headers={'delivery_mode': 2})
        self.client.wait(promise)
        self.client.close()

# --------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    print 'Create transformation queue client :'
    queue = TransformQueueClient("amqp://guest:Alice_in_wonderland@localhost/")
    print 'Send a transformation job :'
    job = TransformJob(None, 'http://in', 'http://out')
    print job.json()
    queue.send_transform_sync(job)
