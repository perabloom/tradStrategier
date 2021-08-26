# Version 3.6.1
from datetime import datetime, timedelta

def isVWAPDownTrending(bars, intervals = 3):
    if (len(bars) < (intervals + 1)):
        return False
    lastBar = bars[-2]._vwap
    prevBar = bars[-3]._vwap
    prevPrevBar = bars[-4]._vwap
    if (prevPrevBar > prevBar and prevBar > lastBar):
        return True
    return False

def isGreen(bar):
    if (bar._o < bar._c):
        return True
    else:
        return False


def fmt(val):
    return
# if trending lower for last three, previous one is better than the second last and the current is better than the last's low
def isDownAndNowBetter(bars, downI = 3, upI = 1):
    maxL = downI + upI + 1
    if (len(bars) < (maxL)):
        return False
    curBar = bars[-1]
    if bars[-maxL]._vwap - bars[-maxL + 1 ]._vwap >= 0.01 and bars[-maxL + 1]._vwap - bars[-maxL + 2]._vwap >= 0.01:
        if (bars[-upI - 1]._vwap >= bars[-upI - 2]._vwap):
            #if (curBar._vwap >= bars[-upI - 1]._vwap):
            if (curBar._c <= bars[-upI - 1]._o ):
                return True
    return False

def lastDdownsUups(bars, D = -3, U = -1):
    maxL = D + U - 1
    if (len(bars) < (-maxL)):
        return False
    for i in range(D + U - 1, U - 1 - 1):
        if (bars[i]._vwap <= bars[i+1]._vwap):
            return False
        if (bars[i]._c <= bars[i+1]._c):
            return False

    for i in range(U-1, -1):
        if ( i == U-1):
            if (bars[i-1]._c < bars[i]._c):
                return False
        elif (bars[i-1]._vwap >= bars[i]._vwap):
            return False
    curBar = bars[-1]

    if (curBar._c < bars[-1]._o):
        return True
    else:
        return False

def sunGreen(bars, WIN):
    if (len(bars) < 4):
        return False

    # Last bar should be green
    if (isGreen(bars[-2]) is False):
        return False

    # Now keep goiing back from -3 onwards till we see continuous declining vwap and lower closes
    i = -3
    while True:
        prev = i - 1
        if (-prev >= len(bars)):
            return False
        if ( bars[i-1]._c > bars[i]._c): # bars[i-1]._vwap > bars[i]._vwap and
            i -= 1
            continue
        else:
            break
    if (i > -7):
        return False
    if (bars[i]._vwap - bars[-2]._vwap >  WIN ):
        return True
    return False

def isVWAPLessThanPrev(bars):
    if (bars[-2]._vwap > bars[-1]._vwap and bars[-2]._vol <= bars[-1]._vol*2):
        return True
    return False

def wasUpAndNowFalling(bars):
    if (len(bars) < 2):
        return False
    if (bars[-1]._c < bars[-2]._l):
        return True
    return False

def isUpUpUpUp(bars):
    if (len(bars) < 4):
        return False
    if (bars[-4]._vwap < bars[-3]._vwap < bars[-2]._vwap < bars[-1]._c):
        return True
    return False

def isUpUpUpUpWithVol(bars):
    if (len(bars) < 4):
        return False
    if (bars[-4]._vwap < bars[-3]._vwap < bars[-2]._vwap < bars[-1]._c):
        if (bars[-4]._vol < bars[-3]._vol < bars[-2]._vol):
            return True
    return False

def isUpUpUpUpWithVolAndHigherCloses(bars):
    if (len(bars) < 4):
        return False
    if (bars[-4]._vwap < bars[-3]._vwap < bars[-2]._vwap < bars[-1]._c):
        if (bars[-4]._vol < bars[-3]._vol < bars[-2]._vol):
            if (bars[-4]._c < bars[-3]._c < bars[-2]._c):
                if (bars[-4]._o < bars[-4]._c < bars[-3]._o < bars[-3]._c < bars[-2]._o < bars[-2]._c):
                    return True
    return False


def getHighestAndLowest(bars, count):
    l = len(bars)
    if (l <= 0):
        print("Bar is of 0 length")
        for bar in bars:
            print (bar)
        return None, None
    lMax = 0
    lMin = 999999
    idx = 1
    while ( idx <= min(l,count)):
        lMax = max(lMax, bars[-idx]._h)
        lMin = min(lMin, bars[-idx]._l)
        idx = idx + 1
    return lMax, lMin
