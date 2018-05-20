__author__ = 'wangpeng'
import tushare as ts
import talib as ta
import matplotlib.pyplot as plt
from futuquant.open_context import *
import datetime
import numpy as np
import pandas as pb


api_ip = '119.29.141.202'#'119.29.141.202'这里要使用本地客户端
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

def my_macd(price, fastperiod=12, slowperiod=26, signalperiod=9):
    macdDIFF, macdDEA, macd = ta.MACDEXT(price, fastperiod=fastperiod, fastmatype=1, slowperiod=slowperiod, slowmatype=1, signalperiod=signalperiod, signalmatype=1)
    macd = macd * 2
    return macdDIFF, macdDEA, macd

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
        df['my_MACD'],df['my_MACDsignal'],df['my_MACDhist'] = my_macd(df['close'].values, fastperiod=6, slowperiod=12, signalperiod=9)
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

def is_hk_stock_break_high(stock_id,days):
    end_day=datetime.date(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day)
    days=days*7/5
    #考虑到周六日非交易
    start_day=end_day-datetime.timedelta(days)

    start_day=start_day.strftime("%Y-%m-%d")
    end_day=end_day.strftime("%Y-%m-%d")
    try:
        ret,df=quote_ctx.get_history_kline(stock_id,start=start_day,end=end_day,ktype='K_DAY', autype='qfq')
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
            #print("代码：%s 今日最高:%0.2f 阶段最高 %0.2f"%(stock_id,today_high,period_high))
            return True
        else:
            return False
    except Exception as e:
        print("%s 错误：%s 返回结果%s"% (stock_id,e,df))
        return  False

def is_cn_stock_break_high_from_futu(stock_id,days):
    end_day=datetime.date(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day)
    days=days*7/5
    #考虑到周六日非交易
    start_day=end_day-datetime.timedelta(days)

    start_day=start_day.strftime("%Y-%m-%d")
    end_day=end_day.strftime("%Y-%m-%d")
    try:
        ret,df=quote_ctx.get_history_kline(stock_id,start=start_day,end=end_day,ktype='K_DAY', autype='qfq')
        if not df.empty:
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
                #print("代码：%s 今日最高:%0.2f 阶段最高 %0.2f"%(stock_id,today_high,period_high))
                return True
            else:
                return False
    except Exception as e:
        print("%s 错误：%s 返回结果%s in %s"% (stock_id,e,df,"is_cn_stock_break_high_from_futu"))
        return  False

def is_cn_stock_break_high_from_tushare(stock_id,days):
    end_day=datetime.date(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day)
    days=days*7/5
    #考虑到周六日非交易
    start_day=end_day-datetime.timedelta(days)

    start_day=start_day.strftime("%Y-%m-%d")
    end_day=end_day.strftime("%Y-%m-%d")

    try:
        df=ts.get_h_data(stock_id[3:],start=start_day,end=end_day)
        #print(df)
        period_high=df['high'].max()
        #print period_high
        today_high=df.iloc[0]['high']
        #这里不能直接用 .values
        #如果用的df【：1】 就需要用.values
        #print today_high
        if today_high>=period_high:
            #df.to_csv('d:/high.csv')
            return True
        else:
            return False
    except Exception as e:
        print("%s 错误：%s 返回结果%s"% (stock_id,e,df))
        return  False

def get_index_stocks(ip, port, strcode):
    quote_ctx = OpenQuoteContext(ip, port)
    ret, data_frame = quote_ctx.get_plate_stock(strcode)
    quote_ctx.close()
    return ret, data_frame

def loop_all_stocks(index_code):
    ret,info = get_index_stocks(api_ip, api_port, index_code)
    print(info)
    for EachStockID in info.code:
         if is_hk_stock_break_high(EachStockID,60):
             print("%s %s"%(EachStockID,info[(info.code == EachStockID)].stock_name.tolist()[0]))
    print("---------------------------END-------------------------------")


def loop_all_hk_stocks_from_file(file_name,days):
    info = pb.read_csv(file_name)
    print("----------------------以下港股冲破%s日新高----------------------------"%(days))
    for EachStockID in info.code:
         if is_hk_stock_break_high(EachStockID,days):
         #if (EachStockID[-1] == '9'):
             print("%s %s"%(EachStockID,info[(info.code == EachStockID)].stock_name.tolist()[0]))
    print("---------------------------END-------------------------------")

