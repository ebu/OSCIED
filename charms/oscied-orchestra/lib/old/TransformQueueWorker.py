#! /usr/bin/env python
# -*- coding: utf-8 -*-

#**************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : ORCHESTRA
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

import puka, time, uuid

from TransformJob import TransformJob
from TransformAck import TransformAck

class TransformQueueWorker:

#    """
#    @throws puka.spec_exceptions.ResourceLocked
#    """
    def __init__(self, rabbit_url):
        # connect to our message broker : RabbitMQ
        self.client = puka.Client(rabbit_url)
        promise = self.client.connect()
        self.client.wait(promise)
        # FIXME : exclusive=True -> puka.spec_exceptions.ResourceLocked
        # declare the transformation queue
        promise = self.client.queue_declare(queue='transform_queue', durable=True)
        self.transform_queue = self.client.wait(promise)['queue']
        # declare the transformation callback queue
        promise = self.client.queue_declare(queue='transform_callback_queue', durable=True)
        self.callback_queue = self.client.wait(promise)['queue']

    def receive_transform_sync(self):
        print ' [*] Waiting for messages. To exit press CTRL+C'
        consume_promise = self.client.basic_consume(queue=self.transform_queue, prefetch_count=1)
        while True:
            msg_result = self.client.wait(consume_promise)
            print " [x] Received %r" % (msg_result['body'],)
            body=msg_result['body']
            time.sleep( body.count('.') )
            print " [x] Done"
            # FIXME do encoding or don't acknowledge the message
            self.client.basic_ack(msg_result)
            # FIXME return msg_result

    def send_callback_sync(self, transform_ack):
        # parameters validation
        if not isinstance(transform_ack, TransformAck):
            raise TypeError('transform_ack is not an instance of TransformAck')
        # send acknowledge to callback queue
        promise = self.client.basic_publish(exchange='',
                                            routing_key=self.callback_queue,
                                            body=transform_ack.json(),
                                            headers={'delivery_mode': 2})
        self.client.wait(promise)
        self.client.close()

# --------------------------------------------------------------------------------------------------

if __name__ == '__main__':
    print 'Create transformation queue worker :'
    queue = TransformQueueWorker("amqp://guest:Alice_in_wonderland@localhost/")
    print 'Receive a transformation job :'
    job = TransformJob.load(queue.receive_transform_sync())
    print job.json()
