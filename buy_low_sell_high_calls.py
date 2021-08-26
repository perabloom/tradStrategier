# Version 3.6.1
# At a high level,
# We will be passing in a symbol as input
# Program will do the following
#   - a method will find all the options assocaited with that symbol
#   - The list returned will then be added to a subscription along with the stock
#   - As the quotes are received, on every tick, it will be determined ( based on extendable strategies ) whether to take long put/call position and hold/sell
#     within that duration for a certain stoploss
#   - QUESTIONS -> How do I know if an order is filled ? -> may be to begin with, trade only liquid stocks

import requests
import json
