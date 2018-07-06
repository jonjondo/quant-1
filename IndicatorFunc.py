__author__ = 'wangpeng'
import tushare as ts
import talib as ta
import matplotlib.pyplot as plt
from futuquant.open_context import *
import datetime
import numpy as np
import pandas as pb
import chardet
import DataFrameToHtmlSytle as df2html
import sendmail as sm
import  time
import getopt




def draw_single_stock_MA(self,stock_id):
    #df=ts.get_k_data(stock_id,start='2018-01-01',end='2018-05-15')
    try:
        ret, df = self.quote_ctx.get_history_kline(stock_id, start='2018-01-01',end='2018-05-15', ktype='K_DAY', autype='qfq')  # 获取历史K线
        #提取收盘价
        closed=df['close'].values
         #获取均线的数据，通过timeperiod参数来分别获取 5,10,20 日均线的数据。
        ma5=ta.SMA(closed,timeperiod=5)
        ma10=ta.SMA(closed,timeperiod=10)
        ma20=ta.SMA(closed,timeperiod=20)
        print(closed)
        print(ma5)
        print(ma10)
        print(ma20)

        #通过plog函数可以很方便的绘制出每一条均线
        #plt.plot(closed)
        plt.plot(ma5)
        plt.plot(ma10)
        plt.plot(ma20)
        #添加网格，可有可无，只是让图像好看点
        plt.grid()
        #记得加这一句，不然不会显示图像
        plt.show()
    except Exception as e:
        print("错误：%s,返回结果%s"% (e,df))


def draw_single_stock_MACD(self,stock_id):
    try:
        ret, df = self.quote_ctx.get_history_kline(stock_id, start='2018-01-01',end='2018-05-15', ktype='K_DAY', autype='qfq')  # 获取历史K线
        #提取收盘价
        #closed=df['close'].values
        close = [float(x) for x in df['close']]
        #计算MACD
        df['EMA12'] = ta.EMA(np.array(close), timeperiod=12)
        df['EMA26'] = ta.EMA(np.array(close), timeperiod=26)
        # 调用talib计算MACD指标
        df['MACD'],df['MACDsignal'],df['MACDhist'] = ta.MACD(np.array(close),fastperiod=12, slowperiod=26, signalperiod=9)
        df['my_MACD'],df['my_MACDsignal'],df['my_MACDhist'] = self.my_macd(df['close'].values, fastperiod=6, slowperiod=12, signalperiod=9)
        df.tail(12)
        fig = plt.figure(figsize=[18,5])
        plt.plot(df.index,df['MACD'],label='DIF')
        plt.plot(df.index,df['MACDsignal'],label='DEA')
        #plt.plot(df.index,df['MACDhist'] ,label='MACD')
        #plt.plot(df.index,mydif,label='my dif')
        #plt.plot(df.index,mydea,label='my dea')
        plt.plot(df.index,df['my_MACDhist'],label='MACD')
        plt.legend(loc='best')
        plt.plot(df)
        plt.grid()
        #记得加这一句，不然不会显示图像
        plt.show()
    except Exception as e:
        print("%s 错误：%s 返回结果%s"% (stock_id,e,df))
        return  False

def get_index_stocks(self,ip, port, strcode):
        quote_ctx = OpenQuoteContext(ip, port)
        ret, data_frame = quote_ctx.get_plate_stock(strcode)
        quote_ctx.close()
        return ret, data_frame

def loop_all_stocks(self,index_code):
    ret,info = self.get_index_stocks(self.api_ip, self.api_port, index_code)
    print(info)
    for EachStockID in info.code:
         if self.is_hk_stock_break_high(EachStockID,60):
             print("%s %s"%(EachStockID,info[(info.code == EachStockID)].stock_name.tolist()[0]))
    print("---------------------------END-------------------------------")


def loop_all_hk_stocks_from_file(self,file_name,days):
    info = pb.read_csv(file_name)
    print("----------------------以下港股冲破%s日新高----------------------------"%(days))
    for EachStockID in info.code:
         if self.is_hk_stock_break_high(EachStockID,days):
         #if (EachStockID[-1] == '9'):
             print("%s %s"%(EachStockID,info[(info.code == EachStockID)].stock_name.tolist()[0]))
    print("---------------------------END-------------------------------")

def loop_all_hk_stocks(self,days):
    info = self.hk_stock_list
    print("----------------------以下港股冲破%s日新高----------------------------"%(days))
    for EachStockID in info.code:
         if self.is_hk_stock_break_high(EachStockID,days):
         #if (EachStockID[-1] == '9'):
             print("%s %s"%(EachStockID,info[(info.code == EachStockID)].stock_name.tolist()[0]))
    print("---------------------------END-------------------------------")

def loop_all_cn_stocks_from_file(self,data_source,file_name,days):
    info = pb.read_csv(file_name)
    print("----------------------以下沪深300符合条件%s----------------------------"%(days))
    for EachStockID in info.code:
        if data_source == 'tushare':
            if self.is_cn_stock_break_high_from_tushare(EachStockID,days):
                 print("%s %s"%(EachStockID,info[(info.code == EachStockID)].stock_name.tolist()[0]))
            sleep(5)
        elif data_source == 'futu':
            #if is_cn_stock_break_high_from_futu(EachStockID,days):
            if self.get_stock_kdj_buy_signal(EachStockID,days):
                print("%s %s"%(EachStockID,info[(info.code == EachStockID)].stock_name.tolist()[0]))
                info.loc[(info.code == EachStockID),'KDJ']=1
    print("---------------------------END-------------------------------")
    print(info.loc[info['KDJ'] == 1])

def get_stock_dmi_ta_signal(self,stock_id,days):
        SHORTMA = 5
        LONGMA = 20
        ADXPERIOD = 14

        ret, df = self.quote_ctx.get_history_kline(stock_id, start='2018-01-01',end='2018-05-27', ktype='K_DAY', autype='qfq')  # 获取历史K线
        if not df.empty:
            high=df['high'].values
            low=df['low'].values
            close=df['close'].values
            df['ADX'] = ta.ADX(high,low,close,ADXPERIOD)
            df['ADXR'] = ta.ADXR(high,low,close,ADXPERIOD)
            df['PLUS_DI'] = ta.PLUS_DI(high,low,close,ADXPERIOD)
            df['MINUS_DI'] = ta.MINUS_DI(high,low,close,ADXPERIOD)
            #df['ADX'] = ta.ADX(high,low,close,ADXPERIOD)
            #df['ADXR'] = ta.ADXR(high,low,close,ADXPERIOD)
            #df['AAJ'] = 3*df['ADX']-2*df['ADXR']
            df['SHORTMA'] = ta.SMA(close,SHORTMA)
            df['LONGMA'] = ta.SMA(close,LONGMA)
            fig = plt.figure(figsize=[18,5])
            #plt.plot(df.index,df['MACD'],label='macd dif')
            #plt.plot(df.index,df['MACDsignal'],label='signal dea')
            plt.plot(df.index,df['ADX'] ,label='ADX')
            plt.plot(df.index,df['ADXR'] ,label='ADXR')
            plt.plot(df.index,df['PLUS_DI'] ,label='PLUS_DI')
            plt.plot(df.index,df['MINUS_DI'] ,label='MINUS_DI')
            plt.plot(df.index,df['AAJ'] ,label='AAJ')
            plt.legend(loc='best')
            #plt.plot(df)
            plt.grid()
            #记得加这一句，不然不会显示图像
            plt.show()
