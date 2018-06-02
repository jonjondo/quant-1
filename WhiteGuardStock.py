__author__ = 'wangpeng'
import tushare as ts
import talib as ta
import matplotlib.pyplot as plt
from futuquant.open_context import *
import datetime
import numpy as np
import pandas as pb
import matplotlib.dates as mdate
import matplotlib.ticker as ticker

api_ip = '192.168.0.104'#'119.29.141.202'这里要使用本地客户端
api_port = 11111

class WhiteGuardStock:
    def __init__(self):
        self.quote_ctx = OpenQuoteContext(api_ip, api_port)
    def init_cn_stock(self,cn_stock_file_name):
        self.cn_stock_list = pb.read_csv(cn_stock_file_name,encoding='GBK')
    def init_hk_stock(self,hk_stock_file_name):
        self.hk_stock_list = pb.read_csv(hk_stock_file_name)
    def clear_quote(self):
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
        ret,info = self.get_index_stocks(api_ip, api_port, index_code)
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

    def loop_all_cn_stocks(self,data_source,days):
        info = self.cn_stock_list
        print("----------------------以下符合条件%s----------------------------"%(days))
        for EachStockID in info.code:
            if data_source == 'tushare':
                if self.is_cn_stock_break_high_from_tushare(EachStockID,days):
                     print("%s %s"%(EachStockID,info[(info.code == EachStockID)].stock_name.tolist()[0]))
                sleep(5)
            elif data_source == 'futu':
                #if is_cn_stock_break_high_from_futu(EachStockID,days):
                if self.get_stock_kdj_buy_signal(EachStockID,days):
                    print("%s %s"%(EachStockID,info[(info.code == EachStockID)].stock_name.tolist()[0]))
                    self.cn_stock_list.loc[(info.code == EachStockID),'KDJ']=1
                if self.get_stock_ma_cross_signal(EachStockID,days):
                    self.cn_stock_list.loc[(info.code == EachStockID),'MACROSS']=1
        print("---------------------------END-------------------------------")
        print(self.cn_stock_list.loc[(info['KDJ'] == 1) & (info['MACROSS'] == 1) ])


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
                stock_data.loc[kdj_position_gold[(kdj_position_gold == True) & (kdj_position_gold.shift() == False)].index, 'KDJ_金叉死叉'] = 1
                stock_data.loc[kdj_position_die[(kdj_position_die == False) & (kdj_position_die.shift() == True)].index, 'KDJ_金叉死叉'] = -1
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
        try:
            ret, df = self.quote_ctx.get_history_kline(stock_id, start='2018-01-01',end='2018-05-18', ktype='K_DAY', autype='qfq')  # 获取历史K线
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
            for i in range(N,len(df.index)):
                #df.ix[i,'NTR']=sum(df.ix[i-N+1:i,'tr'])
                #df.ix[i,'NPDM']=sum(df.ix[i-N+1:i,'DPD'])
                #df.ix[i,'NMDM']=sum(df.ix[i-N+1:i,'DMD'])
                df.ix[i,'NTR']=ta.EMA(df.ix[i-N+1:i,'tr'],N).values[-1]
                df.ix[i,'NPDM']=ta.EMA(df.ix[i-N+1:i,'DPD'],N).values[-1]
                df.ix[i,'NMDM']=ta.EMA(df.ix[i-N+1:i,'DMD'],N).values[-1]
            df['PDI']=df['NPDM']/df['NTR']*100
            df['MDI']=df['NMDM']/df['NTR']*100

            #df.to_csv("dmi2.csv")
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
            ret_code,ret_data= self.quote_ctx.subscribe(stock_id, 'K_15M', push=False)
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
                for i in range(N,len(df.index)):
                    #df.ix[i,'NTR']=sum(df.ix[i-N+1:i,'tr'])
                    #df.ix[i,'NPDM']=sum(df.ix[i-N+1:i,'DPD'])
                    #df.ix[i,'NMDM']=sum(df.ix[i-N+1:i,'DMD'])
                    df.ix[i,'NTR']=ta.EMA(df.ix[i-N+1:i,'tr'],N).values[-1]
                    df.ix[i,'NPDM']=ta.EMA(df.ix[i-N+1:i,'DPD'],N).values[-1]
                    df.ix[i,'NMDM']=ta.EMA(df.ix[i-N+1:i,'DMD'],N).values[-1]
                df['PDI']=df['NPDM']/df['NTR']*100
                df['MDI']=df['NMDM']/df['NTR']*100

                #df.to_csv("dmi2.csv")
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

    def open_trade_make_order(self,unlock_password, stock_id, trade_env):
        if unlock_password == "":
            raise Exception("请先配置交易解锁密码!")
        quote_ctx = OpenQuoteContext(host=api_ip, port=api_port)  # 创建行情api
        quote_ctx.subscribe(stock_id, "ORDER_BOOK", push=False)  # 定阅摆盘

        # 创建交易api
        is_hk_trade = 'HK.' in stock_id
        if is_hk_trade:
            trade_ctx = OpenHKTradeContext(host=api_ip, port=api_port)
        else:
            if trade_env != 0:
                raise Exception("美股交易接口不支持仿真环境")
            trade_ctx = OpenUSTradeContext(host=api_ip, port=api_port)

        # 每手股数
        lot_size = 0
        is_unlock_trade = False
        is_fire_trade = False
        while not is_fire_trade:
            sleep(2)
            # 解锁交易
            if not is_unlock_trade:
                ret_code, ret_data = trade_ctx.unlock_trade(unlock_password)
                is_unlock_trade = (ret_code == 0)
                if not trade_env and not is_unlock_trade:
                    print("请求交易解锁失败：{}".format(ret_data))
                    continue

            if lot_size == 0:
                ret, data = quote_ctx.get_market_snapshot([stock_id])
                lot_size = data.iloc[0]['lot_size'] if ret == 0 else 0
                if ret != 0:
                    print("取不到每手信息，重试中!")
                    continue
                elif lot_size <= 0:
                    raise BaseException("该股票每手信息错误，可能不支持交易 code ={}".format(stock_id))

            ret, data = quote_ctx.get_order_book(stock_id)  # 得到第十档数据
            if ret != 0:
                continue

            # 计算交易价格
            bid_order_arr = data['Bid']
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

            qty = lot_size

            # 价格和数量判断
            if qty == 0 or price == 0.0:
                continue

            # 交易类型
            order_side = 0  # 买
            if is_hk_trade:
                order_type = 0  # 港股增强限价单(普通交易)
            else:
                order_type = 2  # 美股限价单

            # 下单
            order_id = 0
            ret_code, ret_data = trade_ctx.place_order(price=price, qty=qty, strcode=stock_id, orderside=order_side,
                                                       ordertype=order_type, envtype=trade_env)
            is_fire_trade = True
            print('下单ret={} data={}'.format(ret_code, ret_data))
            if ret_code == 0:
                row = ret_data.iloc[0]
                order_id = row['orderid']
                print("下单%s成功，单价:%f 每手%d股,单号为%s"%(stock_id,price,lot_size,order_id))

if __name__ == "__main__":
    #draw_single_stock_MACD('HK.00700')
    #loop_all_hk_stocks_from_file("HSIIndexList.csv",60)
    wgs=WhiteGuardStock()
    #wgs.init_cn_stock("data/stocklist.csv")
    #wgs.loop_all_cn_stocks('futu',30)
    #wgs.get_stock_dmi_my_signal('HK.00700','2017-10-1','2018-06-1')
    #loop_all_stocks('HK.800000')
    #get_stock_kdj_buy_signal('HK.03883',30)
    wgs.get_stock_dmi_my_signal_min('HK.02382',15)
    wgs.clear_quote()