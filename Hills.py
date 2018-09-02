__author__ = 'lottiwang'
from datetime import datetime
import sys
import os
import time
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.dates as mdate
from futuquant import *
#path="/home/ubuntu/quant/quant/data/"
path="data/"



class CalculateHills:
    def __init__(self):
        pd.set_option('precision', 2)
        #self.df_total = pd.DataFrame({'basic':[238.2,200,161.8,150,138.2,100,76.4,61.8,50,38.2,23.6,0,-138.2,-150,-161.8,-200,-238.2]})
        self.df_total = pd.DataFrame({'basic':[161.8,150,138.2,100,76.4,61.8,50,38.2,23.6,0,-138.2,-150,-161.8]})
        self.testmode = False
    def start_connect(self,dst_ip,dst_port):
        self.quote_ctx = OpenQuoteContext(dst_ip, dst_port)

    def __del__(self):
        try:
            self.quote_ctx.close()
        except:
            pass

    def get_stock_hill(self,stock_ids):
        import datetime
        end_day=datetime.date(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day)
        days=30*7/5
        #考虑到周六日非交易
        start_day=end_day-datetime.timedelta(days)
        start_day=start_day.strftime("%Y-%m-%d")
        end_day=end_day.strftime("%Y-%m-%d")
        for stock_id in stock_ids:
            try:
                ret,df=self.quote_ctx.get_history_kline(stock_id,start_day,end_day,ktype=KLType.K_DAY, autype=AuType.QFQ)
                if ret == 0:
                    df['open'].astype('float')
                    df['close'].astype('float')
                    df['high'].astype('float')
                    df['low'].astype('float')
                    df['pe_ratio'].astype('float')
                    df['turnover_rate'].astype('float')
                    df['volume'].astype('float')
                    df['turnover'].astype('float')
                    df['change_rate'].astype('float')

                    high = df.iloc[-1]['high']
                    low = df.iloc[-1]['low']

                    val = high - low
                    self.df_total['mid'] = val * self.df_total['basic'] /100
                    self.df_total['hill'] = self.df_total['mid'] + low
                    print(self.df_total)

                    fig = plt.figure(figsize=[10,10])
                    #plt.plot(df.index,df['MACD'],label='macd dif')
                    #plt.plot(df.index,df['MACDsignal'],label='signal dea')
                    #df.index = df['time_key'].tolist()
                    plt.plot(df.index,df['close'] ,label='close')
                    plt.xlabel("Trading Cycle")
                    plt.ylabel("Price ")
                    plt.xlim((0, len(df.index)))
                    plt.title('%s Patron'%stock_id)
                    #plt.gca().xaxis.set_major_formatter(mdate.DateFormatter('%Y/%m/%d %HH%MM%SS'))
                    #plt.gca().xaxis.set_major_locator(mdate.DayLocator())
                    plt.gca().xaxis.set_major_locator(matplotlib.ticker.MultipleLocator(2))
                    #plt.gca().yaxis.set_major_locator(matplotlib.ticker.MultipleLocator(5000))
                    for index,row in self.df_total.iterrows():
                        value = row['hill']
                        #颜色代码可以换
                        percent = row['basic']
                        if percent > 0:
                            color = "#3383ba"
                            alpha=abs(percent)/self.df_total['basic'][0]
                        elif percent == 0:
                            color = "#eb8a35"
                            alpha = 1
                        else:
                            color = "#51b151"
                            alpha=abs(percent-100)/self.df_total['basic'][0]
                        plt.plot(df.index,[value]*len(df.index),alpha=alpha,color=color)
                        #print(self.df_total.loc[(self.df_total['hill'] == value),'basic'])
                        plt.text(df.index[-1], value, str(round(value,2)) + "(" + str(percent)  + "%)", ha='right', va='bottom', fontsize=8.5)
                        #df_storage_to_sell=wgs.df_total.loc[(wgs.df_total['DMI2'] == -1)]
                        #print(value)
                    plt.setp(plt.gca().get_xticklabels(), rotation=45)
                    plt.legend(loc='best')
                    #plt.plot(df)
                    #plt.grid()
                    #记得加这一句，不然不会显示图像
                    plt.savefig(os.path.join(path,stock_id+"Patron.png"))
                    #plt.show()


                else:
                    print(ret,df)



            except Exception as e:
                print("%s 错误：%s 返回结果%s"% (stock_id,e,self.df_total))
                return  False



if __name__ == "__main__":
    calhill=CalculateHills()
    calhill.start_connect('118.89.22.76',11111)
    calhill.get_stock_hill(['HK.800000','HK.00700','HK.02318'])
    '''
    get_ticker(quote_ctx,['HK.02318'])
    '''
    calhill.quote_ctx.close()