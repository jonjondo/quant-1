__author__ = 'wangpeng'
import tushare as ts
import talib as ta
import matplotlib.pyplot as plt
from futuquant.open_context import *
import datetime
import numpy as np
import pandas as pb
import chardet
from PyQt5.QtCore import QThread,pyqtSignal,QDateTime

class WhiteGuardStockCore4UI:
    update_progress = pyqtSignal(str)
    update_info = pyqtSignal(str)
    def __init__(self,dst_ip = '192.168.0.106',dst_port = 11111):
        # self.api_ip = dst_ip
        # self.api_port = dst_port
        # self.quote_ctx = OpenQuoteContext(self.api_ip, self.api_port)
        self.df_total = pd.DataFrame()
        self.notice_msg = []

    def start_connect(self,dst_ip,dst_port):
        self.quote_ctx = OpenQuoteContext(dst_ip, dst_port)

    def init_cn_stock(self,cn_stock_file_name):
        self.cn_stock_list = pb.read_csv(cn_stock_file_name,encoding='GBK')
    def init_hk_stock(self,hk_stock_file_name):
        self.hk_stock_list = pb.read_csv(hk_stock_file_name)

    def init_us_stock(self,us_stock_file_name):
        self.us_stock_list = pb.read_csv(us_stock_file_name)

    def start_hk_market(self,trade_env):
        self.trade_ctx = OpenHKTradeContext(host=self.api_ip, port=self.api_port)
    def start_us_market(self,trade_env):
        if trade_env != 0:
            raise Exception("美股交易接口不支持仿真环境")
        self.trade_ctx = OpenUSTradeContext(host=self.api_ip, port=self.api_port)
    def clear_quote(self):
        self.quote_ctx.close()

    def __del__(self):
        self.quote_ctx.close()




    def draw_single_stock_MA(self,stock_id):
        #df=ts.get_k_data(stock_id,start='2018-01-01',end='2018-05-15')
        try:
            ret, df = self.quote_ctx.get_history_kline(stock_id, start='2018-01-01',end='2018-05-15', ktype='K_DAY', autype='qfq')  # 获取历史K线
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

    def my_macd(self,price, fastperiod=12, slowperiod=26, signalperiod=9):
        macdDIFF, macdDEA, macd = ta.MACDEXT(price, fastperiod=fastperiod, fastmatype=1, slowperiod=slowperiod, slowmatype=1, signalperiod=signalperiod, signalmatype=1)
        macd = macd * 2
        return macdDIFF, macdDEA, macd

    def draw_single_stock_MACD(self,stock_id):
        try:
            ret, df = self.quote_ctx.get_history_kline(stock_id, start='2018-01-01',end='2018-05-15', ktype='K_DAY', autype='qfq')  # 获取历史K线
            #提取收盘价
            #closed=df['close'].values
            close = [float(x) for x in df['close']]
            #计算MACD
            df['EMA12'] = ta.EMA(np.array(close), timeperiod=12)
            df['EMA26'] = ta.EMA(np.array(close), timeperiod=26)
            # 调用talib计算MACD指标
            df['MACD'],df['MACDsignal'],df['MACDhist'] = ta.MACD(np.array(close),fastperiod=12, slowperiod=26, signalperiod=9)
            df['my_MACD'],df['my_MACDsignal'],df['my_MACDhist'] = self.my_macd(df['close'].values, fastperiod=6, slowperiod=12, signalperiod=9)
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

    def is_hk_stock_break_high(self,stock_id,days):
        end_day=datetime.date(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day)
        days=days*7/5
        #考虑到周六日非交易
        start_day=end_day-datetime.timedelta(days)

        start_day=start_day.strftime("%Y-%m-%d")
        end_day=end_day.strftime("%Y-%m-%d")
        try:
            ret,df=self.quote_ctx.get_history_kline(self,stock_id,start=start_day,end=end_day,ktype='K_DAY', autype='qfq')
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

    def is_cn_stock_break_high_from_futu(self,stock_id,days):
        end_day=datetime.date(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day)
        days=days*7/5
        #考虑到周六日非交易
        start_day=end_day-datetime.timedelta(days)

        start_day=start_day.strftime("%Y-%m-%d")
        end_day=end_day.strftime("%Y-%m-%d")
        try:
            ret,df=self.quote_ctx.get_history_kline(stock_id,start=start_day,end=end_day,ktype='K_DAY', autype='qfq')
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

    def is_cn_stock_break_high_from_tushare(self,stock_id,days):
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

    def get_index_stocks(self,ip, port, strcode):
        quote_ctx = OpenQuoteContext(ip, port)
        ret, data_frame = quote_ctx.get_plate_stock(strcode)
        quote_ctx.close()
        return ret, data_frame

    def loop_all_stocks(self,index_code):
        ret,info = self.get_index_stocks(self.api_ip, self.api_port, index_code)
        print(info)
        for EachStockID in info.code:
             if self.is_hk_stock_break_high(EachStockID,60):
                 print("%s %s"%(EachStockID,info[(info.code == EachStockID)].stock_name.tolist()[0]))
        print("---------------------------END-------------------------------")


    def loop_all_hk_stocks_from_file(self,file_name,days):
        info = pb.read_csv(file_name)
        print("----------------------以下港股冲破%s日新高----------------------------"%(days))
        for EachStockID in info.code:
             if self.is_hk_stock_break_high(EachStockID,days):
             #if (EachStockID[-1] == '9'):
                 print("%s %s"%(EachStockID,info[(info.code == EachStockID)].stock_name.tolist()[0]))
        print("---------------------------END-------------------------------")

    def loop_all_hk_stocks(self,days):
        info = self.hk_stock_list
        print("----------------------以下港股冲破%s日新高----------------------------"%(days))
        for EachStockID in info.code:
             if self.is_hk_stock_break_high(EachStockID,days):
             #if (EachStockID[-1] == '9'):
                 print("%s %s"%(EachStockID,info[(info.code == EachStockID)].stock_name.tolist()[0]))
        print("---------------------------END-------------------------------")

    def loop_all_cn_stocks_from_file(self,data_source,file_name,days):
        info = pb.read_csv(file_name)
        print("----------------------以下沪深300符合条件%s----------------------------"%(days))
        for EachStockID in info.code:
            if data_source == 'tushare':
                if self.is_cn_stock_break_high_from_tushare(EachStockID,days):
                     print("%s %s"%(EachStockID,info[(info.code == EachStockID)].stock_name.tolist()[0]))
                sleep(5)
            elif data_source == 'futu':
                #if is_cn_stock_break_high_from_futu(EachStockID,days):
                if self.get_stock_kdj_buy_signal(EachStockID,days):
                    print("%s %s"%(EachStockID,info[(info.code == EachStockID)].stock_name.tolist()[0]))
                    info.loc[(info.code == EachStockID),'KDJ']=1
        print("---------------------------END-------------------------------")
        print(info.loc[info['KDJ'] == 1])

    def loop_all_stocks(self,data_source,days,market):
        if market == 0: #沪深
            info = self.cn_stock_list
            #total_stock_count = len(self.cn_stock_list.index)
        elif market == 1: #香港
            info = self.hk_stock_list
            #total_stock_count = len(self.hk_stock_list.index)
        elif market == 2:
            info = self.us_stock_list
            #total_stock_count = len(self.us_stock_list.index)
        else:
            info = self.cn_stock_list
        total_stock_count = len(info.index)
        print("----------------------以下符合条件----------------------------")
        end_day=datetime.date(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day)
        end_day=end_day.strftime("%Y-%m-%d")
        #df_last_ret = pd.DataFrame()
        cur_pos = 0
        for EachStockID in info.code:
            cur_pos = cur_pos +1
            self.update_progress.emit(str(cur_pos *100 /total_stock_count))
            if data_source == 'tushare':
                if self.is_cn_stock_break_high_from_tushare(EachStockID,days):
                     print("%s %s"%(EachStockID,info[(info.code == EachStockID)].stock_name.tolist()[0]))
                sleep(5)
            elif data_source == 'futu':
                #if is_cn_stock_break_high_from_futu(EachStockID,days):
                #print("[%s]正在处理%s....."%(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())),EachStockID))
                #ret,stock_data=self.quote_ctx.get_history_kline(EachStockID,start='2018-01-01',end=end_day,ktype='K_DAY', autype='qfq')
                #df=self.get_stock_my_schedule_signal(stock_data)
                #print(df.iloc[-1:])
                #df_last_ret=df_last_ret.append(df.iloc[-1:],ignore_index=True)
                # info['KDJ'] = 0
                # info['DMI2'] = 0
                # info['MACROSS'] = 0
                # info['MACD'] = 0

                if self.is_cn_stock_break_high_from_futu(EachStockID,days*2) == True:  #得算两个月的新高才靠谱
                    print("%s %s[两月前高]"%(EachStockID,info[(info.code == EachStockID)].stock_name.tolist()[0]))
                    self.notice_msg.append("%s %s[两月前高]\n"%(EachStockID,info[(info.code == EachStockID)].stock_name.tolist()[0]))
                    info.loc[(info.code == EachStockID),'NEWHIGH']=1

                if self.get_stock_kdj_buy_signal(EachStockID,days) == True:
                    print("%s %s[KDJ金叉]"%(EachStockID,info[(info.code == EachStockID)].stock_name.tolist()[0]))
                    self.notice_msg.append("%s %s[KDJ金叉]\n"%(EachStockID,info[(info.code == EachStockID)].stock_name.tolist()[0]))
                    info.loc[(info.code == EachStockID),'KDJ']=1
                if self.get_stock_ma_cross_signal(EachStockID,days) == True:
                    info.loc[(info.code == EachStockID),'MACROSS']=1
                    print("%s %s[MA底部穿越]"%(EachStockID,info[(info.code == EachStockID)].stock_name.tolist()[0]))
                    self.notice_msg.append("%s %s[MA底部穿越]\n"%(EachStockID,info[(info.code == EachStockID)].stock_name.tolist()[0]))
                try:
                    df=self.get_stock_dmi_my_signal(EachStockID,'2018-1-1',time.strftime("%Y-%m-%d",time.localtime(time.time())))
                    #print(df)
                    minaaj = ta.MIN(df['AAJ'].values[:-1], timeperiod=12)[-1]
                    maxaaj = ta.MAX(df['AAJ'].values[:-1], timeperiod=12)[-1]
                    #minaaj_index = ta.MININDEX(df['AAJ'].values[:-1], timeperiod=12)[-1]
                    #print(minaaj,minaaj_index,df.iat[-1,-1],stock_id)
                    #最新的AAJ小于0，且大于低谷，并且低谷就是近一段时间的最低值，确认反转
                    if df.iat[-1,-1] < -20 and df.iat[-2,-1] < df.iat[-1,-1] and df.iat[-2,-1] == minaaj: #-20拍脑袋的
                    #if df.iat[-1,-1] < 0 and df.iat[-2,-1] < df.iat[-1,-1] and df.iat[-2,-1] == minaaj: #从-45改成0
                        info.loc[(info.code == EachStockID),'DMI2']=1
                        print("%s %s[DMI2底部反转]"%(EachStockID,info[(info.code == EachStockID)].stock_name.tolist()[0]))
                        self.notice_msg.append("%s %s[DMI2底部反转]\n"%(EachStockID,info[(info.code == EachStockID)].stock_name.tolist()[0]))
                    elif  df.iat[-2,-1] > df.iat[-1,-1] and df.iat[-2,-1] == maxaaj: #去掉大于0的条件
                        info.loc[(info.code == EachStockID),'DMI2']= -1
                        print("%s %s[DMI2顶部反转]"%(EachStockID,info[(info.code == EachStockID)].stock_name.tolist()[0]))
                        self.notice_msg.append("%s %s[DMI2顶部反转]\n"%(EachStockID,info[(info.code == EachStockID)].stock_name.tolist()[0]))

                    if self.get_stock_my_macd_signal(EachStockID,'2018-1-1',time.strftime("%Y-%m-%d",time.localtime(time.time()))) == True:
	                    info.loc[(info.code == EachStockID),'MACD']=1
	                    print("%s %s[MACD趋势相交]"%(EachStockID,info[(info.code == EachStockID)].stock_name.tolist()[0]))
	                    self.notice_msg.append("%s %s[MACD趋势相交]\n"%(EachStockID,info[(info.code == EachStockID)].stock_name.tolist()[0]))
                except:
                    continue
            self.update_info.emit(''.join(self.notice_msg))

        #df_last_ret.to_csv('last_ret.csv')
        print(info)
        print("---------------------------END-------------------------------")
        print("----------------------KDJ金叉 MA穿越--------------------------")
        print(info.loc[(info['KDJ'] == 1) & (info['MACROSS'] == 1) ])
        print("---------------------------DMI2买入指标-------------------------------")
        self.final_selected_stock = info.loc[(info['DMI2'] == 1) & (info['MACD'] == 1)] #df_last_ret[(df_last_ret['MACD'] <= df_last_ret['MACDsignal']) & (df_last_ret['MACD_DIS'] <= 0.5) & (df_last_ret['AAJ_FLAG'] == 1)]
        print(self.final_selected_stock['code'])
        info.to_csv('data/量化结果汇总_'+ str(market) + time.strftime("%Y%m%d",time.localtime(time.time())) + '_' +'.csv')
        return info


    def get_stock_kdj_buy_signal(self,stock_id,days):
        # 计算KDJ指标
        end_day=datetime.date(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day)
        days=days*7/5
        #考虑到周六日非交易
        start_day=end_day-datetime.timedelta(days)

        start_day=start_day.strftime("%Y-%m-%d")
        end_day=end_day.strftime("%Y-%m-%d")
        try:
            ret,stock_data=self.quote_ctx.get_history_kline(stock_id,start=start_day,end=end_day,ktype='K_DAY', autype='qfq')
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
                kdj_position_gold = (stock_data['KDJ_K'] > stock_data['KDJ_D']) & (stock_data['KDJ_K'] <= 25)|(stock_data['KDJ_J'] < 0)
                kdj_position_die = (stock_data['KDJ_K'] > stock_data['KDJ_D']) & (stock_data['KDJ_D'] > 75 )
                try:
                    stock_data.loc[kdj_position_gold[(kdj_position_gold == True) & (kdj_position_gold.shift() == False)].index, 'KDJ_金叉死叉'] = 1
                    stock_data.loc[kdj_position_gold[(kdj_position_gold == True) & (kdj_position_gold.shift() == False)].index-1, 'KDJ_金叉死叉'] = 1
                    stock_data.loc[kdj_position_gold[(kdj_position_gold == True) & (kdj_position_gold.shift() == False)].index-2, 'KDJ_金叉死叉'] = 1
                    stock_data.loc[kdj_position_gold[(kdj_position_gold == True) & (kdj_position_gold.shift() == False)].index-3, 'KDJ_金叉死叉'] = 1
                    stock_data.loc[kdj_position_die[(kdj_position_die == False) & (kdj_position_die.shift() == True)].index, 'KDJ_金叉死叉'] = -1
                except:
                    pass
                #stock_data.to_csv("00700KDJ.csv", index=True, sep=',')
                if len(stock_data.index) > 3:
                    #过去三天出了金叉,或过去五天有J无限接近底部,同时没有扭头向下的话，,标为1.
                    for pos in range(7):
                        if (stock_data.iloc[-pos]['KDJ_金叉死叉'] == 1)  and (stock_data.iloc[-1]['KDJ_J'] >= stock_data.iloc[-1]['KDJ_K']):
                            return  True
                        #(stock_data.iloc[-1]['KDJ_J'] < 1 or stock_data.iloc[-2]['KDJ_J'] < 1 or stock_data.iloc[-3]['KDJ_J'] < 1 or stock_data.iloc[-4]['KDJ_J'] < 1 or stock_data.iloc[-5]['KDJ_J'] < 1) and\
                        #print("股票%s 近三日内出现KDJ金叉"%(stock_id))

                    else:
                        return  False
        except Exception as e:
            print("%s 错误：%s 返回结果%s in %s"% (stock_id,e,stock_data,"get_stock_kdj_buy_signal"))
            return  False

    def get_stock_macd_buy_signal(self,stock_id,days):
        pass
    def get_stock_ma_cross_signal(self,stock_id,days):
        end_day=datetime.date(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day)
        days=days*7/5
        #考虑到周六日非交易
        start_day=end_day-datetime.timedelta(days)

        start_day=start_day.strftime("%Y-%m-%d")
        end_day=end_day.strftime("%Y-%m-%d")
        try:
            ret, df = self.quote_ctx.get_history_kline(stock_id, start=start_day,end=end_day, ktype='K_DAY', autype='qfq')  # 获取历史K线
            if not df.empty:
            #提取收盘价
                closed=df['close'].values
                 #获取均线的数据，通过timeperiod参数来分别获取 5,10,20 日均线的数据。
                df['MA5']=ta.SMA(closed,timeperiod=5)
                df['MA10']=ta.SMA(closed,timeperiod=10)
                df['MA20']=ta.SMA(closed,timeperiod=20)
            if len(df.index) > 20:
                    #这里写策略，穿越策略,如果五日线过去20个交易日有穿越十日线
                    for pos in range(5):
                        if (df.iloc[-pos]['MA5'] - df.iloc[-pos]['MA10'] < 1)  and (df.iloc[-pos]['MA5'] - df.iloc[-pos]['MA10'] > 0) and (df.iloc[-pos-1]['MA5'] - df.iloc[-pos-1]['MA10'] < 0):
                            #print("%s 倒数第%s日 MA5:%s 穿越 MA10:%s"%(stock_id,pos,df.iloc[-pos]['MA5'],df.iloc[-pos]['MA10']))
                            return  True
                        if pos >= len(df.index):
                            return  False
                    return False
        except Exception as e:
            print("错误：%s,返回结果%s in get_stock_ma_cross_signal"% (e,df))
    def get_stock_my_macd_signal(self,stock_id,start_day,end_day):
        # end_day=datetime.date(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day)
        # days=days*7/5
        # #考虑到周六日非交易
        # start_day=end_day-datetime.timedelta(days)
        #
        # start_day=start_day.strftime("%Y-%m-%d")
        # end_day=end_day.strftime("%Y-%m-%d")
        try:
            ret, stock_data = self.quote_ctx.get_history_kline(stock_id, start=start_day,end=end_day, ktype='K_DAY', autype='qfq')  # 获取历史K线
            if not stock_data.empty:
                close = [float(x) for x in stock_data['close']]
                #计算MACD
                stock_data['EMA12'] = ta.EMA(np.array(close), timeperiod=12)
                stock_data['EMA26'] = ta.EMA(np.array(close), timeperiod=26)
                # 调用talib计算MACD指标
                stock_data['MACD'],stock_data['MACDsignal'],stock_data['MACDhist'] = ta.MACD(np.array(close),fastperiod=12, slowperiod=26, signalperiod=9)
                stock_data['my_MACD'],stock_data['my_MACDsignal'],stock_data['my_MACDhist'] = self.my_macd(stock_data['close'].values, fastperiod=6, slowperiod=12, signalperiod=9)
                #plt.plot(df.index,df['MACD'],label='DIF')
                #plt.plot(df.index,df['MACDsignal'],label='DEA')

                def  cal_c(a,b):
                    if abs(a) > abs(b):
                        return abs(abs(a)- abs(b))/abs(a)
                    else:
                        return abs(abs(b)-abs(a))/abs(b)

                stock_data['MACD_DIS'] = stock_data.apply(lambda stock_data:cal_c(stock_data['MACD'],stock_data['MACDsignal']), axis=1)#abs(stock_data['MACDsignal'] - stock_data['MACD'])/abs(stock_data['MACDsignal'])
                #macd_postion= (stock_data['MACD'] > stock_data['MACDsignal'])
                macd_postion= (stock_data['MACD'] < stock_data['MACDsignal']) & (stock_data['MACD_DIS'] < 0.45) & (stock_data['MACD'] > stock_data['MACD'].shift())
                try:
                    stock_data.loc[macd_postion[(macd_postion == True) & (macd_postion.shift() == False)].index, 'MACD_CROSS'] = 1
                    stock_data.loc[macd_postion[(macd_postion == True) & (macd_postion.shift() == False)].index-1, 'MACD_CROSS'] = 2
                    stock_data.loc[macd_postion[(macd_postion == True) & (macd_postion.shift() == False)].index-2, 'MACD_CROSS'] = 3
                    stock_data.loc[macd_postion[(macd_postion == True) & (macd_postion.shift() == False)].index-3, 'MACD_CROSS'] = 4
                except:
                    pass
                #print(stock_data)
                if len(stock_data.index) > 20:
                    #这里写策略，穿越策略,如果五日内有发现置1了
                    for pos in range(5):
                        if stock_data.iloc[-pos]['MACD_CROSS'] >=1:
                            print("%s 倒数第%s日 MACD_CROSS:%s 趋势穿越"%(stock_id,pos,stock_data.iloc[-pos]['time_key']))
                            return  True
                        if pos >= len(stock_data.index):
                            return  False
                    return False
        except Exception as e:
            print("错误：%s,返回结果%s in get_stock_my_macd_signal"% (e,stock_data))


    def get_stock_my_schedule_signal(self,stock_data):
        # 计算KDJ指标
        try:
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
                kdj_position_gold = (stock_data['KDJ_K'] > stock_data['KDJ_D']) #& (stock_data['KDJ_K'] <= 15)|(stock_data['KDJ_J'] < 0)去掉试试
                kdj_position_die = (stock_data['KDJ_K'] > stock_data['KDJ_D']) & (stock_data['KDJ_D'] > 75 )
                stock_data.loc[kdj_position_gold[(kdj_position_gold == True) & (kdj_position_gold.shift() == False)].index, 'KDJ_金叉死叉'] = 1
                try:
                    # stock_data.loc[kdj_position_gold[(kdj_position_gold == True) & (kdj_position_gold.shift() == False)].index - 1, 'KDJ_金叉死叉'] = 1
                    # stock_data.loc[kdj_position_gold[(kdj_position_gold == True) & (kdj_position_gold.shift() == False)].index - 2, 'KDJ_金叉死叉'] = 1
                    stock_data.loc[kdj_position_gold[(kdj_position_gold == True) & (kdj_position_gold.shift() == False)].index - 1, 'KDJ_金叉死叉'] = 1
                    stock_data.loc[kdj_position_gold[(kdj_position_gold == True) & (kdj_position_gold.shift() == False)].index - 2, 'KDJ_金叉死叉'] = 1
                    stock_data.loc[kdj_position_gold[(kdj_position_gold == True) & (kdj_position_gold.shift() == False)].index - 3, 'KDJ_金叉死叉'] = 1
                    stock_data.loc[kdj_position_gold[(kdj_position_gold == True) & (kdj_position_gold.shift() == False)].index + 1, 'KDJ_金叉死叉'] = 1
                except:
                    pass
                stock_data.loc[kdj_position_die[(kdj_position_die == False) & (kdj_position_die.shift() == True)].index, 'KDJ_金叉死叉'] = -1

                #计算MA指标
                # closed=stock_data['close'].values
                # #获取均线的数据，通过timeperiod参数来分别获取 5,10,20 日均线的数据。
                # stock_data['MA5']=ta.SMA(closed,timeperiod=5)
                # stock_data['MA10']=ta.SMA(closed,timeperiod=10)
                # stock_data['MA20']=ta.SMA(closed,timeperiod=20)
                # ma_positon_gold = (stock_data['MA5'] > stock_data['MA10']) & (stock_data['close'] > stock_data['MA20'])
                # stock_data.loc[ma_positon_gold[(ma_positon_gold == True) & (ma_positon_gold.shift() == False)].index,'MA_CROSS'] = 1
                # try:
                #     stock_data.loc[ma_positon_gold[(ma_positon_gold == True) & (ma_positon_gold.shift() == False)].index-1,'MA_CROSS'] = 1
                #     stock_data.loc[ma_positon_gold[(ma_positon_gold == True) & (ma_positon_gold.shift() == False)].index-2,'MA_CROSS'] = 1
                #     stock_data.loc[ma_positon_gold[(ma_positon_gold == True) & (ma_positon_gold.shift() == False)].index+1,'MA_CROSS'] = 1
                #     stock_data.loc[ma_positon_gold[(ma_positon_gold == True) & (ma_positon_gold.shift() == False)].index+2,'MA_CROSS'] = 1
                #     stock_data.loc[ma_positon_gold[(ma_positon_gold == True) & (ma_positon_gold.shift() == False)].index+3,'MA_CROSS'] = 1
                # except:
                #     pass

                # for pos in range(3,len(stock_data.index)-4):
                #         #if (stock_data.iloc[-pos]['MA5'] - stock_data.iloc[-pos]['MA10'] < 1)  and (stock_data.iloc[-pos]['MA5'] - stock_data.iloc[-pos]['MA10'] > 0) and (stock_data.iloc[-pos-1]['MA5'] - stock_data.iloc[-pos-1]['MA10'] < 0):
                #         if (stock_data.iloc[pos]['MA5'] - stock_data.iloc[pos]['MA10'] > 0) and (stock_data.iloc[pos-1]['MA5'] - stock_data.iloc[pos-1]['MA10'] < 0):
                #             #print("%s 倒数第%s日 MA5:%s 穿越 MA10:%s"%(stock_id,pos,df.iloc[-pos]['MA5'],df.iloc[-pos]['MA10']))
                #             stock_data.loc[pos,'MA_CROSS'] = 1
                #             stock_data.loc[pos-1,'MA_CROSS'] = 1
                #             stock_data.loc[pos-2,'MA_CROSS'] = 1
                #             stock_data.loc[pos+1,'MA_CROSS'] = 1
                #             stock_data.loc[pos+2,'MA_CROSS'] = 1

                #计算MACD
                close = [float(x) for x in stock_data['close']]
                #计算MACD
                stock_data['EMA12'] = ta.EMA(np.array(close), timeperiod=12)
                stock_data['EMA26'] = ta.EMA(np.array(close), timeperiod=26)
                # 调用talib计算MACD指标
                stock_data['MACD'],stock_data['MACDsignal'],stock_data['MACDhist'] = ta.MACD(np.array(close),fastperiod=12, slowperiod=26, signalperiod=9)
                stock_data['my_MACD'],stock_data['my_MACDsignal'],stock_data['my_MACDhist'] = self.my_macd(stock_data['close'].values, fastperiod=6, slowperiod=12, signalperiod=9)
                #plt.plot(df.index,df['MACD'],label='DIF')
                #plt.plot(df.index,df['MACDsignal'],label='DEA')

                def  cal_c(a,b):
                    if abs(a) > abs(b):
                        return abs(abs(a)- abs(b))/abs(a)
                    else:
                        return abs(abs(b)-abs(a))/abs(b)

                stock_data['MACD_DIS'] = stock_data.apply(lambda stock_data:cal_c(stock_data['MACD'],stock_data['MACDsignal']), axis=1)#abs(stock_data['MACDsignal'] - stock_data['MACD'])/abs(stock_data['MACDsignal'])
                #macd_postion= (stock_data['MACD'] > stock_data['MACDsignal'])
                #macd_postion= (stock_data['MACD'] < stock_data['MACDsignal']) & (stock_data['MACD_DIS'] < 0.20) #
                macd_postion = (stock_data['MACD'] < stock_data['MACDsignal']) & (stock_data['MACD_DIS'] >= 0.5) & (stock_data['MACD'] > stock_data['MACD'].shift()) #大于这个都是暴涨的
                try:
                    stock_data.loc[macd_postion[(macd_postion == True) & (macd_postion.shift() == False)].index, 'MACD_CROSS'] = 1
                    stock_data.loc[macd_postion[(macd_postion == True) & (macd_postion.shift() == False)].index-1, 'MACD_CROSS'] = 2
                    stock_data.loc[macd_postion[(macd_postion == True) & (macd_postion.shift() == False)].index-2, 'MACD_CROSS'] = 3
                    stock_data.loc[macd_postion[(macd_postion == True) & (macd_postion.shift() == False)].index-3, 'MACD_CROSS'] = 4
                except:
                    pass

                #计算DMI2
                N,MM=14,6
                high=stock_data['high']
                low=stock_data['low']
                close=stock_data['close']
                df = pd.DataFrame()
                df['h-l']=high-low
                df['h-c']=abs(high-close.shift(1))
                df['l-c']=abs(close.shift(1)-low)
                df['tr']=df.max(axis=1)
                df['PDM']=high-high.shift(1)
                df['MDM']=low.shift(1)-low
                df['DPD']=0
                df['DMD']=0
                for i in range(len(df.index)):
                    PDM=df.ix[i,'PDM']
                    MDM=df.ix[i,'MDM']
                    if PDM<0 or PDM<MDM:
                        df.ix[i,'DPD']=0
                    else:
                        df.ix[i,'DPD']=PDM
                    if MDM<0 or MDM<PDM:
                        df.ix[i,'DMD']=0
                    else:
                        df.ix[i,'DMD']=MDM
                #下面这段是原先的代码，先注释掉吧
                df['NTR']=ta.EMA(df['tr'],N)
                df['NPDM']=ta.EMA(df['DPD'],N)
                df['NMDM']=ta.EMA(df['DMD'],N)
                df['PDI']=df['NPDM']/df['NTR']*100
                df['MDI']=df['NMDM']/df['NTR']*100
                ##下面这段是原先的代码，先注释掉吧
                df['DX']=ta.EMA((df['NPDM']-df['NMDM'])/(df['NMDM']+df['NPDM'])*100,MM)
                df['ADX']=df['DX']
                df['ADXR']=ta.EMA(df['ADX'],MM)
                df['AAJ'] =0
                df['AAJ'] = ta.EMA(3*df['ADX']-2*df['ADXR'],2)
                df['AAJ_FLAG'] =0
                #算好了拼一下
                stock_data = pd.concat([stock_data, df], axis=1)
                for pos in range(3,len(stock_data.index)  - 1):
                    if (stock_data.iloc[pos]['AAJ'] - stock_data.iloc[pos-1]['AAJ'] < 0)  and (stock_data.iloc[pos]['AAJ'] - stock_data.iloc[pos+1]['AAJ'] < 0 and stock_data.iloc[pos]['AAJ'] < 0):
                        stock_data.loc[pos,'AAJ_FLAG'] = 1
                #stock_data.to_csv("KDJ.csv", index=True, sep=',')
                return  stock_data
        except Exception as e:
            print("%s 错误：%s 返回结果%s in %s"% (stock_data['code'],e,stock_data,"get_stock_my_schedule_signal"))
            return  stock_data


    def get_stock_dmi_ta_signal(self,stock_id,days):
        SHORTMA = 5
        LONGMA = 20
        ADXPERIOD = 14

        ret, df = self.quote_ctx.get_history_kline(stock_id, start='2018-01-01',end='2018-05-27', ktype='K_DAY', autype='qfq')  # 获取历史K线
        if not df.empty:
            high=df['high'].values
            low=df['low'].values
            close=df['close'].values
            df['ADX'] = ta.ADX(high,low,close,ADXPERIOD)
            df['ADXR'] = ta.ADXR(high,low,close,ADXPERIOD)
            df['PLUS_DI'] = ta.PLUS_DI(high,low,close,ADXPERIOD)
            df['MINUS_DI'] = ta.MINUS_DI(high,low,close,ADXPERIOD)
            #df['ADX'] = ta.ADX(high,low,close,ADXPERIOD)
            #df['ADXR'] = ta.ADXR(high,low,close,ADXPERIOD)
            #df['AAJ'] = 3*df['ADX']-2*df['ADXR']
            df['SHORTMA'] = ta.SMA(close,SHORTMA)
            df['LONGMA'] = ta.SMA(close,LONGMA)
            fig = plt.figure(figsize=[18,5])
            #plt.plot(df.index,df['MACD'],label='macd dif')
            #plt.plot(df.index,df['MACDsignal'],label='signal dea')
            plt.plot(df.index,df['ADX'] ,label='ADX')
            plt.plot(df.index,df['ADXR'] ,label='ADXR')
            plt.plot(df.index,df['PLUS_DI'] ,label='PLUS_DI')
            plt.plot(df.index,df['MINUS_DI'] ,label='MINUS_DI')
            plt.plot(df.index,df['AAJ'] ,label='AAJ')
            plt.legend(loc='best')
            #plt.plot(df)
            plt.grid()
            #记得加这一句，不然不会显示图像
            plt.show()

    def get_stock_dmi_my_signal(self,stock_id,start_day,end_day):
        N,MM=14,6
        ret, dfret = self.quote_ctx.get_history_kline(stock_id, start_day,end_day, ktype='K_DAY', autype='qfq')  # 获取历史K线
        if not dfret.empty:
            high=dfret['high']
            low=dfret['low']
            close=dfret['close']
            df = pd.DataFrame()
            df['h-l']=high-low
            df['h-c']=abs(high-close.shift(1))
            df['l-c']=abs(close.shift(1)-low)
            df['tr']=df.max(axis=1)


            #df['tr']=ta.EMA(df['tr'],N)
            #EXPMEMA(MAX(MAX(HIGH-LOW,ABS(HIGH-REF(CLOSE,1))),ABS(REF(CLOSE,1)-LOW)),N);
            df['PDM']=high-high.shift(1)
            df['MDM']=low.shift(1)-low
            df['DPD']=0
            df['DMD']=0
            for i in range(len(df.index)):
                PDM=df.ix[i,'PDM']
                MDM=df.ix[i,'MDM']
                if PDM<0 or PDM<MDM:
                    df.ix[i,'DPD']=0
                else:
                    df.ix[i,'DPD']=PDM
                if MDM<0 or MDM<PDM:
                    df.ix[i,'DMD']=0
                else:
                    df.ix[i,'DMD']=MDM
                #下面这段是原先的代码，先注释掉吧
                # for i in range(N,len(df.index)):
                #     #df.ix[i,'NTR']=sum(df.ix[i-N+1:i,'tr'])
                #     #df.ix[i,'NPDM']=sum(df.ix[i-N+1:i,'DPD'])
                #     #df.ix[i,'NMDM']=sum(df.ix[i-N+1:i,'DMD'])
                #     #df.ix[i,'NTR']=ta.EMA(df.ix[i-N+1:i,'tr'],N).values[-1]
                #     #df.ix[i,'NPDM']=ta.EMA(df.ix[i-N+1:i,'DPD'],N).values[-1]
                #     #df.ix[i,'NMDM']=ta.EMA(df.ix[i-N+1:i,'DMD'],N).values[-1]
                #     pass
                df['NTR']=ta.EMA(df['tr'],N)
                df['NPDM']=ta.EMA(df['DPD'],N)
                df['NMDM']=ta.EMA(df['DMD'],N)
                df['PDI']=df['NPDM']/df['NTR']*100
                df['MDI']=df['NMDM']/df['NTR']*100


            #df['DX']=abs(df['MDI']-df['PDI'])/(df['MDI']+df['PDI'])*100
            #ADX0:=EMA((DMP-DMM)/(DMP+DMM)*100,M);
            #ADXR0:=EMA(ADX0,M);
            df['DX']=ta.EMA((df['NPDM']-df['NMDM'])/(df['NMDM']+df['NPDM'])*100,MM)
            df['ADX']=df['DX']
            df['ADXR']=ta.EMA(df['ADX'],MM)
            df['AAJ'] =0
            df['AAJ'] = ta.EMA(3*df['ADX']-2*df['ADXR'],2)
            # for i in range(MM,len(df.index)):
            #     summDX=0
            #     summADX=0
            #     for j in range(i-MM,i):
            #         summDX+=df.ix[j,'DX']
            #         summADX+=df.ix[j,'ADX']
            #     df.ix[i,'ADX']=summDX/MM
            #     summADX+=df.ix[j,'ADX']
            #     df.ix[i,'ADXR']=summADX/MM
            #算好了拼一下
            dfret = pd.concat([dfret, df], axis=1)

            '''
            #绘图函数暂时注释
            fig = plt.figure(figsize=[18,6])
            fig.autofmt_xdate()
            dfret['date'] = pd.to_datetime(dfret['time_key'])
            dfret.index = dfret['date'].tolist()
            #print(dfret)
            plt.plot(dfret.index.to_pydatetime() ,dfret['ADX'] ,label='ADX',linestyle='-',color='#ff0000',alpha=0.1)
            plt.plot(dfret.index.to_pydatetime() ,dfret['ADXR'] ,label='ADXR',linestyle='-',color='#00ff00',alpha=0.1)
            plt.fill_between(dfret.index.to_pydatetime(), dfret['ADX'], dfret['ADXR'], dfret['ADX'] > dfret['ADXR'],color='#ff0000', alpha=1)
            plt.fill_between(dfret.index.to_pydatetime(), dfret['ADX'], dfret['ADXR'], dfret['ADX'] < dfret['ADXR'],color='#00ff00', alpha=1)
            plt.plot(dfret.index.to_pydatetime() ,dfret['PDI'] ,label='PDI',color="#3383ba")
            plt.plot(dfret.index.to_pydatetime() ,dfret['MDI'] ,label='MDI',color="#eb8a35")
            plt.plot(dfret.index.to_pydatetime() ,dfret['AAJ'] ,label='AAJ',color="#51b151")
            plt.ylim((-110, 110))
            plt.xlabel("Trading Cycle")
            plt.ylabel("Fluctuation Ratio")
            plt.title('%s DMI2 Indicator'%stock_id)
            plt.gca().xaxis.set_major_formatter(mdate.DateFormatter('%Y/%m/%d'))
            #plt.gca().xaxis.set_major_locator(mdate.DayLocator())
            plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(5))
            plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(10))
            plt.setp(plt.gca().get_xticklabels(), rotation=45)

            plt.legend(loc='best')
            plt.grid()
            #记得加这一句，不然不会显示图像
            plt.show()
            '''
        #return df['PDI'],df['MDI'],df['ADX'],df['ADXR']
        return  dfret

    def get_stock_dmi_my_signal_min(self,stock_id,min_length):
        N,MM=14,6
        try:
            ret_code,ret_data= self.quote_ctx.subscribe(stock_id, 'K_'+str(min_length)+'M', push=False)
            ret, dfret = self.quote_ctx.get_cur_kline(stock_id, 100, ktype='K_'+str(min_length)+'M', autype='qfq')  # 获取分钟线,日内的话自己除就是了
            if not dfret.empty:
                high=dfret['high']
                low=dfret['low']
                close=dfret['close']
                df = pd.DataFrame()
                df['h-l']=high-low
                df['h-c']=abs(high-close.shift(1))
                df['l-c']=abs(close.shift(1)-low)
                df['tr']=df.max(axis=1)


                #df['tr']=ta.EMA(df['tr'],N)
                #EXPMEMA(MAX(MAX(HIGH-LOW,ABS(HIGH-REF(CLOSE,1))),ABS(REF(CLOSE,1)-LOW)),N);
                df['PDM']=high-high.shift(1)
                df['MDM']=low.shift(1)-low
                df['DPD']=0
                df['DMD']=0
                for i in range(len(df.index)):
                    PDM=df.ix[i,'PDM']
                    MDM=df.ix[i,'MDM']
                    if PDM<0 or PDM<MDM:
                        df.ix[i,'DPD']=0
                    else:
                        df.ix[i,'DPD']=PDM
                    if MDM<0 or MDM<PDM:
                        df.ix[i,'DMD']=0
                    else:
                        df.ix[i,'DMD']=MDM
                #下面这段是原先的代码，先注释掉吧
                # for i in range(N,len(df.index)):
                #     #df.ix[i,'NTR']=sum(df.ix[i-N+1:i,'tr'])
                #     #df.ix[i,'NPDM']=sum(df.ix[i-N+1:i,'DPD'])
                #     #df.ix[i,'NMDM']=sum(df.ix[i-N+1:i,'DMD'])
                #     #df.ix[i,'NTR']=ta.EMA(df.ix[i-N+1:i,'tr'],N).values[-1]
                #     #df.ix[i,'NPDM']=ta.EMA(df.ix[i-N+1:i,'DPD'],N).values[-1]
                #     #df.ix[i,'NMDM']=ta.EMA(df.ix[i-N+1:i,'DMD'],N).values[-1]
                #     pass
                df['NTR']=ta.EMA(df['tr'],N)
                df['NPDM']=ta.EMA(df['DPD'],N)
                df['NMDM']=ta.EMA(df['DMD'],N)
                df['PDI']=df['NPDM']/df['NTR']*100
                df['MDI']=df['NMDM']/df['NTR']*100

                ##下面这段是原先的代码，先注释掉吧
                #df['DX']=abs(df['MDI']-df['PDI'])/(df['MDI']+df['PDI'])*100
                #ADX0:=EMA((DMP-DMM)/(DMP+DMM)*100,M);
                #ADXR0:=EMA(ADX0,M);
                df['DX']=ta.EMA((df['NPDM']-df['NMDM'])/(df['NMDM']+df['NPDM'])*100,MM)
                df['ADX']=df['DX']
                df['ADXR']=ta.EMA(df['ADX'],MM)
                df['AAJ'] =0
                df['AAJ'] = ta.EMA(3*df['ADX']-2*df['ADXR'],2)
                #下面这段是原先的代码，先注释掉吧
                #df['AAJ'] = 3*df['ADX']-2*df['ADXR']
                # for i in range(MM,len(df.index)):
                #     summDX=0
                #     summADX=0
                #     for j in range(i-MM,i):
                #         summDX+=df.ix[j,'DX']
                #         summADX+=df.ix[j,'ADX']
                #     df.ix[i,'ADX']=summDX/MM
                #     summADX+=df.ix[j,'ADX']
                #     df.ix[i,'ADXR']=summADX/MM
                #算好了拼一下
                dfret = pd.concat([dfret, df], axis=1)
        except:
            print("结果异常，错误码:%d 返回结果:%s"%(ret,dfret))


        #绘图函数暂时注释
        '''
        fig = plt.figure(figsize=[18,6])
        #dfret.index = dfret['time_key'].tolist()
        #print(dfret)
        plt.plot(dfret.index,dfret['ADX'] ,label='ADX',linestyle='-',color='#ff0000',alpha=0.1)
        plt.plot(dfret.index ,dfret['ADXR'] ,label='ADXR',linestyle='-',color='#00ff00',alpha=0.1)
        plt.fill_between(dfret.index, dfret['ADX'], dfret['ADXR'], dfret['ADX'] > dfret['ADXR'],color='#ff0000', alpha=1)
        plt.fill_between(dfret.index, dfret['ADX'], dfret['ADXR'], dfret['ADX'] < dfret['ADXR'],color='#00ff00', alpha=1)
        plt.plot(dfret.index,dfret['PDI'] ,label='PDI',color="#3383ba")
        plt.plot(dfret.index,dfret['MDI'] ,label='MDI',color="#eb8a35")
        plt.plot(dfret.index,dfret['AAJ'] ,label='AAJ',color="#51b151")
        plt.ylim((-110, 110))
        plt.xlabel("Trading Cycle")
        plt.ylabel("Fluctuation Ratio")
        plt.title('%s DMI2 Indicator'%stock_id)
        plt.gca().xaxis.set_major_formatter(mdate.DateFormatter('%Y/%m/%d %HH%MM%SS'))
        #plt.gca().xaxis.set_major_locator(mdate.DayLocator())
        plt.gca().xaxis.set_major_locator(ticker.MultipleLocator(5))
        plt.gca().yaxis.set_major_locator(ticker.MultipleLocator(10))
        plt.setp(plt.gca().get_xticklabels(), rotation=45)

        plt.legend(loc='best')
        plt.grid()
        #记得加这一句，不然不会显示图像
        plt.show()
        '''
            #return df['PDI'],df['MDI'],df['ADX'],df['ADXR']

        return  dfret

    def open_trade_make_order(self,unlock_password, stock_id, trade_env,order_side,lot_size,stock_size):
        if unlock_password == "":
            raise Exception("请先配置交易解锁密码!")
        #quote_ctx = OpenQuoteContext(host=api_ip, port=api_port)  # 创建行情api
        self.quote_ctx.subscribe(stock_id, "ORDER_BOOK", push=False)  # 定阅摆盘
        # 创建交易api
        is_hk_trade = 'HK.' in stock_id

        # 每手股数
        lot_size = 0
        is_unlock_trade = False
        is_fire_trade = False
        while not is_fire_trade:
            sleep(2)
            # 解锁交易
            if not is_unlock_trade:
                ret_code, ret_data = self.trade_ctx.unlock_trade(unlock_password)
                is_unlock_trade = (ret_code == 0)
                if not trade_env and not is_unlock_trade:
                    print("请求交易解锁失败：{}".format(ret_data))
                    continue

            if lot_size == 0:
                ret, data = self.quote_ctx.get_market_snapshot([stock_id])
                lot_size = data.iloc[0]['lot_size'] if ret == 0 else 0
                if ret != 0:
                    print("取不到每手信息，错误码%d 错误信息 %s重试中!"%(ret,data))
                    continue
                elif lot_size <= 0:
                    raise BaseException("该股票每手信息错误，可能不支持交易 code ={}".format(stock_id))

            ret, data = self.quote_ctx.get_order_book(stock_id)  # 得到第十档数据
            if ret != 0:
                continue
            price = 0
            qty = 0
            # 交易类型
            #order_side = 0  # 0，买 1,卖
            if is_hk_trade:
                order_type = 0  # 港股增强限价单(普通交易)
            else:
                order_type = 2  # 美股限价单

            if order_side == 0 : #买入价格计算,直接秒卖一
                # 计算交易价格
                bid_order_arr = data['Ask']
                if is_hk_trade:
                    if len(bid_order_arr) != 10:
                        continue
                    # 港股下单: 价格定为第一档
                    price, _, _ = bid_order_arr[0]
                else:
                    if len(bid_order_arr) == 0:
                        continue
                    # 美股下单： 价格定为一档降10%
                    price, _, _ = bid_order_arr[0]
                    price = round(price * 0.94, 2)

                qty = int(stock_size/price/lot_size)*lot_size #资金上限除以单价，算出来是多少股
                if qty < lot_size:
                    qty = lot_size

                # 价格和数量判断
                if qty == 0 or price == 0.0:
                    continue
                typestr = '买单'
            elif order_side == 1:   #卖出价格计算,直接秒买一
                ask_order_arr = data['Bid']
                if is_hk_trade:
                    if len(ask_order_arr) != 10:
                        continue
                    # 港股下单: 价格定为第一档
                    price, _, _ = ask_order_arr[0]
                else:
                    if len(ask_order_arr) == 0:
                        continue
                    # 美股下单： 价格定为一档降10%
                    price, _, _ = ask_order_arr[0]
                    price = round(price * 0.94, 2)

                qty = lot_size * stock_size

                # 价格和数量判断
                if qty == 0 or price == 0.0:
                    continue
                typestr = '卖单'


            # 下单
            order_id = 0
            #ret_data = "[%s] [%s]尝试下%s，单价:%f 数量%d 每手%d股,金额%f HK$,单号为%s"%(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())),stock_id,typestr,price,qty,lot_size,price*qty,order_id)
            #print(ret_data)
            ret_code, ret_data = self.trade_ctx.place_order(price=price, qty=qty, strcode=stock_id, orderside=order_side,
                                                       ordertype=order_type, envtype=trade_env)
            is_fire_trade = True
            #print('下单ret={} data={}'.format(ret_code, ret_data))
            if ret_code == 0:
                row = ret_data.iloc[0]
                order_id = row['orderid']
                ret_data = "[%s] [%s]下%s成功，单价:%f 每手%d股,金额%f HK$,单号为%s"%(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())),stock_id,typestr,price,lot_size,price*qty,order_id)
                print(ret_data)
            return ret_code,ret_data

    def get_current_position_list(self,trade_env):
        ret_code, ret_data = self.trade_ctx.position_list_query(strcode='', stocktype='', pl_ratio_min='', pl_ratio_max='', envtype=trade_env)
        return  ret_data
    #获取每手信息有频率限制，计划一次全获取
    def get_current_trade_list_info(self,stocklist):
        while True:
            ret, data = self.quote_ctx.get_market_snapshot(stocklist)
            #lot_size = data.iloc[0]['lot_size'] if ret == 0 else 0
            if ret != 0:
                print("取不到每手信息，错误码%d 错误信息 %s重试中!"%(ret,data))
            else:
                break;
        return ret,data

    #获取每天的策略，该买啥卖啥
    def get_everyday_schedule(self,market):
        self.init_cn_stock("data/stocklist.csv")
        #wgs.loop_all_cn_stocks('futu',30,0)
        self.init_hk_stock("data/HSIIndexList.csv")
        self.init_us_stock("data/us_market.csv")
        self.df_to_do= pd.DataFrame()
        if market < 0:
            df = self.loop_all_stocks('futu',30,0) #0 沪深 #1 香港 #2美国
            self.df_total = self.df_total.append(df)
            df = self.loop_all_stocks('futu',30,1) #0 沪深 #1 香港 #2美国
            self.df_total = self.df_total.append(df)

            df = self.loop_all_stocks('futu',30,2) #0 沪深 #1 香港 #2美国
            self.df_total = self.df_total.append(df)
        else:
            df = self.loop_all_stocks('futu',30,market) #0 沪深 #1 香港 #2美国
            self.df_total = self.df_total.append(df)

        df_selected =wgs.df_total.loc[(wgs.df_total['DMI2'] == 1) & (wgs.df_total['KDJ'] >= 1)]
        df_sell = wgs.df_total.loc[(wgs.df_total['DMI2'] == -1)]
        df_selected = df_selected[['code','stock_name']]
        df_selected = df_selected.drop_duplicates(['code'])
        print("--------------以下为今日选股-----------------")
        print(df_selected)
        print("------------------结束----------------------")
        df_storage =pd.DataFrame()
        try:
            df_selected.to_csv("data/schedule"+ time.strftime("%Y%m%d",time.localtime(time.time())) +".csv",columns=['code','stock_name'])
            with open("data/storagelist.csv", 'rb') as f:
                    result = chardet.detect(f.read())
                    df_storage = pb.read_csv("data/storagelist.csv",encoding=result['encoding'])
        except:
            print("尝试写入文件%s失败，跳过...."%("data/schedule"+ time.strftime("%Y%m%d",time.localtime(time.time())) +".csv"))
        #df_storage = pd.read_csv("data/storagelist.csv")
        df_storage=df_storage.append(df_selected)
        df_storage = df_storage.drop_duplicates(['code'])
        df_storage_keep = df_storage[~(df_storage['code'].isin(df_sell['code']))]
        df_storage_keep = df_storage_keep[['code','stock_name']]
        df_storage_to_sell = df_storage[(df_storage['code'].isin(df_sell['code']))]
        df_storage_keep.to_csv("data/storagelist.csv",columns=['code','stock_name'])
        print("--------------以下持仓应该卖出-----------------")
        print(df_storage_to_sell)
        print("------------------结束-----------------------")

    #还没写好，回测功能函数
    def calculate_rate_of_my_schedule(self):
        end_day=datetime.date(datetime.date.today().year,datetime.date.today().month,datetime.date.today().day)
        end_day=end_day.strftime("%Y-%m-%d")
        all_stock = pd.DataFrame()
        progress = 0
        for code in self.cn_stock_list['code']:
            progress = progress + 1
            print("[%s]正在处理%s.....进度%0.1f"%(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(time.time())),code,progress/len(self.cn_stock_list.index)*100))
            ret,stock_data=self.quote_ctx.get_history_kline(code,start='2017-01-01',end=end_day,ktype='K_DAY', autype='qfq')
            if stock_data.empty:
                continue
            df=self.get_stock_my_schedule_signal(stock_data)
            #print(df)
            for n in [1, 2, 3, 5, 10, 20]:
                df['接下来'+str(n)+'个交易日涨跌幅'] =df['close'].shift(-1*n) / df['close'] - 1.0
            df.dropna(how='any', inplace=True)# 删除所有有空值的数据行

            # 筛选出符合条件的数据，并将这些数据合并到all_stock中
            try:
                #stock_data = df[(((df['MACD_CROSS'] == 3 & df['MACD_DIS'] <= 0.3) |(df['MACD_CROSS'] == 4 & df['MACD_DIS'] <= 0.4)) & (df['AAJ_FLAG'] == 1))]
                #stock_data = df[(df['MACD_CROSS'] >= 3)  & (df['MACD_DIS'] <= 0.5) & (df['AAJ_FLAG'] == 1)]
                #macd_postion= (stock_data['MACD'] < stock_data['MACDsignal']) & (stock_data['MACD_DIS'] <= 0.45) & (stock_data['MACD'] > stock_data['MACD'].shift())
                #stock_data = df[(df['MACD_CROSS'] >= 1) & (df['AAJ_FLAG'] == 1)]
                stock_data = df[(df['KDJ_金叉死叉'] == 1) & (df['AAJ_FLAG'] == 1)]
                #stock_data = pd.merge(stock_data,stock_data2,how='left')
            except:
                continue

            if stock_data.empty:
                pass
            all_stock = all_stock.append(stock_data, ignore_index=True)
        all_stock.to_csv("data/回测数据.csv", index=True, sep=',')
        # ========== 根据上一步得到的所有股票KDJ金叉数据all_stock，统计这些股票在未来交易日中的收益情况
        print('所选择股票清单中符合条件的股票收益统计如下，一共%s，这些股票在：' %all_stock.shape[0])

        for n in [1, 2, 3, 5, 10, 20]:
            print("条件触发之后的%d个交易日内，" % n),
            print("平均涨幅为%.2f%%，" % (all_stock['接下来'+str(n)+'个交易日涨跌幅'].mean() * 100)),
            print("其中上涨股票的比例是%.2f%%。" % \
                  (all_stock[all_stock['接下来'+str(n)+'个交易日涨跌幅'] > 0].shape[0]/float(all_stock.shape[0]) * 100))



if __name__ == "__main__":
    #draw_single_stock_MACD('HK.00700')
    #loop_all_hk_stocks_from_file("HSIIndexList.csv",60)
    #wgs=WhiteGuardStockCore()
    #wgs=WhiteGuardStockCore('119.29.141.202',11111)
    wgs=WhiteGuardStockCore4UI()
    wgs.start_connect('192.168.0.106',11111)
    #wgs.init_cn_stock("data/stocklist.csv")
    #wgs.loop_all_cn_stocks('futu',30,0)
    #wgs.init_hk_stock("data/HSIIndexList.csv")
    #wgs.get_stock_dmi_my_signal('HK.00700','2017-10-1','2018-06-1')
    #loop_all_stocks('HK.800000')
    #get_stock_kdj_buy_signal('HK.03883',30)
    #wgs.get_stock_dmi_my_signal_min('HK.02382',15)
    #每日运行选股
    wgs.get_everyday_schedule(-1)
    #回测功能
    #wgs.calculate_rate_of_my_schedule()
    wgs.clear_quote()
