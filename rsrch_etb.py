# Version 3.6.1
import requests
from tia.auth import *
from tia.log import *
import etb as etbUtil
import rsrch_vwap as rsrchVWAPUtil
import numpy as np
import pandas as pd


def example2():
    # including x and y
    avg_vol = 100000
    results = etbUtil.get_etb_between_x_y(4, 10, avg_vol) # [{'symbol': 'LUMN', 'last': 12.155, 'avg_vol': 14862408}]
    #results = [{'symbol' : 'SLB'}, {'symbol' : 'OXY'}, {'symbol' : 'HAL'}, {'symbol' : 'SPY'}, {'symbol' : 'QQQ'}]
    mp = {}
    df = pd.DataFrame()
    for res in results:
        print(res)
        symbol = res['symbol']
        res_df = rsrchVWAPUtil.dailyVWAPs(symbol)
        df[symbol] = res_df['vwap'].pct_change()
        mp[symbol] = res_df
    print(df)
    print (mp)
    print(len(mp))
    return
    df.drop(index=df.index[0],axis = 0, inplace=True)

    symbols = list(df.columns)
    for symbol in symbols:
        df_temp = df
        if (True):
            list_stk = df_temp[symbol].tolist()[1:]
            df_temp = df_temp.drop(symbol, 1)
            df_temp.drop(df.tail(1).index,inplace=True)
            df_temp[symbol] = list_stk
        correlation_mat = df_temp.corr()
        correlation_mat[symbol][symbol] = 0
        best = correlation_mat[symbol].max()
        bestIdx = correlation_mat[symbol].idxmax()
        worst = correlation_mat[symbol].min()
        worstIdx = correlation_mat[symbol].idxmin()
        print(symbol, best,bestIdx,  worst, worstIdx)
        #correlation_mat.to_csv("correlation.csv")
        #print(correlation_mat)

if __name__ == '__main__':
    example2()
