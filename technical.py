import ffn
from flask import Flask
import numpy as np
import pandas as pd
import pandas_datareader.data as web
import requests
from datetime import datetime
import pickle
import talib
from talib import MA_Type
import requests
import io

# 計算 MaxDD
def DrawDownAnalysis(cumRet):
    dd_series = ffn.core.to_drawdown_series(cumRet)
    dd_details = ffn.core.drawdown_details(dd_series)
    return dd_details['drawdown'].min(), dd_details['days'].max()

# sharpe ratio: 判斷報酬的好壞跟穩定度，數值越大越好
# maxdd: maximum drawdown, 最糟糕的狀況會賠幾 %
# maxddd: maximum drawdown duration, 低於上一次最高報酬的天數
# cumRet[-1]: 最後賺的 % 數

def indicators(df):
    dailyRet = df['Close'].pct_change()
    excessRet = (dailyRet - 0.04/252)[df['positions'] == 1]
    SharpeRatio = np.sqrt(252.0)*np.mean(excessRet)/np.std(excessRet)
    cumRet = np.cumprod(1+excessRet)
    maxdd, maxddd = DrawDownAnalysis(cumRet)
    return SharpeRatio, maxdd, maxddd, cumRet[-1]

def BBands_way(df,timeperiod,std):
    df['UBB'], df['MBB'], df['LBB'] = talib.BBANDS(df['Close'].values, timeperiod=timeperiod, nbdevup=std, nbdevdn=std, matype=0)

    has_position = False
    df['signals'] = 0
    for t in range(2, df['signals'].size):
        if df['Close'][t] < df['LBB'][t-1]:
            if not has_position:
                df.loc[df.index[t], 'signals'] = 1
                has_position = True
            elif df['Close'][t] > df['UBB'][t-1]:
                if has_position:
                    df.loc[df.index[t], 'signals'] = -1
                    has_position = False

    df['positions'] = df['signals'].cumsum().shift()
    return df

def KD_way(df,upbreak,downbreak):
    df["K"], df["D"] = talib.STOCHF(df["High"].values, df["Low"].values, df['Close'].values,
                                    fastk_period=9, fastd_period=9,fastd_matype=MA_Type.T3)

    has_position = False
    df['signals'] = 0
    for t in range(2, df['signals'].size):
        if (df['K'][t] > df["D"][t-1])|(df["D"][t] > upbreak):
            if not has_position:
                df.loc[df.index[t], 'signals'] = 1
                has_position = True
        elif (df['K'][t] < df["D"][t-1])|(df["D"][t] < downbreak):
            if has_position:
                df.loc[df.index[t], 'signals'] = -1
                has_position = False

    df['positions'] = df['signals'].cumsum().shift()
    return df

def william_way(df,timeperiod,oversold,overbuy):
    df["W"] = talib.WILLR(df["High"].values, df["Low"].values, df["Close"].values, timeperiod = timeperiod)

    has_position = False
    df['signals'] = 0
    for t in range(2, df['signals'].size):
        if (df['W'][t] > -oversold):
            if not has_position:
                df.loc[df.index[t], 'signals'] = 1
                has_position = True
        elif (df['W'][t] < -overbuy):
            if has_position:
                df.loc[df.index[t], 'signals'] = -1
                has_position = False

    df['positions'] = df['signals'].cumsum().shift()
    return df

def RSI_way(df,LRSI,HRSI):
    df['RSI'] = talib.RSI(df['Close'].values)

    has_position = False
    df['signals'] = 0
    for t in range(2, df['signals'].size):
        if df['RSI'][t-1] < LRSI:
            if not has_position:
                df.loc[df.index[t], 'signals'] = 1
                has_position = True
            elif df['RSI'][t-1] > HRSI:
                if has_position:
                    df.loc[df.index[t], 'signals'] = -1
                    has_position = False

    df['positions'] = df['signals'].cumsum().shift()
    return df

def MA_way(df,SMA,LMA):
    df['SMA'] = np.round(pd.Series.rolling(df['Close'], window=SMA).mean(), 2)
    df['LMA'] = np.round(pd.Series.rolling(df['Close'], window=LMA).mean(), 2)

    has_position = False
    df['signals'] = 0
    for t in range(2, df['signals'].size):
        if df['Close'][t] > df['SMA'][t-1] and df['SMA'][t-1] > df['LMA'][t-1] :
            if not has_position:
                df.loc[df.index[t], 'signals'] = 1
                has_position = True
        elif df['Close'][t] < df['SMA'][t-1] and df['SMA'][t-1] < df['LMA'][t-1] :
            if has_position:
                df.loc[df.index[t], 'signals'] = -1
                has_position = False

    df['positions'] = df['signals'].cumsum().shift()
    return df
