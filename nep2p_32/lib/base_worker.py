import gevent
import gevent.queue
import gevent.socket
from util.config import *

class base_worker(object):
    def __init__(self):
        self.pkt_queue = gevent.queue.Queue(0)
        gevent.spawn(self._recvfrom_pkt_queue)
        gevent.spawn(self.regular)
    
    def _recvfrom_pkt_queue(self):
        while True:
            try:
                pkt = self.pkt_queue.get()
                self.process_queue_pkt(pkt)
            except gevent.queue.Empty:
                pass
            gevent.sleep(REGULAR_INTERVAL)
    
    def process_queue_pkt(self, pkt):
        raise NotImplementedError('I am abstract')

    def regular(self):
        while True:
            self.regular_action()
            gevent.sleep(REGULAR_INTERVAL)

    def regular_action(self):
        raise NotImplementedError('I am abstract')
