# Version 3.6.1
from datetime import datetime, timedelta
import sys
import rsrch_vwap as rsrchVWAPUtil


# find out if it ever did not touch last days VWAP
# Technically, find out how many times did SPY's MIN was lower or equal to the last day's VWAP

import pandas as pd
import plotly.express as px
pd.options.plotting.backend = "plotly"
def findPattern(symbol):
    df = rsrchVWAPUtil.dailyVWAPs(symbol, False)
    print(df)
    plot = px.scatter(x=df['DATE'], y=[ df['vwap'], df['low'], df['high']])
    plot.show()


findPattern(sys.argv[1])
