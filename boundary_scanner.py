# -*- coding: utf-8 -*-
"""
扫描全盘找目标

"""
from time import sleep
import sys
import os

sys.path.append(os.path.split(os.path.abspath(os.path.pardir))[0])
## from futuquant import *
from futuquant import *
import send_email as sm
import tushare as ts
import talib as ta
import matplotlib
import matplotlib.pyplot as plt
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
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

bio_techs = "NKTR,ALKS,EXEL,CTLT,FGEN,AMRX,RDY,GMED,IMMU,ARRY,MDCO,HZNP,HRTX,IRWD,FOLD,AERI,ASND,SUPN,EBS,NUVA,PTLA,BPMC,ENDP,WMGI,HALO,CLVS,MNTA,SPPI,GBT,AKRX,XNCR,RGEN,CNMD,AXGN,CBM,ZGNX,ACAD,XLRN,TSRO,ARNA,MRTX,PBYI,XON,INSM,PBH,MNK,NXTM,PTCT,NVRO,AIMT,PCRX,DPLO,ARWR,CORT,IMGN,SGMO,LXRX,TBPH,ALDR,CHRS,ITCI,QURE,RDUS,CSII,ACOR,ESPR,RTRX,CRY,OFIX,BABY,ECYT,VNDA,OMER,RVNC,ASMB,KPTI,XENT,ADAP,FLXN,EPZM,VRAY,KTWO,TGTX,LJPC,MGNX,DVAX,ANIP,AMPH,CDXS,PETS,ADMS,DRNA,VKTX,COLL,CBAY,ABUS,CCXI,GLYC,AKBA,CARA,PRTA,ANIK,IVC,CUTR,FPRX,DEPO,FATE,LCI,STML,COOL,KIN,VCEL,DERM,MNOV,ZFGN,CNCE,VTL,PRTK,BSTC,MCRB,NERV,BLFS,NSTG,GLMD,IRMD,XOMA,SPNE,XENE,FONR,NATR,MSON,JNP,CBIO,CSBR,NAII"
bio_techs3 = "NAII"

bio_tech_array = bio_techs.split(",")
# print(bio_tech_array)
data = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
table = data[0]
sliced_table = table[1:]
header = table.iloc[0]
corrected_table = sliced_table.rename(columns=header)
SP500_tickers = corrected_table['Ticker symbol'].tolist()



data = pd.read_html('https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average')
table = data[1]
sliced_table = table[1:]
header = table.iloc[0]
corrected_table = sliced_table.rename(columns=header)
DAO_30 = corrected_table['Symbol'].tolist()

receipients = ["wangpenghehe@qq.com"]


class EmailNotification(object):
    """邮件提醒类"""
    sender = 'wangpenghehe@qq.com'
    password = 'tingting520'
    smtpserver = 'smtp.qq.com:465'
    enable = True

    @staticmethod
    def set_enable(enable=False):
        EmailNotification.enable = enable

    @staticmethod
    def is_enable():
        return EmailNotification.enable

    @staticmethod
    def send_email(receiver, subject, words, form):
        if not EmailNotification.is_enable():
            return
        try:
            msg = MIMEText(words, form, 'utf-8')  # 中文需参数‘utf-8'，单字节字符不需要
            msg['Subject'] = Header(subject, 'utf-8')  # 邮件标题
            msg['from'] = EmailNotification.sender  # 发信人地址
            msg['to'] = receiver  # 收信人地址

            smtp = smtplib.SMTP()
            smtp.connect(EmailNotification.smtpserver, 465)
            smtp.starttls()
            smtp.ehlo()
            smtp.login(EmailNotification.sender, EmailNotification.password)
            smtp.sendmail(EmailNotification.sender, receiver,
                          msg.as_string())  # 这行代码解决的下方554的错误
            print("Before smtp quit")
            smtp.quit()
            print("邮件发送成功!")
        except Exception as e:
            print(e)


def get_index_components(url, offset, key):
    data = pd.read_html(url)
    table = data[offset]
    sliced_table = table[1:]
    header = table.iloc[0]
    corrected_table = sliced_table.rename(columns=header)
    return corrected_table[key].tolist()

def lo_sir_stock_pick(quote_ctx, stock_id, start_day, end_day):
    ret, dfret = quote_ctx.get_history_kline(stock_id, start_day, end_day, ktype='K_DAY', autype='qfq')  # 获取历史K线
    # print(dfret)
    try:
        if not dfret.empty:
            high = dfret['high']
            # print(high)
            low = dfret['low']
            close = dfret['close']
            # print(close)
            opens = dfret['open']
            # print(opens)
            candle_stick = close - opens
            # print(candle_stick)
            largest_candle = max(candle_stick)

            l = len(candle_stick)
            if largest_candle == candle_stick[l-1] and largest_candle >= candle_stick[l-2] * 1.5:
                print(stock_id + " a good candidate")
                return True
            else:
                print(stock_id + " a bad candidate")
                return False
    except:
        print("Fail to process " + stock_id)
        return False
    return False

