__author__ = 'lottiwang'
from futuquant import  *
import  pandas as pd


class WarrantInfoCore:
    def __init__(self,dst_ip = '192.168.0.106',dst_port = 11111):
        # self.api_ip = dst_ip
        # self.api_port = dst_port
        # self.quote_ctx = OpenQuoteContext(self.api_ip, self.api_port)
        self.testmode = False
    def start_connect(self,dst_ip,dst_port):
        self.quote_ctx = OpenQuoteContext(dst_ip, dst_port)


    def getStockWarrantList(self,stock_id):
        #print(quote_ctx.get_referencestock_list('HK.00700', SecurityReferenceType.WARRANT))
        ret,df=self.quote_ctx.get_referencestock_list(stock_id,SecurityReferenceType.WARRANT)
        if ret == 0:
            return df
        else:
            return ret
    def getWarrantInfo(self,WarrantList):
        df_total_snap= pd.DataFrame()
        for i in range(0,len(WarrantList),199):
            if i + 199 > len(WarrantList):
                ret0, dfret_snap = self.quote_ctx.get_market_snapshot(WarrantList[i:])
            else:
                ret0, dfret_snap = self.quote_ctx.get_market_snapshot(WarrantList[i:i+199])
            if ret0 != 0:
                print("get market snapshot error %s,%s"%(dfret_snap,i))
            else:
                df_total_snap=df_total_snap.append(dfret_snap, ignore_index=True)
        return df_total_snap

    def clear_quote(self):
        self.quote_ctx.close()

    def __del__(self):
        try:
            self.quote_ctx.close()
        except:
            pass








if __name__ == "__main__":
    #quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
    wc=WarrantInfoCore()
    wc.start_connect('118.89.22.76',11111)
    df = wc.getStockWarrantList('HK.00700')
    df_detail = wc.getWarrantInfo(df['code'].tolist())
    df_detail.to_csv("data/tempfile/00700warrantdetail.csv")
    #time.sleep(15)