def loop_all_cn_stocks_from_file(data_source,file_name,days):
    info = pb.read_csv(file_name)
    print("----------------------以下沪深300符合条件%s----------------------------"%(days))
    for EachStockID in info.code:
        if data_source == 'tushare':
            if is_cn_stock_break_high_from_tushare(EachStockID,days):
                 print("%s %s"%(EachStockID,info[(info.code == EachStockID)].stock_name.tolist()[0]))
            sleep(5)
        elif data_source == 'futu':
            #if is_cn_stock_break_high_from_futu(EachStockID,days):
            if get_stock_kdj_buy_signal(EachStockID,days):
                print("%s %s"%(EachStockID,info[(info.code == EachStockID)].stock_name.tolist()[0]))
                info.loc[(info.code == EachStockID),'KDJ']=1
    print("---------------------------END-------------------------------")
    print(info.loc[info['KDJ'] == 1])


def get_stock_kdj_buy_signal(stock_id,days):
    # 计算KDJ指标
    end_day=datetime.date(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day)
    days=days*7/5
    #考虑到周六日非交易
    start_day=end_day-datetime.timedelta(days)

    start_day=start_day.strftime("%Y-%m-%d")
    end_day=end_day.strftime("%Y-%m-%d")
    try:
        ret,stock_data=quote_ctx.get_history_kline(stock_id,start=start_day,end=end_day,ktype='K_DAY', autype='qfq')
        if not stock_data.empty:
            low_list = pd.rolling_min(stock_data['low'], 9)
            low_list.fillna(value=pd.expanding_min(stock_data['low']), inplace=True)
            high_list = pd.rolling_max(stock_data['high'], 9)
            high_list.fillna(value=pd.expanding_max(stock_data['high']), inplace=True)
            rsv = (stock_data['close'] - low_list) / (high_list - low_list) * 100
            stock_data['KDJ_K'] = pd.ewma(rsv, com=2)
            stock_data['KDJ_D'] = pd.ewma(stock_data['KDJ_K'], com=2)
            stock_data['KDJ_J'] = 3 * stock_data['KDJ_K'] - 2 * stock_data['KDJ_D']
            # 计算KDJ指标金叉、死叉情况
            stock_data['KDJ_金叉死叉'] = ''
            kdj_position_gold = (stock_data['KDJ_K'] > stock_data['KDJ_D']) & (stock_data['KDJ_D'] < 25)
            kdj_position_die = (stock_data['KDJ_K'] > stock_data['KDJ_D']) & (stock_data['KDJ_D'] > 75 )
            stock_data.loc[kdj_position_gold[(kdj_position_gold == True) & (kdj_position_gold.shift() == False)].index, 'KDJ_金叉死叉'] = 1
            stock_data.loc[kdj_position_die[(kdj_position_die == False) & (kdj_position_die.shift() == True)].index, 'KDJ_金叉死叉'] = -1
            #stock_data.to_csv("00700KDJ.csv", index=True, sep=',')
            if len(stock_data.index) > 3:
                #过去三天出了金叉,且过去五天有J无限接近底部，同时没有扭头向下的话，标为1.
                if (stock_data.iloc[-1]['KDJ_金叉死叉'] == 1 or stock_data.iloc[-2]['KDJ_金叉死叉'] == 1 or stock_data.iloc[-3]['KDJ_金叉死叉'] == 1) and \
                        (stock_data.iloc[-1]['KDJ_J'] < 1 or stock_data.iloc[-2]['KDJ_J'] < 1 or stock_data.iloc[-3]['KDJ_J'] < 1 or stock_data.iloc[-4]['KDJ_J'] < 1 or stock_data.iloc[-5]['KDJ_J'] < 1) and\
                        (stock_data.iloc[-1]['KDJ_J'] >= stock_data.iloc[-1]['KDJ_K']):
                    #print("股票%s 近三日内出现KDJ金叉"%(stock_id))
                    return  True
                else:
                    return  False
    except Exception as e:
        print("%s 错误：%s 返回结果%s in %s"% (stock_id,e,stock_data,"get_stock_kdj_buy_signal"))
        return  False

def get_stock_macd_buy_signal(stock_id,days):
    pass


if __name__ == "__main__":
    #draw_single_stock_MACD('HK.00700')
    #loop_all_hk_stocks_from_file("HSIIndexList.csv",60)
    loop_all_cn_stocks_from_file("futu","stocklist.csv",30)
    #loop_all_stocks('HK.800000')
    #get_stock_kdj_buy_signal('HK.03883',30)