# Version 3.6.1
import requests
from tia.auth import *
from tia.log import *
import trade as tradeUtil
import orders as orderUtil
import positions as positionUtil
import timesaleMoves as timesaleMovesUtil
import dailyMoves as dailyMovesUtil
from datetime import datetime


#NOTES - 0.04:0.12 ( W:L) at 15 seconds was best for NKLA and BB on 30th June 2020 ( before 10:45 am)
class AC:
    def __init__(self, symbol):
        self.symbol = symbol
        self.DAILY_MAX_PCT_CHANGE = None
        self.MAX_SPREAD = 0.01
        self.MAX_LOSS = 0.06
        self.BUY_ON_DIFF = 0.06
        self.WIN = 0.09
        self.DAILY_ALPHA_PCT = -1
        self.INTRA_PCT = -1
        self.canAct = False
        self.hasPosition = False
        self.positions = 0
        self.cost = 0
        self.NUM_UNCLOSED_BUY_TXNS = 0 # NUMBER OF UNCLOSED BUY TRANSACTIONS
        self.NUM_BUY_SELL_LOOPS = 0 # TOTAL Number of opened and finally closed txns
        self.realizedPnL = 0
        self.lastLimitsUpdate = None # WIN LOSS LIMITS UPDATE
        self.buyFlag = False # This is imp, if this is on, that means the security will be bought overriding everything!
        self.sellAllFlag = False # This is imp too, if this is on, the security will be sold
        self.stopTrading = False # IF THIS FLAG IS True, algo won't trade in this stock
        self.LAST_LOOP_STATE = None # none indicates there was not a single loop yet
        self.NUM_TIMES_UNSCATHED = 0 # Indicates number of times we came out unscathed

    def getPosition(self):
        return self.positions

    def getAvgPrice(self):
        return self.cost / max(1,self.positions)

    def getRealizedPnL(self):
        return self.realizedPnL

    def getUnrealizedPnL(self, currentPrice):
        return currentPrice * self.positions - self.cost

    def checkAndResetBuyFlag(self):
        res = self.buyFlag
        self.buyFlag = False
        return res

    def checkAndResetSellAllFlag(self):
        res = self.sellAllFlag
        self.sellAllFlag = False
        return res

