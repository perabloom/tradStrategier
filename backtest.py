# Version 3.6.1
from tia.log import *
from datetime import datetime, timedelta
import timesale as timesale
import tickprocessor as tickprocessor
#import strategies.s_momentum as strat
import strategies.s_momentum_short_sell_profit_or_loss as strat
import trade as tradeUtil
import sys

OFFSET_IN_DAYS = int(sys.argv[2]) # How many days back from current day
BAR_INTERVAL = 0.5 # In minutes
QTY = 10

config = {
    'trade_quantity' : 50,
    'bar_interval_in_mins' : 5/60,
    'use_own_date' : False,
    'is_backtest' : True,
    'backtest_offset_days' : OFFSET_IN_DAYS,
    'max_spread' : 0.10,
    }

# CURRENT LOG LEVEL
log().setLevel("INFO")
strategy = strat.MOMENTUM_SHORT_SELL_PROFIT_OR_LOSS(config)




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



def run_backtest(symbol):
    # Critical for ANY TEST RUN
    global start_input,end_input, end
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
            strategy.hndl([tick])

            # From here on, get the corresponding broker and find out running pnL etc
            ac = strategy.getBroker().getAC(symbol)
            d = datetime.fromtimestamp(int(i['timestamp'])/1000)
            dt.append(d)
            unrealizedPnL.append(ac.positions * i['price'] - ac.cost)
            maxLoss = max(ac.cost - ac.positions * i['price'], maxLoss)
            maxCost = max(ac.cost, maxCost)
            realizedPnL.append(ac.realizedPnL)
            price.append(i['price'])
        start_input = end_input
    strategy.getProcessor().getTickStore(symbol).getTickBars().printBars()
    file1 = open('BACKTEST_RESULTS', 'a',)
    res = symbol + "OFFSET :" + str(OFFSET_IN_DAYS) +  ", UNREAL :" + str(unrealizedPnL[-1]) + ", Real :" + str(realizedPnL[-1]) + ", MAX drawdown :" + str(maxLoss) + ", maxCost: " + str(maxCost) + "\n"
    print(res)
    file1.write(res)
    file1.close()
    strategy.getProcessor().getTickStore(symbol).getTickBars().plotBars()

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



run_backtest(sys.argv[1])

'''
# USAGE
for d in 2 3 4; do for sym in "AMC" "TAL"  "WKHS" "NKLA" "RIDE"; do echo $sym $d; python3 backtest.py $sym $d; done; done;
python3 backtest.py FB 3
'''
