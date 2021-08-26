# Version 3.6.1
import requests
import json
from tia.auth import *
from tia.log import *
from datetime import datetime, timedelta


f = open('VOL_STOCKS', 'r')

dt = {'under_5' : 0, 'under_10' : 0, 'under_15'  : 0, 'under_20' : 0, 'under_30' : 0, 'over_30' : 0}

for line in f:
    quote = json.loads(line)
    if (quote['average_volume'] is None or quote['average_volume'] == 0):
        continue
    if (quote['average_volume'] > 10000000 and  quote['per_interval_moves_pct'] >= 1 ):
        print(quote, "\n")
    if (quote['last'] <= 5):
        dt['under_5'] += 1
    elif (quote['last'] <= 10):
        dt['under_10'] += 1
    elif (quote['last'] <= 15):
        dt['under_15'] += 1
    elif (quote['last'] <= 20):
        dt['under_20'] += 1
    elif (quote['last'] <= 30):
        dt['under_30'] += 1
    else:
        dt['over_30'] += 1
print(dt)
