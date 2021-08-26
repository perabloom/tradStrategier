# Version 3.6.1
import requests
import json
import trade as tradeUtil
import orders as orderUtil
import positions as position_util
from tia.log import *
from tickprocessor import *
import broker as brokerUtil

import time

class MARKET_MAKE:
  def __init__(self, config = {
                  'trade_quantity' : 100,
                  'bar_interval_in_mins' : 0.5,
                  'use_own_date' : False,
                  'is_backtest' : False,
                  'backtest_offset_days' : 0,
                  'max_spread' : 0.10,
                  }):
    self._processor = TickProcessor(config)
    self._broker = brokerUtil.Broker()
    self._config = config
    self.QUANTITY = self._config['trade_quantity']
    self.MAX_SPREAD = self._config['max_spread']
    self.ORDER_TYPE = 'limit'
    self.DURATION = 'pre'


  ASSET_TYPES = ["STOCK"]

  def getProcessor(self):
      return self._processor

  def getBroker(self):
      return self._broker

  def hndl(self, data):
    print(data)
    self.handle_data(data)

  ## Make market essentially! Quote a bit under bid ask - buy low , sell high
  def handle_data(self, data):
    log().debug(data)
    symbol = data[0]['symbol']

    # Process each tick
    for tick in data:
        self._processor.process(symbol, tick)

    stats = self._processor.getTickStore(symbol).getStats()
    timesale = self._processor.getTickStore(symbol).getLatestTimesale()
    quote = self._processor.getTickStore(symbol).getLatestQuote()

    ORDER_TYPE = self.ORDER_TYPE
    DURATION = self.DURATION
    QUANTITY = self.QUANTITY

    data = data[0]
    start = time.perf_counter()
    orders = orderUtil.getOrdersIdsWithStateForSymbol('open', symbol) # send symbol
    end = time.perf_counter()
    positions = position_util.getPositions(symbol) # Send symbol
    end2 = time.perf_counter()
    log().debug("ORDER CALL: " + str(end - start))
    log().debug("POSITION CALL : " +  str(end2 - end))
    e3 = time.perf_counter()
    log().debug("LOGGING CALL : " +str(e3 - end2))
    order_exists = len(orders) >= 1
    position_exists = len(positions) >= 1
    if (len(positions) > 1):
      raise Exception("More than 1 position reported", len(positions), positions)
    if (len(orders) > 1):
      raise Exception("More than 1 open orders : ", len(orders))
    log().debug('ORDER - ' + str(orders))
    log().debug('POSITION -' + str(positions))
    if (data['type'] == 'quote' or data['type'] == 'timesale'):
      ask = float("{:.2f}".format(float(data['ask'])))
      bid = float("{:.2f}".format(float(data['bid'])))
      spread = ask - bid
      spread = float("{:.3f}".format(spread))
      my_bid = bid + 0.01
      my_bid = float("{:.2f}".format(my_bid))
      my_ask = ask - 0.01
      my_ask = float("{:.2f}".format(my_ask))
      log().debug('(MY_BID,MY_ASK) - ' + str(my_bid) + "," + str(my_ask))
      if (my_ask - my_bid <= 0.02):
        if (order_exists):
          log().warn("My Bid >= My Ask, cancelling any orders and/or close positions if any")
          tradeUtil.cancelOrder(orders[0]['id'])
        if (position_exists):
          tradeUtil.closePositions(positions, DURATION)
        return
      if (position_exists == False):
        log().debug("NO POSITION EXISTS")
        if (order_exists == True):
          orders = orders[0]
          orderId = orders['id']
          # Is it a sell order or buy order
          side = orders['side']
          price = orders['price']
          log().debug('ORDER ALREADY EXISTS - adjustBidIfNeeded')
          if (side == 'buy'):
            # check if my_bid is same as order's bid
            if (abs(price - bid) < 0.001):
              log().debug("NO ADJUSTMENT OF BID NEEDED as current bid equals the bid that was sent")
              pass
            else:
              # cancel the order and resend a new one
              # It will fail if it's filled, in which case handle the exception and return
              try:
                log().warn("Cancelling existing bid for order - " + str(orderId))
                tradeUtil.cancelOrder(orderId)
              except Exception as e:
                log().debug("ERROR : Failed to cancel order " + str(orderId) + " with exception : " + str(e))
                return
              # place new trade with new price
              log().debug('Placing a new Bid post cancellation of earlier bid')
              order_id = tradeUtil.sendOrder('equity', data['symbol'], 'buy', QUANTITY, my_bid, ORDER_TYPE, DURATION, data['symbol'])
          elif (side == 'sell'):
            log().critical("ERROR - There should not be any sell order if NO POSITION exists")
            raise Exception("No position exists")
        else:
          # No position or order, send a buy limit order
          log().info('NO ORDER EXISTS - Sending an Order')
          order_id = tradeUtil.sendOrder('equity', data['symbol'], 'buy', QUANTITY, my_bid, ORDER_TYPE, DURATION, data['symbol'])
      else:
        # if position exists
        log().debug("POSITION ALREADY EXISTS")
        if (order_exists == True):
            orders = orders[0]
            # Is it a sell order or buy order
            side = orders['side']
            price = orders['price']
            log().debug('adjustAskIfNeeded')
            # check if my_ask is same as order's ask
            if (abs(price - ask) < 0.001):
              log().debug("NO ADJUSTMENT OF ASK NEEDED as my_ask equals my expected theo ask")
              pass
            else:
              # cancel the order and resend a new one
              # It will fail if it's filled, in which case handle the exception and return
              try:
                log().warn("Cancelling existing ask for order -" + str(orders['id']))
                tradeUtil.cancelOrder(orders['id'])
              except Exception as e:
                log().debug("ERROR : Failed to cancel order " + str(orders['id']) + " with exception : " + str(e))
                return
              # place new trade with new price
              order_id = tradeUtil.sendOrder('equity', data['symbol'], 'sell', QUANTITY, my_ask, ORDER_TYPE, DURATION, data['symbol'])
        else:
          # Has position but no order, send a sell limit order
          log().info('POSITION EXISTS BUT NO SELL ORDER EXIST - Sending an SELL Order')
          order_id = tradeUtil.sendOrder('equity', data['symbol'], 'sell', QUANTITY, my_ask, ORDER_TYPE, DURATION, data['symbol'])




      # send a limit buy order to buy just above the bid,
      # Check if it's executed, , send a limit sell order just under the ask
      # if quote bid goes down, cancel the order and move it just above the bid, if quote matches, cancel and increase it
