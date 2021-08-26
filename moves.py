import timesaleMoves as timeSaleMovesUtil
import sys


#for sym in ['TAL', 'WISH', 'PSFE', 'SPY', 'QQQ', 'BCEL', 'FUBO', 'WKHS', 'RIDE', 'NKLA', 'AMC']:
#    val = movement1m(sym, 0, 10)
#    if (float(val['per_interval_moves_pct']) >= 1):
#        print(val)
def example():
    if (len (sys.argv) > 1 and sys.argv[1] is not None):
        daysBack = 10
        print(timeSaleMovesUtil.dailyOpenCloseMoves(sys.argv[1], daysBack))
#example()
print(timeSaleMovesUtil.movement1m(sys.argv[1], 0, 10))
