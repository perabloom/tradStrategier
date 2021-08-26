# Version 3.6.1

from tia_utils_internal import *
import tickstore as tickStore
from tia.log import *


class TickProcessor:
    def __init__(self,config):
        log().debug( "TickProcessor Inited")
        self._config = config
        self._map = {} # TickStore


    # processes the tick by adding it to the corresponding tickstore
    def process(self, symbol, tick, isOption):
        if symbol not in self._map:
            self._map[symbol] = tickStore.TickStore(symbol, self._config)
        self._map[symbol].add(tick, isOption)

    # Returns the corresponding TickStore object
    def getTickStore(self, symbol):
        #print ("getting map for ", symbol , self._map.keys())
        return self._map[symbol]

def example():
    a = TickProcessor({'bar_interval_in_mins' : 0.5, 'backtest_offset_days' : 0, 'use_own_date' : False})
    a.process("WISH", {'last' : 32, 'symbol' : "WISH",'type' :'quote', 'biddate' : '1624913021000', 'askdate' : '1624913021000'})
    print(a.getTickStore("WISH").getLatestQuote())
    a.process("WKHS", {'last' : 89, 'symbol' : "WKSH",'type' :'quote', 'biddate' : '1624913022000', 'askdate' : '1624953021000'})
    print(a.getTickStore("WISH").getLatestQuote())

#example()
