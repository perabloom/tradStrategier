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
timedelta = timedelta(weeks=12)
start_date = today - timedelta
print ("Start Date :", start_date)
hist = histUtil.getHistory("WKHS", 'daily', start_date)
hist = hist['history']['day']
high = 0.0
low = 999999.0
avg_vol = 0
idx = 1
res = []
closes = []
opens = []
CL = []
prev = None
upordown = 0
opp = 0
for h in hist:
    high = max(high, h['high'])
    low = min(low, h['low'])
    avg_vol += h['volume']
    idx +=1
    dt = datetime.strptime(h['date'], "%Y-%m-%d" )
    if ( dt == today):
        continue
    if (prev is None):
        prev = h
        continue
    prev_cl = prev['close']
    op = h['open']
    cl = h['close']
    opens.append(1 if op >= prev_cl else 0 )
    closes.append(1 if cl >= op else 0)
    print (prev_cl, op, cl)
    prev = h
    CL.append(cl)
    if ((op >= prev_cl and cl >= op) or (op <= prev_cl and cl <= prev_cl)):
        upordown += 1
    else:
        opp += 1


avg_vol = avg_vol / idx
print (avg_vol)
# Get 52 week high and low and volume


import plotly.graph_objects as go
import pandas as pd
import plotly.express as px

pd.options.plotting.backend = "plotly"
df = pd.DataFrame(dict(CLOSES=CL))
fig = df.plot()
#fig.show()

import numpy as np
print(np.corrcoef(opens,  closes))
for x , y, z in zip(opens, closes, CL):
    print (x,y,z)

print (upordown, opp)
