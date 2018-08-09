# -*- coding: utf-8 -*-
"""
监测AAJ基于日线数据的变化并发出邮件提醒
"""
from time import sleep
import sys
import os

from data_orm import *
import wechat_assit as wa

sys.path.append(os.path.split(os.path.abspath(os.path.pardir))[0])
## from futuquant import *

import tushare as ts
import talib as ta
import matplotlib
import matplotlib.pyplot as plt
from futuquant import *
import datetime
import numpy as np
import pandas as pb
import matplotlib.dates as mdate

import smtplib
from email.mime.text import MIMEText
from email.header import Header

import numpy
import chardet
import csv
import sqlite3

from datetime import datetime, timedelta, time
from time import gmtime, strftime
import time as t

from stock_user_manager import StockUserMgr



def process_single_df(dfret, stock_id, market_snap_data):
    startTime = int(round(t.time() * 1000))
    N, MM = 14, 6
    high = dfret['high']
    size = len(high)
    high[size] = market_snap_data[stock_id][0]

    low = dfret['low']
    low[size] = market_snap_data[stock_id][1]
    close = dfret['close']
    close[size] = market_snap_data[stock_id][2]
    df = pd.DataFrame()
    df['h-l'] = high - low
    df['h-c'] = abs(high - close.shift(1))
    df['l-c'] = abs(close.shift(1) - low)
    df['tr'] = df.max(axis=1)

    df['PDM'] = high - high.shift(1)
    df['MDM'] = low.shift(1) - low
    df['DPD'] = 0
    df['DMD'] = 0
    for i in range(len(df.index)):
        PDM = df.ix[i, 'PDM']
        MDM = df.ix[i, 'MDM']
        if PDM < 0 or PDM < MDM:
            df.ix[i, 'DPD'] = 0
        else:
            df.ix[i, 'DPD'] = PDM
        if MDM < 0 or MDM < PDM:
            df.ix[i, 'DMD'] = 0
        else:
            df.ix[i, 'DMD'] = MDM

        df['NTR'] = ta.EMA(df['tr'], N)
        df['NPDM'] = ta.EMA(df['DPD'], N)
        df['NMDM'] = ta.EMA(df['DMD'], N)
        df['PDI'] = df['NPDM'] / df['NTR'] * 100
        df['MDI'] = df['NMDM'] / df['NTR'] * 100
    try:
        ma20 = ta.SMA(dfret['close'].values, timeperiod=20)
        df['DX'] = ta.EMA((df['NPDM'] - df['NMDM']) / (df['NMDM'] + df['NPDM']) * 100, MM)
        df['ADX'] = df['DX']
        df['ADXR'] = ta.EMA(df['ADX'], MM)
        df['AAJ'] = 0
        df['AAJ'] = ta.EMA(3 * df['ADX'] - 2 * df['ADXR'], 2)
        endTime = int(round(t.time() * 1000))
        print("计算AAJ成功,耗时%sms"%(endTime - startTime))
    except:
       print("计算AAJ失败%s"%stock_id)
       df['AAJ']=None
    return df['AAJ'], ma20

def get_stocks_dmi_my_signal(quote_ctx, stock_ids, market_snap_data):
    now = datetime.now()
    start_day = (now - timedelta(90)).strftime("%Y-%m-%d")
    ## 往前读多一天，创造Index
    end_day = (now + timedelta(1)).strftime("%Y-%m-%d")

    stock_id_2_aaj = {}
    stock_id_2_ma20 = {}

    ret, dfrets = quote_ctx.get_multiple_history_kline(stock_ids, start_day, end_day, ktype='K_DAY', autype='qfq')  # 获取历史K线
    for idx, dfret in enumerate(dfrets):
        if not dfret.empty:
            curr_stock_id = stock_ids[idx]
            curr_aaj, ma20 = process_single_df(dfret, curr_stock_id, market_snap_data)
            stock_id_2_aaj[curr_stock_id] = curr_aaj
            stock_id_2_ma20[curr_stock_id] = ma20
        else:
            print("Failed to process " + stock_ids[idx])
    return stock_id_2_aaj, stock_id_2_ma20

def aaj_out_bound(upper, lower, aaj):
    return aaj >= upper or aaj <= lower

def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end


