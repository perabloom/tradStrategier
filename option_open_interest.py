# Version 3.6.1
import sys as sys
import quote as quoteUtil
import option_chain as optionChainUtil
import tia_utils_internal as utils
from datetime import datetime, timedelta
import get_options as getOptionsUtil



getNearest = True
expiriesTill = 3
# Symbol, how many above and below spot, nearest and expiries Till
options = getOptionsUtil.getOptions(sys.argv[1], int(sys.argv[2]), getNearest, expiriesTill)
calls = []
puts = []
expCalls = {}
expPuts = {}

for option in options:
    occ = utils.get_option_from_occ(option['symbol'])
    if (occ['option_type'] == "C"):
        calls.append(option)
        if (occ['expiry'] not in expCalls):
            expCalls[occ['expiry']] = []
        expCalls[occ['expiry']].append(option)
    else:
        puts.append(option)
        if (occ['expiry'] not in expPuts):
            expPuts[occ['expiry']] = []
        expPuts[occ['expiry']].append(option)

for option in calls:
    #print(option)
    print(option['symbol'],option['description'], option['open_interest'])
print("\n")
for option in puts:
    print(option['symbol'],option['description'], option['open_interest'])

expCalls = []
for exp in expCalls:
    print(exp)
    for option in expCalls[exp]:
        print(option['symbol'],option['description'], option['open_interest'])
