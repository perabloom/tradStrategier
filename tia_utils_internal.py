# Version 3.6.1
# At a high level,
# This is an internal util class to get quick conversions/helper methods



import requests
import json
from tia.auth import *
from datetime import datetime
import time

# is it an equity symbol
def isEquitySymbol(symbol):
    if (len(symbol) <= 6):
        return True
    return False

def isOCCSymbol(symbol):
    if (len(symbol) >= 19):
        return True
    return False

# Get option details from the occ
def get_option_from_occ(opra):
    opra_symbol = opra[:-15]
    opra_expiry = '20' + opra[-15:-9]
    opra_date_time_object = datetime.strptime(opra_expiry,'%Y%m%d')
    # This is done so that the diff between expiries checked yield a better result
    opra_date_time_object = opra_date_time_object.replace(hour=23, minute=59)
    opra_cp = opra[-9]
    opra_strike = int(opra[-8:]) * .001
    return {'occ' : opra,
            'symbol' : opra_symbol,
            'expiry' : opra_date_time_object,
            'option_type' : opra_cp,
            'strike' : opra_strike }


#check if time epoch is stale
def isStale(line,epoch):
    epoch = int(epoch)/1000
    current_epoch = int(time.time())
    if (current_epoch - epoch > 10):
        file1 = open("STALE_DATA", "a")
        file1.write(str(json.loads(line)) + "\n")
        file1.close()

def example():
    print(get_option_from_occ('GOOG210820C02485000'))
