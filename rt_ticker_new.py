from datetime import  datetime,date,timedelta
import sys
import os,shutil
from futuquant import *
import pandas as pd
from time import localtime,strftime,time
import math
path_prefix= '/home/ubuntu/quant/quant/'
file_name= path_prefix+'data/tempfile/rtdata/rt_test'+strftime("%Y%m%d",localtime(time()))
path=path_prefix +"data/tempfile/rtdata/"
objcode='HK_FUTURE.999010'
class TickerTest(TickerHandlerBase):
    def __init__(self):
        self.df_total = pd.DataFrame()
        self.df_total_final = pd.DataFrame()

        self.count = 0
        self.buy = 0
        self.sell = 0
        self.write_header = True
        if strftime("%a",localtime(time())) == 'Mon':
            lastnight_file_name = path_prefix + 'data/tempfile/rtdata/rt_' + datetime.strptime(str(date.today()+timedelta(-3)),"%Y-%m-%d").strftime("%Y%m%d")
        else:
            lastnight_file_name = path_prefix + 'data/tempfile/rtdata/rt_' +datetime.strptime(str(date.today()+timedelta(-1)),"%Y-%m-%d").strftime("%Y%m%d")


        if (datetime.now().hour >= 17 or datetime.now().hour < 6):
            self.night = '_night'
            self.sell_lastnight = 0
            self.buy_lastnight = 0
            self.df_lastnight = pd.DataFrame()
        else:
            self.night=''
            self.df_lastnight= pd.read_csv(lastnight_file_name+"_night.csv")
            self.buy_lastnight = self.df_lastnight[(self.df_lastnight['ticker_direction'] == 'BUY') & (self.df_lastnight['code']== objcode)]['volume'].sum()
            self.sell_lastnight = self.df_lastnight[(self.df_lastnight['ticker_direction'] == 'SELL') & (self.df_lastnight['code']== objcode)]['volume'].sum()
            if not math.isnan(self.buy_lastnight):
                self.buy = self.buy_lastnight
            else:
                self.buy = 0
            if not math.isnan(self.sell_lastnight):
                self.sell = self.sell_lastnight
            else:
                self.sell = 0
        self.df_statistics = pd.read_csv(path_prefix + 'service/statistics.csv')
        # if len(self.df_statistics[(self.df_statistics['date'] == strftime("%Y/%m/%d",localtime(time())))].index ) <= 0: #默认把今天的添加上，如果没有的话
        #     self.df_statistics.loc[len(self.df_statistics.index)+1] = [strftime("%Y/%m/%d",localtime(time())),0,0,0.0,0,0,0.0]
        print(self.buy_lastnight,self.sell_lastnight,self.buy,self.sell)
        #print(self.df_statistics)
        #self.update_statistics()


    def on_recv_rsp(self, rsp_str):
        ret_code, data = super(TickerTest,self).on_recv_rsp(rsp_str)
        if ret_code != RET_OK:
            print("TickerTest: error, msg: %s" % data)
            return RET_ERROR, data
        print("TickerTest ", data) # RTDataTest自己的处理逻辑

        self.count = self.count + len(data.index)
        self.df_total=data
        self.df_total_final = self.df_total_final.append(data)




        # 检查是不是尾盘
        # ret, market_states = quote_ctx.get_global_state()
        if (datetime.now().hour > 16 and datetime.now().hour < 17) or (datetime.now().hour > 0 and datetime.now().hour < 1) :
            runtime_write = True
        else:
            runtime_write = False


        if (datetime.now().hour >= 17 or datetime.now().hour < 6):
            self.night = '_night'
        else:
            self.night=''
        new_file_name = file_name + self.night +".csv"


        
        #如果是收盘时间要退出一下
        if (datetime.now().hour == 16 and datetime.now().minute >= 31) or (datetime.now().hour == 1 and datetime.now().minute >= 1):
            self.df_total.to_csv(new_file_name,mode='a')
            self.df_total_final.to_csv(new_file_name+"_final.csv")
            rt_copyfile(new_file_name,new_file_name+".bak")
            print("Daily Market Close")
            rt.clear_quote()
            time.sleep(3)
            sys.exit(-1)

        #半小时写一次总的文件
        if (datetime.now().minute == 0 or datetime.now().minute == 30):
            self.df_total_final.to_csv(new_file_name+"_final.csv")

        # if not runtime_write:
        #     if self.count >= 50:
        #         self.df_total.to_csv(new_file_name,mode='a')
        #         self.count = 0
        # else:
        #     self.df_total.to_csv(new_file_name,mode='a')
        #     self.count = 0
        if self.write_header == True:
            self.df_total.to_csv(new_file_name,mode='a')
            self.write_header = False
        else:
            self.df_total.to_csv(new_file_name,mode='a',header=False)

        if len(self.df_total[(self.df_total['ticker_direction'] == 'BUY') & ( self.df_total['code']== objcode)].index) > 0:
            self.buy = self.buy + self.df_total[(self.df_total['ticker_direction'] == 'BUY') & ( self.df_total['code']== objcode)]['volume'].sum()
        if len(self.df_total[(self.df_total['ticker_direction'] == 'SELL') & ( self.df_total['code']== objcode)].index) > 0:
            self.sell = self.sell + self.df_total[(self.df_total['ticker_direction'] == 'SELL') & ( self.df_total['code']== objcode)]['volume'].sum()

        self.strcount = "本次tick买:" + str(self.df_total[(self.df_total['ticker_direction'] == 'BUY') & ( self.df_total['code']== objcode)]['volume'].sum()) + "卖:" +str(self.df_total[(self.df_total['ticker_direction'] == 'SELL') &  (self.df_total['code']== objcode)]['volume'].sum())
        print(self.buy,self.sell,self.strcount)
        self.render_html()
        return RET_OK, data

    def render_html(self):
        #   html='<html>\
        #   <meta http-equiv="refresh" content="15">\
        #   <head>\
        #     <title>期指即时交易查看</title>\
        #   </head>\
        #   <body>\
        #       <h1 align="center">当日即时数据</h1>\
        #       <h4 align="center" color="red">(数据包括上一个夜市，每15s刷新一次)</h4>\
        #       <table border="2" width="600" cellpadding="5" cellspacing="0" align="center">\
        #             <tr>\
        #                 <td>全天买</td>\
        #                 <td>' + str(self.buy) + '</td>\
        #             </tr>\
        #             <tr>\
        #                 <td>全天卖</td>\
        #                 <td>' + str(self.sell) + '</td>\
        #             </tr>\
        #         </table>\
        #   </body>\
        # </html>'
        # with open('service/static/total.html', 'w') as f:
        #    f.write(html)
        #self.update_statistics()
        with open('service/hsi.txt', 'w') as f2:
           f2.write(str(self.buy) + ',' +str(self.sell))


    def update_statistics(self):
        if len(self.df_statistics[(self.df_statistics['date'] == strftime("%Y/%m/%d",localtime(time())))].index ) <= 0: #默认把今天的添加上，如果没有的话
            total = len(self.df_statistics.index)
        else:
            total = len(self.df_statistics.index)-1
        last_close = 0
        curr_price = 0
        #获取当前最新价
        ret,data = rt.quote_ctx.get_market_snapshot(['HK.999010'])
        if ret == 0:
            curr_price = data.iloc[len(data.index)-1]['last_price']
        #开始获取上个交易日的收盘价
        end_day=date(date.today().year,date.today().month,date.today().day)
        days=7*7/5
        #考虑到周六日非交易
        start_day=end_day-timedelta(days)
        start_day = start_day.strftime("%Y-%m-%d")
        end_day=end_day.strftime("%Y-%m-%d")
        ret,trade_day=rt.quote_ctx.get_trading_days(Market.HK, start=start_day, end=end_day)
        ret, data, page_req_key = rt.quote_ctx.request_history_kline('HK.999010', start=trade_day[-1], end=trade_day[-1], max_count=1)
        if ret == 0:
            last_close = data.iloc[len(data.index)-1]['close']
        else:
            print("last_close error%s"%ret)
        dis = curr_price - last_close
        self.df_statistics.loc[total,'date']= strftime("%Y/%m/%d",localtime(time()))
        self.df_statistics.loc[total,'buy']=self.buy
        self.df_statistics.loc[total,'sell']=self.sell
        self.df_statistics.loc[total,'好淡比']=self.buy/self.sell
        self.df_statistics.loc[total,'净仓']=self.buy - self.sell
        self.df_statistics.loc[total,'涨跌额']=dis  #这里要取指数差额
        self.df_statistics.loc[total,'净张贡献']=dis/(self.buy - self.sell) #这里要除以差额
        self.df_statistics.to_csv(path_prefix + 'service/statistics.csv',index=False,float_format = '%.3f')
        #print(self.df_statistics)


