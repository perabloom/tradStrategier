#import commonclass as cc
import threading, time
import time
import tickprocessor as tickProcessorUtil
import broker as brokerUtil



class A():
    def __init__(self):
        config = {
            'trade_quantity' : 10,
            'bar_interval_in_mins' : 0.5,
            'use_own_date' : False,
            'is_backtest' : True,
            'backtest_offset_days' : 1,
            'max_spread' : 0.10,
            }
        self._processor = tickProcessorUtil.TickProcessor(config)
        self._broker = brokerUtil.Broker(self._processor)
    def hndl(self, symbol):
        ac = self._broker.getAC(symbol)
        if (symbol == 'AMC'):
            print(symbol , ac.NUM_UNCLOSED_BUY_TXNS)
            ac.NUM_UNCLOSED_BUY_TXNS += 1
            time.sleep(0.1)
            if (ac.NUM_UNCLOSED_BUY_TXNS > 4):
                ac.NUM_UNCLOSED_BUY_TXNS = 1
            print(symbol)
        elif(symbol == 'TAL'):
            time.sleep(0.5)
            print(symbol, ac.NUM_UNCLOSED_BUY_TXNS)



def example():
    lst = ['AMC','TAL','SPY', 'WKHS','RIDE','TYME','CIDM']
    func = A().hndl
    while(True):
        threads = []
        for c in lst:
            t = threading.Thread(target=func,args=(c,))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()



example()
