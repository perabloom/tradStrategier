# Version 3.6.1
import time
import requests
import json
from tia.log import *


log().warning("HAHAHAasdfasdfasdfadsHAH")
log().setLevel("ERROR")


c0 = time.perf_counter()
c1 = time.perf_counter()
spend2 = c1 - c0
print("perf_counter() time I: {}s".format(spend2))
c0 = time.perf_counter()
from datetime import datetime
d = 1625600212160
dt = datetime.fromtimestamp(int(d/1000))
dt = dt.replace(microsecond=1000*(d%1000))
dt = dt.strftime("%H:%M:%S.%f")
print(dt)
#log.critical('VISHAL IT IS')
log().critical(dt + 'Watch out!')

log().info('Watch out!')
log().debug('Watch out!')
log().error('Watch out!')

c1 = time.perf_counter()
spend2 = c1 - c0
print("perf_counter() time II: {}s".format(spend2))

time.sleep(1)