def my_monitor(quote_ctx, mgr):
    # 读取数据库记录
    stocks_to_user_emails = {}
    trend_record = {}
    # TODO: 这个阈值，个股都应该有自己的
    aaj_upper = 75
    aaj_lower = -75.46
    
    stock_ids = mgr.get_all_stock_ids()

    # 股票分类
    china_list = list(filter(lambda x: ("HK" in x[:2]) or ("SH" in x[:2]) or ("SZ" in x[:2]), stock_ids))
    us_list = list(filter(lambda x: ("US" in x), stock_ids))
    # 当前检测的列表，默认是全部
    working_list = stock_ids

    cur_aaj_values = {}
    market_is_open = False
    #TODO： 冬令时和夏令时，而且应该用UTC时间，考虑到加村和中国刚好相反
    Chinese_market_open = time(9, 30)
    Chinese_market_close = time(22, 0)

    US_market_open = time(21, 30)
    US_market_close = time(4, 0)

    now = datetime.now()
    curr_time = time(now.hour, now.minute)

    # 检查市场状态
    # ret, market_states = quote_ctx.get_global_state()
    if (time_in_range(Chinese_market_open, Chinese_market_close, curr_time)):
        working_list = china_list
        market_is_open = True
    elif (time_in_range(US_market_open, US_market_close, curr_time)):
        working_list = us_list
        market_is_open = True
    else:
        market_is_open = False

    if not market_is_open:
        print("Market is not open, waiting " + str(datetime.now()))
        return

    # 获取当前报价
    df_total_snap= pb.DataFrame()
    for i in range(0,len(working_list),199):
        if i + 199 > len(working_list):
            ret0, dfret_snap = quote_ctx.get_market_snapshot(working_list[i:])
        else:
            ret0, dfret_snap = quote_ctx.get_market_snapshot(working_list[i:i+199])
        if ret0 != 0:
            print("get market snapshot error %s,%s"%(dfret_snap,i)) 
        else:
            df_total_snap=df_total_snap.append(dfret_snap, ignore_index=True) # sneaky little dataframe will keep the indices.

    market_snap_data = {}
    if not df_total_snap.empty:
        for i in range(len(df_total_snap.index)):
            snap_data = [df_total_snap['high_price'][i], df_total_snap['low_price'][i], df_total_snap['last_price'][i]]
            market_snap_data[df_total_snap['code'][i]] = snap_data
    else:
        print("Fail to read the market snap data")

    stock_id_2_aaj, stock_id_2_ma20 = get_stocks_dmi_my_signal(quote_ctx, working_list, market_snap_data)

    for stock in working_list:
        try: 
            aaj = stock_id_2_aaj[stock]
            ma20 = stock_id_2_ma20[stock]
        except:
            continue
        if len(aaj) == 0:
            print("ERROR: stock " + stock + " has no data")
            continue
        last = len(aaj)
        curr_aaj = aaj[last - 1]
        prev_aaj = aaj[last - 2]
        mid = ma20[-1]
        descision = ""
        op = ""
        try:
            if (market_snap_data[stock][2] >= mid and curr_aaj > prev_aaj):
                descision = 'BUY'
                op = "趋势反转，超过20日均线，可以考虑加仓"
            elif (market_snap_data[stock][2] < mid and curr_aaj < prev_aaj):
                descision = 'SELL'
                op = "低于MA20并趋势向下，可以考虑减仓或者止损"
            # elif (market_snap_data[stock][2] <  mid and trend_record[stock] == "BUY closed price > ma20"): 因为满足条件1 以后，数据库的记录会变化，这个会导致发邮件过于频繁 TODO: 三个点的线性回归判断
            #    descision = "SELL closed price < ma20"
            elif (curr_aaj > aaj_upper and curr_aaj < prev_aaj) or (prev_aaj >= aaj_upper and curr_aaj <= aaj_upper):
                descision = 'SELL'
                op = "顶部趋势扭转，逃顶/清仓"
            elif ((curr_aaj < aaj_lower and curr_aaj > prev_aaj) or (prev_aaj < aaj_lower and curr_aaj > aaj_lower)):
                descision = 'BUY'
                op = "底部趋势扭转，抄底/建仓"
            else:
                descision = 'WAIT'
                op = '等待时机'
        # 单纯地看趋势扭转太敏感
        # elif curr_aaj  < prev_aaj:
        # decision = "SELL"
        # elif curr_aaj > prev_aaj:
        # decision = "BUY"
            print("处理%s %s 完成"%(stock,descision))
        #mgr.search_stockrecord_by_stockcode_semi_rt(stock,descision, op)
        except:
            print("处理%s %s 失败，数据可能为空"%(stock,descision))
            continue

if __name__ == "__main__":
    API_SVR_IP = '127.0.0.1'
    API_SVR_PORT = 11111
    quote_ctx = OpenQuoteContext(host=API_SVR_IP, port=API_SVR_PORT)  # 创建行情api
    startTime = int(round(t.time() * 1000))
    print("开始量化处理%s"%int(round(t.time() * 1000)))
    mgr = StockUserMgr()
    my_monitor(quote_ctx, mgr)
    endTime = int(round(t.time() * 1000))
    print("处理结束,总共耗时%s"%(endTime - startTime))
    quote_ctx.close()