def getDatetimeYesterday(days):
        today = getDatetimeToday() #datetime类型当前日期
        yesterday = today + timedelta(days = -1) #减去一天
        print(yesterday)
        return yesterday

def getDatetimeToday(self):
        t = date.today()  #date类型
        dt = datetime.strptime(str(t),'%Y-%m-%d') #date转str再转datetime
        return dt

def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end

def rt_copyfile(srcfile,dstfile):
    if not os.path.isfile(srcfile):
        print("%s not exist!"%(srcfile))
    else:
        fpath,fname=os.path.split(dstfile)    #分离文件名和路径
        if not os.path.exists(fpath):
            os.makedirs(fpath)                #创建路径
        shutil.copyfile(srcfile,dstfile)      #复制文件
        print("copy %s -> %s"%( srcfile,dstfile))

def get_ticker(ctx,stock_id_list):
    #quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    ctx.subscribe(stock_id_list, [SubType.TICKER])
    for id in stock_id_list:
        ret,df=rt.quote_ctx.get_rt_ticker(id, 1000)
        df.to_csv(os.path.join(path,"rt_"+ id +".csv"), index=True, sep=',',mode='a')
    rt.quote_ctx.close()


class rtCore:
    def __init__(self,dst_ip = '192.168.0.106',dst_port = 11111):
        # self.api_ip = dst_ip
        # self.api_port = dst_port
        # self.quote_ctx = OpenQuoteContext(self.api_ip, self.api_port)
        self.testmode = False
    def start_connect(self,dst_ip,dst_port):
        self.quote_ctx = OpenQuoteContext(dst_ip, dst_port)

    def clear_quote(self):
        self.quote_ctx.stop()
        self.quote_ctx.close()

    def __del__(self):
        try:
            self.quote_ctx.stop()
            self.quote_ctx.close()
        except:
            pass


rt = rtCore()
if __name__ == "__main__":
    # rt.start_connect('127.0.0.1',11111)
    # handler = TickerTest()
    # rt.quote_ctx.set_handler(handler)
    # #rt.quote_ctx.subscribe(['SZ.002475','SH.600519'], [SubType.TICKER])
    # rt.quote_ctx.subscribe(['HK.999010','HK.999011','HK.00700'], [SubType.TICKER])
    # rt.quote_ctx.start()
    # #time.sleep(15)

    print(getDatetimeYesterday)