class Broker():
    def __init__(self, tickProcessor = None):
        log().debug("INITING BROKER")
        self._symbolMap = {}
        self._tickProcessor = tickProcessor

    def getAC(self, symbol):
        if (symbol in self._symbolMap):
            return self._symbolMap[symbol]
        else:
            self._symbolMap[symbol] = AC(symbol)
            self.checkAndSetACLimits(symbol)
            self.setDailyMaxPctChange(symbol)
            return self._symbolMap[symbol]

    def getSymbolMap(self):
        return self._symbolMap

    def setDailyMaxPctChange(self, symbol):
        ac = self.getAC(symbol)
        ac.DAILY_MAX_PCT_CHANGE = dailyMovesUtil.printHistory(symbol, 10) / 100

    def checkAndSetACLimits(self, symbol):
        ac = self.getAC(symbol)
        if (ac.lastLimitsUpdate is None) :
            try:
                # get moves for first 10 minutes
                # in future, adjust these moves as we migrate from one 10 mins band to another ?
                moves = timesaleMovesUtil.movement1m(symbol, 0, 10)
                ac.WIN = moves['per_interval_moves']/2
                ac.MAX_LOSS = moves['daily_avg_moves']/5
                ac.DAILY_ALPHA_PCT = moves['daily_avg_moves_pct']
                ac.INTRA_PCT = moves['per_interval_moves_pct']
                log().info (symbol + " (WIN, LOSS) limit set to : (" + "{:.3f}".format(ac.WIN) + ","  + "{:.3f}".format(ac.MAX_LOSS) + ")"  + " DAILY_ALPHA_PCT :" + "{:3f}".format(ac.DAILY_ALPHA_PCT)  + " INTRA_PCT : " + "{:3f}".format(ac.INTRA_PCT)   )
            except Exception as e:
                log().critical("*********************CRITICAL : Failed to set limits for " + str(symbol) + " " + str(e))
            ac.lastLimitsUpdate = datetime.now()

    def updateACAutoLimits(self, symbol, minsSinceOpen, durationInMins):
        ac = self.getAC(symbol)
        now = datetime.now()
        ac.lastLimitsUpdate = now
        try:
            # get moves for first 10 minutes
            # in future, adjust these moves as we migrate from one 10 mins band to another ?
            moves = timesaleMovesUtil.movement1m(symbol, minsSinceOpen, durationInMins)
            ac.WIN = moves['per_interval_moves']/2
            ac.MAX_LOSS = moves['daily_avg_moves']/5
            ac.DAILY_ALPHA_PCT = moves['daily_avg_moves_pct']
            ac.INTRA_PCT = moves['per_interval_moves_pct']
            log().info (symbol + " (WIN, LOSS) limit set to : (" + "{:.3f}".format(ac.WIN) + ","  + "{:.3f}".format(ac.MAX_LOSS) + ")"  + " DAILY_ALPHA_PCT :" + "{:3f}".format(ac.DAILY_ALPHA_PCT)  + " INTRA_PCT : " + "{:3f}".format(ac.INTRA_PCT)   )
        except Exception as e:
            log().critical("*********************CRITICAL : Failed to set limits for " + str(symbol) + " " + str(e))


    def getLimitsForSymbol(self, symbol):
        ac = self.getAC(symbol)
        if (ac.lastLimitsUpdate is None):
            return None
        alpha = 1 - self.getAC(symbol).DAILY_ALPHA_PCT/200
        delta = self.getAC(symbol).INTRA_PCT/200
        M = ( 1 - alpha * ( 1 + delta) ) / (alpha * delta )
        return {"SYMBOL" : symbol, "WIN" : ac.WIN, "MAX_LOSS" : ac.MAX_LOSS, "DAILY_ALPHA_PCT" : ac.DAILY_ALPHA_PCT, "INTRA_PCT" : ac.INTRA_PCT, "M" : M }

    def getLimits(self):
        res = []
        for sym in self._symbolMap.keys():
            val = self.getLimitsForSymbol(sym)
            if (val is not None):
                res.append(val)
        return res

    def enableBuy(self, symbol):
        ac = self.getAC(symbol)
        ac.buyFlag = True
        log().info("Enabling Buy for " + str(symbol))

    def enableSellAll(self, symbol):
        ac = self.getAC(symbol)
        ac.sellAllFlag = True
        log().info("Enabling Sell ALL for " + str(symbol))

    def isTradingStopped(self, symbol):
        ac = self.getAC(symbol)
        return ac.stopTrading

    def stopTrading(self, symbol):
        ac = self.getAC(symbol)
        ac.stopTrading = True
        log().info("Stopped Trading for " + str(symbol))


    # Checks if it can be bought now, resets the value to False after the check
    def isBuyNow(self, symbol):
        ac = self.getAC(symbol)
        return ac.checkAndResetBuyFlag()


    def getAllOrders(self):
        return orderUtil.getAllOrders()

    def getAllOrdersIdsWithState(self,state):
        return orderUtil.getOrdersIdsWithState(state)

    def checkOrder(self,order_id):
        return orderUtil.checkOrder(order_id)

    def getOrdersIdsWithStateForSymbol(self,state, symbol):
        return orderUtil.getOrdersIdsWithStateForSymbol(state, symbol)

    def sendLimitOrder(self, asset_type, symbol, side, quantity, price, order_type, duration, tag):
        order_id = tradeUtil.sendOrder(asset_type, symbol, side, quantity, price, order_type, duration, tag)
        if symbol not in self._symbolMap:
            self._symbolMap[symbol] = {'sentLimitOrders' : 0, 'pendingOrderIds' : set()}
        self._symbolMap[symbol]['sentLimitOrders'] += 1
        self._symbolMap[symbol]['pendingOrderIds'].add(order_id)

    def sendMarketOrder(self, asset_type, symbol, side, quantity, duration, tag):
        tradeUtil.sendMarketOrder(asset_type, symbol, side, quantity, duration, tag)
        if symbol not in self._symbolMap:
            self._symbolMap[symbol] = {'sentMarketOrders' : 0}
        self._symbolMap[symbol]['sentMarketOrders'] += 1

    def cancelOrder(self,order_id):
        tradeUtil.cancelOrder(order_id)
        self._symbolMap[symbol]['sentLimitOrders'] -= 1
        self._symbolMap[symbol]['pendingOrderIDs'].remove(order_id)

    def getPositions(self,symbol):
        positionUtil.getPositions(symbol)

    def buy(self,symbol, expectedPrice, quantity, assetType = 'EQUITY'):
        if (len(symbol) > 13):
            tradeUtil.sendOptionsMarketOrder('OPTION', symbol, 'buy_to_open', quantity, 'day', symbol, expectedPrice)
        else:
            tradeUtil.sendMarketOrder(assetType, symbol, 'buy', quantity, 'day', symbol, expectedPrice)
        ac = self.getAC(symbol)
        ac.hasPosition = True
        ac.positions += quantity
        ac.cost += quantity * expectedPrice
        ac.NUM_UNCLOSED_BUY_TXNS += 1

    def sellToClose(self, symbol, expectedPrice, assetType = 'EQUITY'):
        ac = self.getAC(symbol)
        if (len(symbol) > 13):
            tradeUtil.sendOptionsMarketOrder('OPTION', symbol, 'sell_to_close', ac.positions, 'day', symbol, expectedPrice)
        else:
            tradeUtil.sendMarketOrder(assetType, symbol, 'sell', ac.positions, 'day', symbol, expectedPrice)
        ac.hasPosition = False
        ac.realizedPnL += ac.positions * expectedPrice - ac.cost
        ac.positions = 0
        ac.cost = 0
        ac.NUM_UNCLOSED_BUY_TXNS = 0
        ac.NUM_BUY_SELL_LOOPS  += 1

    def sell(self,symbol, expectedPrice, quantity, assetType = 'EQUITY'):
        if (len(symbol) > 13):
            tradeUtil.sendOptionsMarketOrder('OPTION', symbol, 'sell_to_close', quantity, 'day', symbol, expectedPrice)
        else:
            tradeUtil.sendMarketOrder(assetType, symbol, 'sell', quantity, 'day', symbol, expectedPrice)
        ac = self.getAC(symbol)
        remainingQty = int(ac.positions) - int(quantity)
        ac.hasPosition =  True if remainingQty > 0 else False
        ac.positions -= quantity
        ac.cost -= quantity * expectedPrice
        if (remainingQty == 0):
            ac.NUM_UNCLOSED_BUY_TXNS = 0
            ac.NUM_BUY_SELL_LOOPS  += 1

    def sellShort(self,symbol, expectedPrice, quantity, assetType = 'EQUITY'):
        if (len(symbol) > 13):
            tradeUtil.sendOptionsMarketOrder('OPTION', symbol, 'sell_to_open', quantity, 'day', symbol, expectedPrice)
        else:
            tradeUtil.sendMarketOrder(assetType, symbol, 'sell_short', quantity, 'day', symbol, expectedPrice)
        ac = self.getAC(symbol)
        ac.hasPosition = True
        ac.positions += (-quantity)
        ac.cost += (-quantity) * expectedPrice
        ac.NUM_UNCLOSED_BUY_TXNS += 1


    def buyToCover(self,symbol, expectedPrice, assetType = 'EQUITY'):
        ac = self.getAC(symbol)
        quantity = -ac.positions
        if (len(symbol) > 13):
            tradeUtil.sendOptionsMarketOrder('OPTION', symbol, 'buy_to_close', quantity, 'day', symbol, expectedPrice)
        else:
            tradeUtil.sendMarketOrder(assetType, symbol, 'buy_to_cover', quantity, 'day', symbol, expectedPrice)
        ac.hasPosition = False
        ac.realizedPnL += ac.positions * expectedPrice - ac.cost
        ac.positions = 0
        ac.cost = 0
        ac.NUM_UNCLOSED_BUY_TXNS = 0
        ac.NUM_BUY_SELL_LOOPS  += 1


    def printPnLForSymbol(self, symbol):
        realized = self.getAC(symbol).getRealizedPnL()
        print (symbol , "Realized : ", realized)
        if (self._tickProcessor is not None):
            tickStore = self._tickProcessor.getTickStore(symbol)
            quote = tickStore.getLatestQuote()
            if (quote is not None):
                last = quote['bid']
                unrealized = self.getAC(symbol).getUnrealizedPnL(last)
                print (symbol, "Unrealized : ", "{:.3f}".format(unrealized))
                print (symbol, "Last Ask :", last)
        print(symbol, "Position : ", self.getAC(symbol).positions)
        print(symbol, "Avg Price : ", "{:.3f}".format(self.getAC(symbol).cost/max(self.getAC(symbol).positions, 1)))
        print("\n")

    def printPnL(self):
        totalRealized = 0
        totalUnrealized = 0
        for symbol in self._symbolMap.keys():
            realized = self.getAC(symbol).getRealizedPnL()
            totalRealized += realized
            print (symbol , "Realized : ", "{:.3f}".format(realized))
            if ( self._tickProcessor is not None):
                tickStore = self._tickProcessor.getTickStore(symbol)
                quote = tickStore.getLatestQuote()
                if (quote is not None):
                    last = quote['bid']
                    unrealized = self.getAC(symbol).getUnrealizedPnL(last)
                    print (symbol, "Unrealized : ", "{:.3f}".format(unrealized))
                    print (symbol, "Last Ask :", last)
                    totalUnrealized += unrealized
            print(symbol, "Position : ", self.getAC(symbol).positions)
            print(symbol, "Avg Price : ", "{:.3f}".format(self.getAC(symbol).cost/max(self.getAC(symbol).positions, 1)), "\n" )
        print ("\n**** TOTAL REALIZED :",totalRealized, " ** Total UnRealized :", "{:.3f}".format(totalUnrealized), "\n")

    def getTotalPnLSoFar(self):
        totalRealized = 0
        totalUnrealized = 0
        for symbol in self._symbolMap.keys():
            realized = self.getAC(symbol).getRealizedPnL()
            totalRealized += realized
            tickStore = self._tickProcessor.getTickStore(symbol)
            quote = tickStore.getLatestQuote()
            if (quote is not None):
                last = quote['bid']
                unrealized = self.getAC(symbol).getUnrealizedPnL(last)
                totalUnrealized += unrealized
            else:
                log().critical ("ERROR : QUOTE IS NONE for " + str(symbol))
        return totalRealized + totalUnrealized

    def logPnL(self):
        totalRealized = 0
        totalUnrealized = 0
        totalCost = 0
        for symbol in self._symbolMap.keys():
            prefix = "logPnL " + symbol
            realized = self.getAC(symbol).getRealizedPnL()
            totalRealized += realized
            log().info(prefix + " Realized : " + "{:.3f}".format(realized))
            if ( self._tickProcessor is not None):
                tickStore = self._tickProcessor.getTickStore(symbol)
                quote = tickStore.getLatestQuote()
                if (quote is not None):
                    last = quote['bid']
                    unrealized = self.getAC(symbol).getUnrealizedPnL(last)
                    log().info(prefix + " Unrealized : " + " {:.3f}".format(unrealized))
                    log().info(prefix + " Last Ask : " + str(last))
                    totalUnrealized += unrealized
            log().info(prefix + " Position : " + str(self.getAC(symbol).positions) )
            log().info(prefix + " Avg Price : " + "{:.3f}".format(self.getAC(symbol).cost/max(self.getAC(symbol).positions, 1)))
            log().info(prefix + " Cost : " + str(self.getAC(symbol).cost) + "\n")
            totalCost += self.getAC(symbol).cost
        log().info("**** TOTAL REALIZED :" + str(totalRealized) +  " ** Total UnRealized :" + "{:.3f}".format(totalUnrealized) +  " ** Total Cost :" +"{:.0f}".format(totalCost) +  "\n")
