# Version 3.6.1
import time
from logbook import Logger, StreamHandler
from logbook.queues import ZeroMQHandler


import sys

#StreamHandler(sys.stdout).push_application()
addr='tcp://127.0.0.1:5053'
handler = ZeroMQHandler(addr)
handler.push_application()
log = Logger('A Fancy Name')
c0 = time.perf_counter()
#checkOrder(9793486)
#getOrdersIdsWithState('cancelled')
log.warn('Watch out!')
log.critical('VISHAL IT IS')
log.warn('Watch out!')
log.warn('Watch out!')
log.warn('Watch out!')
log.warn('Watch out!')
log.info('Watch out!')
log.debug('Watch out!')




c1 = time.perf_counter()
spend2 = c1 - c0
print("perf_counter() time: {}s".format(spend2))

time.sleep(3)
