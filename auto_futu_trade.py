__author__ = 'lottiwang'
import tushare as ts
import talib as ta
import matplotlib.pyplot as plt
from futuquant.open_context import *
import datetime
import numpy as np
import pandas as pb
import matplotlib.dates as mdate
import matplotlib.ticker as ticker
import threading
import  time
from get_newhigh_stock import WhiteGuardStock



class AutoFutuTrade:
    def __init__(self):
        #self.quote_ctx = OpenQuoteContext(api_ip, api_port)
        self.wgs= WhiteGuardStock()
        pass


    def start_trade(self,stock_id):
        self.trade_code = stock_id
        self.timer = threading.Timer(1.0, self.auto_trade, [stock_id])
        self.timer.start()

    #测试用的函数
    def auto_trade(self,stock_id):
        #print("hello %s" % name)
        df=self.wgs.get_stock_dmi_my_signal_min(self.trade_code,15)
        print(df)
        self.timer = threading.Timer(1.0, self.auto_trade, [stock_id])
        self.timer.start()


    def make_order(self):
        pass


    def clear(self):
        self.wgs.clear_quote()




if __name__ == "__main__":
    aft = AutoFutuTrade()
    aft.start_trade('HK.00700')


