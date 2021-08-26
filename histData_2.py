# Version 3.6.1
import requests
import json
from tia.log import *
from tia.auth import *
from datetime import datetime, date, timedelta
import quote as quoteUtil
import history as histUtil


today = date.today()
today = datetime(year=today.year,month=today.month,day=today.day,)
timedelta = timedelta(weeks=26)
start_date = today - timedelta
print ("Start Date :", start_date)
hist = histUtil.getHistory("WISH", 'daily', start_date)
hist = hist['history']['day']
high = 0.0
low = 999999.0
avg_vol = 0
idx = 1
res = []
closes = []
gems = []
for h in hist:
    high = max(high, h['high'])
    low = min(low, h['low'])
    avg_vol += h['volume']
    idx +=1
    dt = datetime.strptime(h['date'], "%Y-%m-%d" )
    if ( dt == today):
        continue
    op = h['open']
    h['high'] = h['high'] * 100 / op
    h['low'] = h['low'] * 100 / op
    h['close'] = h['close'] * 100 / op
    h['open'] = h['open'] * 100 / op
    gem = ( (h['high']- h['low'] ) * h['close']) / h['open']
    gems.append(gem)
    closes.append(h['close'])
    res.append(h)
    print (h)
    print (gem)
print (len(res))
avg_vol = avg_vol / idx
print (avg_vol)
# Get 52 week high and low and volume


import plotly.graph_objects as go
import pandas as pd
import plotly.express as px

pd.options.plotting.backend = "plotly"
df = pd.DataFrame(dict(GEM=gems[0:-1],CLOSES=closes[1:]))
fig = df.plot()
fig.show()

import numpy as np
print(np.corrcoef(gems[0:-1],  closes[1:]))
