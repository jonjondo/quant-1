__author__ = 'lottiwang'
import tushare as ts
import talib as ta
import matplotlib.pyplot as plt
import datetime
info=ts.get_stock_basics()
def get_all_stock_id():
    #获取所有股票代码
    #for i in stock_info.index:
    #    print(i)
    print(info['name'])

def get_hs300s():
    df=ts.get_hs300s()
    #hs300=df['name'].values
    print(df)

def draw_single_stock_MA(stock_id):
    df=ts.get_k_data(stock_id,start='2018-01-01',end='2018-05-15')
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


def loop_all_stocks():
    for EachStockID in info.index:
         if is_break_high(EachStockID,60):
             print("High price on",)
             print(EachStockID,)
             print(info.ix[EachStockID]['name'])




def is_break_high(stockID,days):
    end_day=datetime.date(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day)
    days=days*7/5
    #考虑到周六日非交易
    start_day=end_day-datetime.timedelta(days)

    start_day=start_day.strftime("%Y-%m-%d")
    end_day=end_day.strftime("%Y-%m-%d")
    df=ts.get_h_data(stockID,start=start_day,end=end_day)

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















if __name__ == "__main__":
   #draw_single_stock_MA('002273')
   #get_all_stock_id()
   #ts.get_hs300s()
   #ts.get_industry_classified()
   loop_all_stocks()