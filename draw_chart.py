# Version 3.6.1
from tia.log import *
from datetime import datetime, timedelta
import timesale as timesale
import tickprocessor as tickProcessorUtil
import trade as tradeUtil
import sys

OFFSET_IN_DAYS = int(sys.argv[2]) # How many days back from current day
BAR_INTERVAL = 30 # In seconds
QTY = 10

config = {
    'trade_quantity' : 50,
    'bar_interval_in_mins' : BAR_INTERVAL/60,
    'use_own_date' : False,
    'is_backtest' : True,
    'backtest_offset_days' : OFFSET_IN_DAYS,
    'max_spread' : 0.10,
    }

# CURRENT LOG LEVEL
log().setLevel("CRITICAL")

###########################################################################################################################################
##################################### DO NOT TOUCH BELOW THE FOLLOWING ##########################################################################
###########################################################################################################################################
dt = datetime.today() - timedelta(days=OFFSET_IN_DAYS)
start = datetime.now().replace(month=dt.month, day=dt.day, hour=9, minute=30,second=0,microsecond=0)
end = datetime.now().replace(month=dt.month, day=dt.day, hour=16, minute=00,second=0,microsecond=0)
print(start)
print(end)

start_input = start.strftime("%Y-%m-%d %H:%M")
end_input = end.strftime("%Y-%m-%d %H:%M")
tradeUtil.DO_NOT_TRADE = True



def run(symbol):
    # Critical for ANY TEST RUN
    global start_input,end_input, end, config
    _processor = tickProcessorUtil.TickProcessor(config)
    isOption = False
    if (len(symbol) > 13):
        isOption = True
    tradeUtil.DO_NOT_TRADE = True
    dt = []
    unrealizedPnL = []
    realizedPnL = []
    price = []
    maxLoss = 0
    maxCost = 0
    for endHour in range(10,17):
        end = end.replace(hour=endHour)
        end_input = end.strftime("%Y-%m-%d %H:%M")
        print("end_input", end_input)
        timesales = timesale.getTimeSale(symbol, start_input, end_input)['series']['data']
        for i in timesales:
            # Convert it to actual timesale format
            tick = {'symbol' : symbol, 'type' : 'timesale', 'last' : i['price'], 'size' : i['volume'], 'date' : i['timestamp'], 'bid' : i['price'], 'ask' : i['price']}
            # handle the tick here
            _processor.process(symbol, tick, isOption)
        start_input = end_input

    _processor.getTickStore(symbol).getTickBars().plotBars()

    '''
    import plotly.graph_objects as go
    import pandas as pd
    import plotly.express as px

    plot = px.scatter(x=dt, y=realizedPnL)
    plot.show()
    pd.options.plotting.backend = "plotly"
    df = pd.DataFrame(dict(unrealPnL=unrealizedPnL,realizedPnL=realizedPnL))
    fig = df.plot()
    fig.show()
    '''



run(sys.argv[1])

'''
# USAGE
for d in 2 3 4; do for sym in "AMC" "TAL"  "WKHS" "NKLA" "RIDE"; do echo $sym $d; python3 backtest.py $sym $d; done; done;
python3 backtest.py FB 3
'''
