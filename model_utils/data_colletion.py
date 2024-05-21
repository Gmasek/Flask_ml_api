import os
from datetime import datetime

import IPython
import IPython.display
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import tensorflow as tf
import yfinance as yf

sectors ={
"Communication Services":1,
"Consumer Cyclical":2,
"Consumer Defensive":3,
"Energy":4,
"Financial Services":5,
"Healthcare":6,
"Industrials":7,
"Technology":8,
"Basic Materials":9,
"Real Estate":10,
"Utilities":11
}

def get_stocks_data(ticker:str,start:str,end:str)->pd.DataFrame:
    stock_data = yf.download(tickers=ticker,start=start,end=end)
    stock_data = stock_data.dropna()
    stock_data = pd.DataFrame(stock_data)
    #stock_sector = str(yf.Ticker(ticker).info["sector"])
    #stock_data["Sector"] = np.full(len(stock_data),stock_sector)
    return stock_data

def calc_macd(data, len1,len2,len3):
    shortEMA = data.ewm(span = len1, adjust= False).mean()
    longEMA = data.ewm(span = len2, adjust= False).mean()
    MACD = shortEMA-longEMA
    signal = MACD.ewm(span = len3 , adjust= False).mean()
    return MACD , signal

def calc_rsi(data,period):
    delta = data.diff() #egy nappal shiftelt diff
    up = delta.clip(lower=0)
    down = -1*delta.clip(upper=0)
    ema_up = up.ewm(com = period, adjust=False).mean()
    ema_down = down.ewm(com = period, adjust=False).mean()
    rs = ema_up / ema_down
    rsi = 100 - (100/(1+rs))
    return rsi

def get_indicators(data):
    df = pd.DataFrame(data)
    print(df.head())
    df['Prev_close'] = df.loc[:,'Close'].shift(1)
    df['Prev_volume'] = df.loc[:,'Volume'].shift(1)
    df['Prev_Open']= df.loc[:,'Open'].shift(1)
    df['Prev_Hi']=df.loc[:,'High'].shift(1)
    df['Prev_lo']=df.loc[:,'Low'].shift(1)
   
    
    
    datetimes = df.index.values
    weekdays = []
   
    for dt in datetimes:
        dt = datetime.strptime(str(dt), '%Y-%m-%dT%H:%M:%S.000000000')
        weekdays.append(dt.weekday())
    df['Weekday'] = weekdays    
    
    df["5SMA"] = df['Prev_close'].rolling(5).mean()
    df["10SMA"] = df['Prev_close'].rolling(10).mean()
    df["50SMA"] = df['Prev_close'].rolling(50).mean()
    df["200SMA"] = df['Prev_close'].rolling(200).mean()
    df["Move_direct"]= (1-df['Prev_Open'] / df["Prev_close"] )*100
    df["OBV"]=np.where(df['Prev_close'] > df['Prev_close'].shift(1), df['Prev_volume'], np.where(df['Prev_close'] < df['Prev_close'].shift(1), -df['Prev_volume'], 0)).cumsum()
    df["TR"]=np.maximum(df["Prev_Hi"]-df["Prev_lo"],df["Prev_Hi"]-df["Prev_close"].shift(1),df["Prev_close"].shift(1)-df["Prev_lo"])
    df['ATR14'] = df["TR"].rolling(14).mean()
    df["+DM"]=df["Prev_Hi"].shift(1)-df["Prev_Hi"]
    df["-DM"]=df["Prev_lo"].shift(1)-df["Prev_lo"]
    df["EMA14+"]=df["+DM"].ewm(com=0.1).mean()
    df["EMA14-"]=df["-DM"].ewm(com=0.1).mean()
    df["Prediction"]= df['Close'].transform(lambda x : np.sign(x.diff()))
    
    df["+DI14"]=(df["EMA14+"]/df['ATR14'])*100
    df["-DI14"]=(df["EMA14-"]/df['ATR14'])*100
    df["DI14"]= np.abs(df["+DI14"]-df["-DI14"]) / np.abs(df["+DI14"] + df["-DI14"])
    df["ADX14"]= (df["DI14"].shift(1)*13 + df["DI14"])*100
    df["ADXUT"]= np.where((df["ADX14"] < 25) & (df["ADX14"].shift(1) > 25) & (df["+DI14"] > df["-DI14"]),1,0)
    df["ADXDT"]= np.where((df["ADX14"] < 25) & (df["ADX14"].shift(1) > 25) & (df["+DI14"] < df["-DI14"]),-1,0)
    df["StcOsc"]= 100*(df["Prev_close"]-df["Prev_close"].rolling(14).min())/(df["Prev_close"].rolling(14).max() - df["Prev_close"].rolling(14).min())
    macd,signal = calc_macd(df['Prev_close'],12,26,9)
    df['MACD'] = macd
    df['MACD_signal']=signal
    df['RSI'] = calc_rsi(df['Prev_close'],13)
    df['RSI_volume'] = calc_rsi(df['Prev_volume'],13)
    df["Target"] = df.rolling(2).apply(lambda x: x.iloc[1] > x.iloc[0])["Prev_close"]
    df.dropna()
    return df

df = get_indicators(get_stocks_data("GOOG","2000-01-01","2024-05-01"))

def data_split(df:pd.DataFrame):
    colum_indices = {name: i for i,name in enumerate(df.columns)}
    n = len(df)
    train_df = df[0:int(0.7*n)]
    val_df = df[int(n*0.7):int(n*0.9)]
    test_df = df[int(n*0.9):]
    num_features = df.shape[1]
    train_mean = train_df.mean()
    train_std = train_df.std()
    train_df = (train_df - train_mean) / train_std
    val_df = (val_df - train_mean) / train_std
    test_df = (test_df - train_mean) / train_std
    df_std = (df - train_mean) / train_std
    df_std = df_std.melt(var_name='Column', value_name='Normalized')
    return train_df,val_df,test_df

data_split(df=df)