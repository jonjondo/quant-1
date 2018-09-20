import  datetime
import sys
import os,shutil
from futuquant import *
import pandas as pd
from time import localtime,strftime,time
path_prefix= '/home/ubuntu/quant/quant/'
file_name= path_prefix+'data/tempfile/rtdata/rt_test'+strftime("%Y%m%d",localtime(time()))
path=path_prefix +"data/tempfile/rtdata/"
class TickerTest(TickerHandlerBase):
    def __init__(self):
        self.df_total = pd.DataFrame()
        self.count = 0
        self.buy = 0
        self.sell = 0
        self.write_header = True
        if strftime("%a",localtime(time())) == 'Mon':
            lastnight_file_name = path_prefix + 'data/tempfile/rtdata/rt_' + str(int(strftime("%Y%m%d",localtime(time())))-3)
        else:
            lastnight_file_name = path_prefix + 'data/tempfile/rtdata/rt_' + str(int(strftime("%Y%m%d",localtime(time())))-1)

        if (datetime.now().hour >= 17 or datetime.now().hour < 6):
            self.night = '_night'
            self.sell_lastnight = 0
            self.buy_lastnight = 0
            self.df_lastnight = pd.DataFrame()
        else:
            self.night=''
            self.df_lastnight= pd.read_csv(lastnight_file_name+"_night.csv")
            self.buy_lastnight = self.df_lastnight[(self.df_lastnight['ticker_direction'] == 'BUY') & (self.df_lastnight['code']== 'HK_FUTURE.999010')]['volume'].sum()
            self.sell_lastnight = self.df_lastnight[(self.df_lastnight['ticker_direction'] == 'SELL') & (self.df_lastnight['code']== 'HK_FUTURE.999010')]['volume'].sum()
            self.buy = self.buy_lastnight
            self.sell = self.sell_lastnight
        print(self.buy_lastnight,self.sell_lastnight,self.buy,self.sell)

    def on_recv_rsp(self, rsp_str):
        ret_code, data = super(TickerTest,self).on_recv_rsp(rsp_str)
        if ret_code != RET_OK:
            print("TickerTest: error, msg: %s" % data)
            return RET_ERROR, data
        print("TickerTest ", data) # RTDataTest自己的处理逻辑

        self.count = self.count + len(data.index)
        self.df_total=data
        #TODO： 冬令时和夏令时，而且应该用UTC时间，




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
            rt_copyfile(new_file_name,new_file_name+".bak")
            print("Daily Market Close")
            rt.clear_quote()
            time.sleep(3)
            sys.exit(-1)
        
        

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

        if len(self.df_total[(self.df_total['ticker_direction'] == 'BUY') & ( self.df_total['code']== 'HK_FUTURE.999010')].index) > 0:
            self.buy = self.buy + self.df_total[(self.df_total['ticker_direction'] == 'BUY') & ( self.df_total['code']== 'HK_FUTURE.999010')]['volume'].sum()
        if len(self.df_total[(self.df_total['ticker_direction'] == 'SELL') & ( self.df_total['code']== 'HK_FUTURE.999010')].index) > 0:
            self.sell = self.sell + self.df_total[(self.df_total['ticker_direction'] == 'SELL') & ( self.df_total['code']== 'HK_FUTURE.999010')]['volume'].sum()

        self.strcount = "本次--买:" + str(self.df_total[(self.df_total['ticker_direction'] == 'BUY') & ( self.df_total['code']== 'HK_FUTURE.999010')]['volume'].sum()) + "卖:" +str(self.df_total[(self.df_total['ticker_direction'] == 'SELL') &  (self.df_total['code']== 'HK_FUTURE.999010')]['volume'].sum())
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
        with open('service/hsi.txt', 'w') as f2:
           f2.write(str(self.buy) + ',' +str(self.sell))



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
    #quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    rt.start_connect('127.0.0.1',11111)
    '''
    get_ticker(quote_ctx,['HK.02318'])
    '''
    handler = TickerTest()
    rt.quote_ctx.set_handler(handler)
    rt.quote_ctx.subscribe(['HK.999010','HK.999011','HK.00700'], [SubType.TICKER])
    rt.quote_ctx.start()
    #time.sleep(15)
