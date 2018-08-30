import  datetime
import sys
import os
from futuquant import *
file_name= '/home/ubuntu/quant/quant/data/tempfile/rt_999010_'+time.strftime("%Y%m%d",time.localtime(time.time()))+'.csv'
path="/home/ubuntu/quant/quant/data/"

class TickerTest(TickerHandlerBase):
    def __init__(self):
        self.df_total = pd.DataFrame()
        self.count = 0
    def on_recv_rsp(self, rsp_str):
        ret_code, data = super(TickerTest,self).on_recv_rsp(rsp_str)
        if ret_code != RET_OK:
            print("TickerTest: error, msg: %s" % data)
            return RET_ERROR, data
        print("TickerTest ", data) # RTDataTest自己的处理逻辑

        self.count = self.count + len(data.index)
        self.df_total=self.df_total.append(data)
        #TODO： 冬令时和夏令时，而且应该用UTC时间，




        # 检查是不是尾盘
        # ret, market_states = quote_ctx.get_global_state()
        if (datetime.now().hour > 16 and datetime.now().hour < 17) or (datetime.now().hour > 0 and datetime.now().hour < 1) :
            runtime_write = True
        else:
            runtime_write = False

        if not runtime_write:
            if self.count >= 100:
                self.df_total.to_csv(file_name)
                self.count = 0
        else:
            self.df_total.to_csv(file_name)
            self.count = 0
        return RET_OK, data

def time_in_range(start, end, x):
    """Return true if x is in the range [start, end]"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end


def get_ticker(ctx,stock_id_list):
    #quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    ctx.subscribe(stock_id_list, [SubType.TICKER])

    for id in stock_id_list:
        ret,df=quote_ctx.get_rt_ticker(id, 1000)
        df.to_csv(os.path.join(path,"tempfile/rt_"+ id +".csv"), index=True, sep=',')
    quote_ctx.close()


if __name__ == "__main__":
    quote_ctx = OpenQuoteContext(host='118.89.22.76', port=11111)
    '''
    get_ticker(quote_ctx,['HK.02318'])
    '''
    handler = TickerTest()
    quote_ctx.set_handler(handler)
    quote_ctx.subscribe(['HK.999010','HK.999011'], [SubType.TICKER])
    quote_ctx.start()
    time.sleep(15)