def get_stock_dmi_my_signal(quote_ctx, stock_id):
    N, MM = 14, 6
    now = datetime.now()
    start_day = (now - timedelta(90)).strftime("%Y-%m-%d")

    end_day = now.strftime("%Y-%m-%d")

    ret, dfret = quote_ctx.get_history_kline(stock_id, start_day, end_day, ktype='K_DAY', autype='qfq')  # 获取历史K线
    if not dfret.empty:
        high = dfret['high']
        low = dfret['low']
        close = dfret['close']
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
    return df['AAJ'], ma20, dfret['volume']

def generate_list(quote_ctx, market, file_name, upper, lower):
    ret, data_frame = quote_ctx.get_stock_basicinfo(market=market, stock_type='STOCK')
    df = data_frame[data_frame['name'].str.contains("退市|ST") == False]
    print(df)

    tickers_lower = []
    names_lower = []
    values_lower = []
    volumes_lower = []
    options_lower = []
    tickers_upper = []
    names_upper = []
    values_upper = []
    volumes_upper = []
    options_upper = []
    for index, row in df.iterrows():
        try:
            aajs, ma20s, ret_volumes = get_stock_dmi_my_signal(quote_ctx, row['code'])
            last = aajs.values[-1]
            volume = int(ret_volumes.values[-1])
            if volume < 10000:
                continue
            value_to_be_added = ""
            if last > upper and market != "SZ" and market != "SH":
                print(str(row['code']) + " " + str(row['name']) + " " + str(upper))
                value_to_be_added = "> " + str(upper)
                option_choice = "Short Call or Long Put"
                tickers_upper.append(row['code'])
                names_upper.append(row['name'])
                values_upper.append(value_to_be_added)
                volumes_upper.append(volume)
                if market != "SZ" and market != "SH":
                    options_upper.append(option_choice)
            elif last < lower:
                print(str(row['code']) + " " + str(row['name']) + " " + str(lower))
                value_to_be_added = "< " + str(lower)
                option_choice = "Long Call or Short Put"
                tickers_lower.append(row['code'])
                names_lower.append(row['name'])
                values_lower.append(value_to_be_added)
                volumes_lower.append(volume)
                if market != "SZ" and market != "SH":
                    options_lower.append(option_choice)
        except:
            print("Ticker " + str(row['code']) + " " + str(row['name']) + " has a problem")


    email_agent = EmailNotification()
    if market != "SZ" and market != "SH":
        data_lower = {'ticker': tickers_lower, 'name': names_lower, 'value': values_lower, 'volume' : volumes_lower, "option" : options_lower }
    else:
        data_lower = {'ticker': tickers_lower, 'name': names_lower, 'value': values_lower, 'volume': volumes_lower }

    df_to_write_lower = pd.DataFrame(data_lower)
    df_to_write_sorted_lower = df_to_write_lower.sort_values('volume', ascending=False)
    df_to_write_sorted_lower.to_csv(file_name + "_short.csv", index=True, sep=' ', columns=['ticker', 'name', 'value', 'volume'])
    df_to_write_sorted_lower.to_html(file_name + ".html")
    print(df_to_write_sorted_lower)
    content_lower = df_to_write_sorted_lower.to_html()

    if market != "SZ" and market != "SH":
        data_upper = {'ticker': tickers_upper, 'name': names_upper, 'value': values_upper, 'volume': volumes_upper, "option": options_upper}
    else:
        data_upper = {'ticker': tickers_upper, 'name': names_upper, 'value': values_upper, 'volume': volumes_upper}
    df_to_write_upper = pd.DataFrame(data_upper)
    df_to_write_sorted_upper = df_to_write_upper.sort_values('volume', ascending=False)
    df_to_write_sorted_upper.to_csv(file_name + "_short.csv", index=True, sep=' ',
                                    columns=['ticker', 'name', 'value', 'volume'])
    df_to_write_sorted_upper.to_html(file_name + ".html")
    content_upper = df_to_write_sorted_upper.to_html()

    if market == "US":
        for receipient in receipients:
           # email_agent.send_email(receipient, market + " candidates to LONG", content_lower, 'html')
            sm.send_mail(receipient, market + " candidates to LONG", content_lower)
            #email_agent.send_email(receipient, market + " candidates to SHORT", content_upper, 'html')
            sm.send_mail(receipient, market + " candidates to SHORT", content_upper)
    else:
        for receipient in receipients:
            #email_agent.send_email(receipient, market + " candidates to LONG", content_lower, 'html')
            sm.send_mail(receipient, market + " candidates to LONG", content_lower)

