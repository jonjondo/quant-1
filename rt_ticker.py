import time
from futuquant import *
file_name= '/home/ubuntu/quant/quant/data/tempfile/rt_999010_'+time.strftime("%Y%m%d",time.localtime(time.time()))+'.csv'
class TickerTest(TickerHandlerBase):
    def __init__(self):
        self.df_total = pd.DataFrame() 
    def on_recv_rsp(self, rsp_str):
        ret_code, data = super(TickerTest,self).on_recv_rsp(rsp_str)
        if ret_code != RET_OK:
            print("TickerTest: error, msg: %s" % data)
            return RET_ERROR, data
        print("TickerTest ", data) # RTDataTest自己的处理逻辑
        self.df_total=self.df_total.append(data)
        self.df_total.to_csv(file_name)
        return RET_OK, data

quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
handler = TickerTest()
quote_ctx.set_handler(handler)
quote_ctx.subscribe(['HK.999010','HK.999011'], [SubType.TICKER])
quote_ctx.start()
time.sleep(15)
