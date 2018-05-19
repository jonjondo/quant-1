__author__ = 'wangpeng'
import tushare as ts
import talib as ta
import matplotlib.pyplot as plt
from futuquant.open_context import *
import datetime
import numpy as np


api_ip = 'localhost' #''119.29.141.202'这里要使用本地客户端
api_port = 11111
quote_ctx = OpenQuoteContext(api_ip, api_port)

#quote_ctx.get_history_kline(code, start=None, end=None, ktype='K_DAY', autype='qfq')  # 获取历史K线
def draw_single_stock_MA(stock_id):
    #df=ts.get_k_data(stock_id,start='2018-01-01',end='2018-05-15')
    try:
        ret, df = quote_ctx.get_history_kline(stock_id, start='2018-01-01',end='2018-05-15', ktype='K_DAY', autype='qfq')  # 获取历史K线
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
def myMACD(price, fastperiod=12, slowperiod=26, signalperiod=9):
    ewma12 = pd.ewma(price,span=fastperiod)
    ewma60 = pd.ewma(price,span=slowperiod)
    dif = ewma12-ewma60
    dea = pd.ewma(dif,span=signalperiod)
    bar = (dif-dea) #有些地方的bar = (dif-dea)2，但是talib中MACD的计算是bar = (dif-dea)1
    return dif,dea,bar,ewma12,ewma60

def draw_single_stock_MACD(stock_id):
    try:
        ret, df = quote_ctx.get_history_kline(stock_id, start='2018-01-01',end='2018-05-15', ktype='K_DAY', autype='qfq')  # 获取历史K线
        #提取收盘价
        #closed=df['close'].values
        close = [float(x) for x in df['close']]
        #计算MACD
        df['EMA12'] = ta.EMA(np.array(close), timeperiod=12)
        df['EMA26'] = ta.EMA(np.array(close), timeperiod=26)
        # 调用talib计算MACD指标
        df['MACD'],df['MACDsignal'],df['MACDhist'] = ta.MACD(np.array(close),fastperiod=12, slowperiod=26, signalperiod=9)
        #mydif,mydea,mybar = myMACD(df['close'].values, fastperiod=12, slowperiod=26, signalperiod=9)
        #df.tail(12)
        fig = plt.figure(figsize=[18,5])
        plt.plot(df.index,df['MACD'],label='macd dif')
        plt.plot(df.index,df['MACDsignal'],label='signal dea')
        plt.plot(df.index,df['MACDhist'] ,label='MACD')
        # plt.plot(df.index,mydif,label='my dif')
        # plt.plot(df.index,mydea,label='my dea')
        # plt.plot(df.index,mybar,label='my bar')
        plt.legend(loc='best')
        #plt.plot(df)
        plt.grid()
        #记得加这一句，不然不会显示图像
        plt.show()
    except Exception as e:
        print("错误：%s,返回结果%s"% (e,df))

def is_break_high(stockID,days):
    end_day=datetime.date(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day)
    days=days*7/5
    #考虑到周六日非交易
    start_day=end_day-datetime.timedelta(days)

    start_day=start_day.strftime("%Y-%m-%d")
    end_day=end_day.strftime("%Y-%m-%d")
    ret,df=quote_ctx.get_history_kline(stockID,start=start_day,end=end_day,ktype='K_DAY', autype='qfq')
    df['open'].astype('float')
    df['close'].astype('float')
    df['high'].astype('float')
    df['low'].astype('float')
    df['pe_ratio'].astype('float')
    df['turnover_rate'].astype('float')
    df['volume'].astype('float')
    df['turnover'].astype('float')
    df['change_rate'].astype('float')
    period_high=df['high'].max()
    #print period_high
    today_high=df.iloc[len(df)-1]['high']
    #这里不能直接用 .values
    #如果用的df【：1】 就需要用.values
    #print today_high
    if today_high>=period_high:
        #df.to_csv('d:/high.csv')
        print("代码：%s 今日最高:%0.2f 阶段最高 %0.2f"%(stockID,today_high,period_high))
        return True
    else:
        return False
def get_index_stocks(ip, port, strcode):
    quote_ctx = OpenQuoteContext(ip, port)
    ret, data_frame = quote_ctx.get_plate_stock(strcode)
    quote_ctx.close()
    return ret, data_frame

def loop_all_stocks(index_code):
    ret,info = get_index_stocks(api_ip, api_port, index_code)
    print(info)
    for EachStockID in info.code:
         if is_break_high(EachStockID,60):
             print("High price on %s"%(EachStockID))
             #print(EachStockID,)
             #print(info[(info.code == EachStockID)].stock_name.tolist()[0])
    print("---------------------------END-------------------------------")





if __name__ == "__main__":
    api_ip = 'localhost' #''119.29.141.202'这里要使用本地客户端
    api_port = 11111
    draw_single_stock_MACD('HK.00700')
    #loop_all_stocks('HK.800000')