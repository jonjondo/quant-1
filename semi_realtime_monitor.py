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
from futuquant.open_context import *

import tushare as ts
import talib as ta
import matplotlib
import matplotlib.pyplot as plt
from futuquant.open_context import *
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


def get_stock_dmi_my_signal(quote_ctx, stock_id, market_snap_data):
    N, MM = 14, 6
    now = datetime.now()
    start_day = (now - timedelta(365)).strftime("%Y-%m-%d")

    ## 往前读多一天，创造Index
    end_day = (now + timedelta(1)).strftime("%Y-%m-%d")

    ret, dfret = quote_ctx.get_history_kline(stock_id, start_day, end_day, ktype='K_DAY', autype='qfq')  # 获取历史K线
    if not dfret.empty:
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

        # df['tr']=ta.EMA(df['tr'],N)
        # EXPMEMA(MAX(MAX(HIGH-LOW,ABS(HIGH-REF(CLOSE,1))),ABS(REF(CLOSE,1)-LOW)),N);
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

        ma20 = ta.SMA(dfret['close'].values, timeperiod=20)
        df['DX'] = ta.EMA((df['NPDM'] - df['NMDM']) / (df['NMDM'] + df['NPDM']) * 100, MM)
        df['ADX'] = df['DX']
        df['ADXR'] = ta.EMA(df['ADX'], MM)
        df['AAJ'] = 0
        df['AAJ'] = ta.EMA(3 * df['ADX'] - 2 * df['ADXR'], 2)

        dfret = pd.concat([dfret, df], axis=1)
    return df['AAJ'], ma20

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
    print(china_list)
    us_list = list(filter(lambda x: ("US" in x), stock_ids))
    # 当前检测的列表，默认是全部
    working_list = stock_list

    cur_aaj_values = {}
    market_is_open = False

    #TODO： 冬令时和夏令时，而且应该用UTC时间，考虑到加村和中国刚好相反
    Chinese_market_open = time(9, 30)
    Chinese_market_close = time(16, 0)

    US_market_open = time(21, 30)
    US_market_close = time(4, 0)

    now = datetime.now()
    curr_time = time(now.hour, now.minute)

    # 检查市场状态
    ret, market_states = quote_ctx.get_global_state()
    if (time_in_range(Chinese_market_open, Chinese_market_close, curr_time) and (
            market_states['Market_HK'] == '3' or market_states['Market_HK'] == '5' or market_states[
        'Market_SH'] == '3' or market_states['Market_SH'] == '5')):
        working_list = china_list
        market_is_open = True
    elif (time_in_range(US_market_open, US_market_close, curr_time) and (
            market_states['Market_US'] == '3' or market_states['Market_US'] == '5')):
        working_list = us_list
        market_is_open = True
    else:
        market_is_open = False

    if not market_is_open:
        print("Market is not open, waiting " + str(datetime.now()))
        return

    # 获取当前报价
    ret0, dfret_snap = quote_ctx.get_market_snapshot(working_list)
    market_snap_data = {}
    if not dfret_snap.empty:
        for i in range(len(dfret_snap.index)):
            snap_data = [dfret_snap['high_price'][i], dfret_snap['low_price'][i], dfret_snap['last_price'][i]]
            market_snap_data[dfret_snap['code'][i]] = snap_data
    else:
        print("Fail to read the market snap data")

    for stock in working_list:
        aaj, ma20 = get_stock_dmi_my_signal(quote_ctx, stock, market_snap_data)

        last = len(aaj)
        curr_aaj = aaj[last - 1]
        prev_aaj = aaj[last - 2]
        mid = ma20[-1]
        descision = ""
        op = ""
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
        # 单纯地看趋势扭转太敏感
        # elif curr_aaj  < prev_aaj:
        # decision = "SELL"
        # elif curr_aaj > prev_aaj:
        # decision = "BUY"
        mgr.search_stockrecord_by_stockcode(descision, op)


if __name__ == "__main__":
    API_SVR_IP = '192.168.0.106'
    API_SVR_PORT = 11111
    quote_ctx = OpenQuoteContext(host=API_SVR_IP, port=API_SVR_PORT)  # 创建行情api

    mgr = StockUserMgr()
    my_monitor(quote_ctx, mgr)
    quote_ctx.close()