def find_all_good_candidates(quote_ctx, market, file_name, start_day, end_day):
    ret, data_frame = quote_ctx.get_stock_basicinfo(market=market, stock_type='STOCK')
    df = data_frame[data_frame['name'].str.contains("退市") == False]
    print(df)

    tickers = []
    names = []
    values = []
    for index, row in df.iterrows():
        good_stock = lo_sir_stock_pick(quote_ctx, row['code'], start_day, end_day)
        if good_stock:
            tickers.append(row['code'])
            names.append(row['name'])
    data = {'ticker': tickers, 'name': names}
    df_to_write = pd.DataFrame(data)
    df_to_write.to_csv(file_name, index=True, sep=' ', columns=['ticker', 'name'])

def process_single_df(dfret, market_snap_data):
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

    ma20 = ta.SMA(dfret['close'].values, timeperiod=20)
    df['DX'] = ta.EMA((df['NPDM'] - df['NMDM']) / (df['NMDM'] + df['NPDM']) * 100, MM)
    df['ADX'] = df['DX']
    df['ADXR'] = ta.EMA(df['ADX'], MM)
    df['AAJ'] = 0
    df['AAJ'] = ta.EMA(3 * df['ADX'] - 2 * df['ADXR'], 2)
    return df['AAJ'], ma20

def get_stocks_dmi_my_signal(quote_ctx, stock_ids, market_snap_data):
    now = datetime.now()
    start_day = (now - timedelta(90)).strftime("%Y-%m-%d")
    end_day = (now + timedelta(1)).strftime("%Y-%m-%d")

    stock_id_2_aaj = {}
    stock_id_2_ma20 = {}

    ret, dfrets = quote_ctx.get_history_kline(stock_ids, start_day, end_day, ktype='K_DAY', autype='qfq')  # 获取历史K线
    for idx, dfret in enumerate(dfrets):
        if not dfret.empty:
            curr_aaj, ma20 = process_single_df(dfret, market_snap_data)
            curr_stock_id = stock_ids[idx]
            stock_id_2_aaj[curr_stock_id] = curr_aaj
            stock_id_2_ma20[curr_stock_id] = ma20
        else:
            print("Failed to process " + stock_ids[idx])

    return stock_id_2_aaj, stock_id_2_ma20



if __name__ == "__main__":
    API_SVR_IP = '127.0.0.1'
    API_SVR_PORT = 11111
    SP_500_URL = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    DAO_URL = 'https://en.wikipedia.org/wiki/Dow_Jones_Industrial_Average'

    """
    sp500_tickers = get_index_components(SP_500_URL, 0, 'Ticker symbol')
    DAO_tickers = get_index_components(DAO_URL, 1, 'Symbol')
    bio_tech_array3 = bio_techs.split(',')
    ticker_groups = [sp500_tickers, DAO_tickers, bio_tech_array3]
    ticker_group_names = ["标普500成分股", "道指成分股", "生科股（做空为主）"]
    """

    quote_ctx = OpenQuoteContext(host=API_SVR_IP, port=API_SVR_PORT)  # 创建行情api

    #generate_list(quote_ctx, "SH", "沪市备选.csv", 90, -90)
    #print("Done with SH market")
    #generate_list(quote_ctx, "SZ", "深市备选.csv", 90, -90)
    #print("Done with SZ market")
    generate_list(quote_ctx, "HK", "香港备选.csv", 90, -90)
    print("Done with HK market")
    generate_list(quote_ctx, "US", "US_market_option_candidate", 100, -100)
    print("Done with US market")

    """
    lo_sir_stock_pick(quote_ctx, "US.AWX", "2017-12-04", "2018-07-24")
    # find_all_good_candidates(quote_ctx, 'US', "good_candidates_to_research.csv", "2017-01-01", "2018-07-24")
    find_all_good_candidates(quote_ctx, 'SH', "good_candidates_to_research_SH.csv", "2017-07-27", "2018-07-27")
    find_all_good_candidates(quote_ctx, 'SZ', "good_candidates_to_research_SZ.csv", "2017-07-27", "2018-07-27")
    find_all_good_candidates(quote_ctx, 'HK', "good_candidates_to_research_HK.csv", "2017-07-27", "2018-07-27")
    """
    quote_ctx.close()
