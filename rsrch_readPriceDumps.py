# Version 3.6.1
import requests
import json
from tia.auth import *
from tia.log import *
from datetime import datetime, timedelta

# all of the following is needed only if plotting is enabled
plot = True
symbol = 'SPY'
import tickprocessor as tickProcessorUtil
BAR_INTERVAL = 30 # In seconds
config = {
    'trade_quantity' : 50,
    'bar_interval_in_mins' : BAR_INTERVAL/60,
    'use_own_date' : False,
    'is_backtest' : True,
    'backtest_offset_days' : 5,
    'max_spread' : 0.10,
    }
_processor = tickProcessorUtil.TickProcessor(config)
# Till here

def process(quote):
    if (plot):
        _processor.process(quote['symbol'], quote, False)
    else:
        print(quote)


# Now we can read from the file
def readDump(callback = process):
    fileHandle = open('Z_OPTIONS_2021-08-13_WHOLE_DAY.txt', 'r')
    count = 0
    skipped = 0
    activate = False
    current = datetime.today() - timedelta(days=5)
    market_open_time = current.replace(hour=9, minute=30, second=0, microsecond=0)
    market_close_time = current.replace(hour=16, minute=0, second=0, microsecond=0)
    for quote in fileHandle:
        quote = json.loads(quote)
        if (quote['symbol'] == symbol):
            activate = True
        else:
            continue
        if (activate == False):
            continue
        if (quote['type'] == 'timesale'):
            tick_time = datetime.fromtimestamp(int(quote['date'])/1000)
        else:
            tick_time = datetime.fromtimestamp(int(max(quote['askdate'],quote['askdate']) )/1000)
            continue
        if ( market_open_time <= tick_time <= market_close_time):
            count += 1
            #print(quote)
            callback(quote)
    if (plot == True):
        _processor.getTickStore(symbol).getTickBars().plotBars()
    print('Count', count, ',Skipped', skipped)


#dumpAllStockQuotesToFile()
if __name__ == '__main__':
    readDump()
