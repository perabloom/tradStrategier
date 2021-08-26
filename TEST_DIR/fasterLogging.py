# Version 3.6.1
import time
import requests
import json
from tia.log import Log
from queue import *


class EvictQueue(Queue):
    def __init__(self, maxsize):
        self.discarded = 0
        super().__init__(maxsize)

    def put(self, item, block=False, timeout=None):
        while True:
            try:
                super().put(item, block=False)
            except queue.Full:
                try:
                    self.get_nowait()
                    self.discarded += 1
                except queue.Empty:
                    pass

def speed_up_logs():
    log = Log().log()
    rootLogger = log
    log_que = EvictQueue(1000)
    print (log.handlers)
    queue_handler = log.handlers.QueueHandler(log_que)
    queue_listener = logging.handlers.QueueListener(log_que, *rootLogger.handlers)
    queue_listener.start()
    rootLogger.handlers = [queue_handler]

speed_up_logs()


log = Log().log()
c0 = time.perf_counter()
#checkOrder(9793486)
#getOrdersIdsWithState('cancelled')
log.warning('Watch out!')
log.critical('VISHAL IT IS')
log.warning('Watch out!')
log.warning('Watch out!')
log.warning('Watch out!')
log.warning('Watch out!')
log.info('Watch out!')
log.debug('Watch out!')

c1 = time.perf_counter()
spend2 = c1 - c0
print("perf_counter() time: {}s".format(spend2))
time.sleep(3)
