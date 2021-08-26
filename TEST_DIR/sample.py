import signal
import sys
import time



dt = []
pnl = []
file1 = open('/Users/vjain1/Personal/Tradier/Sandbox/Logs/2021-07-16.txt', 'r',)
for line in file1:
    if "Total PnL so far" in line:
        g = line.split()
        if (float(g[-1][1:]) == 0):
            continue
        print (g[1], g[-1][1:])
        dt.append(g[1])
        pnl.append(float(g[-1][1:]))

import plotly.graph_objects as go
import pandas as pd
import plotly.express as px

plot = px.scatter(x=dt, y=pnl)
plot.show()
#pd.options.plotting.backend = "plotly"
#df = pd.DataFrame(dict(unrealPnL=unrealizedPnL,realizedPnL=realizedPnL))
#fig = df.plot()#
#fig.show()
