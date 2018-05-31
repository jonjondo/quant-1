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


def get_basic_detail_by_history(info_type,start_year,end_year):
    if info_type == 1:
        print("---------获取业绩报告主表----------\n")
        for i in range(start_year,end_year):
            for j in range(4):
                year = i
                quater = j+1
                try:
                    df = ts.get_report_data(year,quater)
                    if not df.empty:
                        ret_file_name = "data/hsbasic/cnstockquaterreport"+str(year)+"q"+str(quater)+".csv"
                        df.to_csv(ret_file_name, index=True, sep=',')
                        print("file %s saved" %ret_file_name)
                except Exception as e:
                    print("报告主表发生错误%s"%e.messagme)
                    break;
    elif info_type == 2:
        print("---------获取盈利能力----------\n")
        for i in range(start_year,end_year):
            for j in range(4):
                year = i
                quater = j+1
                try:
                    df = ts.get_profit_data(year,quater)
                    if not df.empty:
                        ret_file_name = "data/hsbasic/cnstockbenefitability"+str(year)+"q"+str(quater)+".csv"
                        df.to_csv(ret_file_name, index=True, sep=',')
                        print("file %s saved" %ret_file_name)
                except Exception as e:
                    print("盈利能力发生错误%s"%e.messagme)
                    break;
    elif info_type == 3:
        print("---------获取营运能力----------\n")
        for i in range(start_year,end_year):
            for j in range(4):
                year = i
                quater = j+1
                try:
                    df = ts.get_operation_data(year,quater)
                    if not df.empty:
                        ret_file_name = "data/hsbasic/cnstockoperationability"+str(year)+"q"+str(quater)+".csv"
                        df.to_csv(ret_file_name, index=True, sep=',')
                        print("file %s saved" %ret_file_name)
                except Exception as e:
                    print("营运能力发生错误%s"%e.messagme)
                    break;
    elif info_type == 4:
        print("---------获取成长能力----------\n")
        for i in range(start_year,end_year):
            for j in range(4):
                year = i
                quater = j+1
                try:
                    df = ts.get_growth_data(year,quater)
                    if not df.empty:
                        ret_file_name = "data/hsbasic/cnstockgrowthability"+str(year)+"q"+str(quater)+".csv"
                        df.to_csv(ret_file_name, index=True, sep=',')
                        print("file %s saved" %ret_file_name)
                except Exception as e:
                    print("成长能力发生错误%s"%e.messagme)
                    break;
    elif info_type == 5:
        print("---------获取偿债能力----------\n")
        for i in range(start_year,end_year):
            for j in range(4):
                year = i
                quater = j+1
                try:
                    df = ts.get_debtpaying_data(year,quater)
                    if not df.empty:
                        ret_file_name = "data/hsbasic/cnstockdebtability"+str(year)+"q"+str(quater)+".csv"
                        df.to_csv(ret_file_name, index=True, sep=',')
                        print("file %s saved" %ret_file_name)
                except Exception as e:
                    print("偿债能力发生错误%s"%e.messagme)
                    break;
    elif info_type == 6:
        print("---------获取现金流量----------\n")
        for i in range(start_year,end_year):
            for j in range(4):
                year = i
                quater = j+1
                try:
                    df = ts.get_cashflow_data(year,quater)
                    if not df.empty:
                        ret_file_name = "data/hsbasic/cnstockcashflowability"+str(year)+"q"+str(quater)+".csv"
                        df.to_csv(ret_file_name, index=True, sep=',')
                        print("file %s saved" %ret_file_name)
                except Exception as e:
                    print("偿债能力发生错误%s"%e.messagme)
                    break;


def get_basic_detail_by_quater(year,quater):
    df = ts.get_report_data(year,quater)
    ret_file_name = "data/hsbasic/cnstockquaterreport"+str(year)+"q"+str(quater)+".csv"
    df.to_csv(ret_file_name, index=True, sep=',')
    print("file %s saved" %ret_file_name)

    df = ts.get_profit_data(year,quater)
    ret_file_name = "data/hsbasic/cnstockbenefitability"+str(year)+"q"+str(quater)+".csv"
    df.to_csv(ret_file_name, index=True, sep=',')
    print("file %s saved" %ret_file_name)

    df = ts.get_operation_data(year,quater)
    ret_file_name = "data/hsbasic/cnstockoperationability"+str(year)+"q"+str(quater)+".csv"
    df.to_csv(ret_file_name, index=True, sep=',')
    print("file %s saved" %ret_file_name)

    df = ts.get_growth_data(year,quater)
    ret_file_name = "data/hsbasic/cnstockgrowthability"+str(year)+"q"+str(quater)+".csv"
    df.to_csv(ret_file_name, index=True, sep=',')
    print("file %s saved" %ret_file_name)

    df = ts.get_debtpaying_data(year,quater)
    ret_file_name = "data/hsbasic/cnstockdebtability"+str(year)+"q"+str(quater)+".csv"
    df.to_csv(ret_file_name, index=True, sep=',')
    print("file %s saved" %ret_file_name)


    df = ts.get_cashflow_data(year,quater)
    ret_file_name = "data/hsbasic/cnstockcashflowability"+str(year)+"q"+str(quater)+".csv"
    df.to_csv(ret_file_name, index=True, sep=',')
    print("file %s saved" %ret_file_name)




if __name__ == "__main__":
    #draw_single_stock_MA('002273')
    #get_all_stock_id()
    #ts.get_hs300s()
    #ts.get_industry_classified()
    #loop_all_stocks()
    #df = ts.get_stock_basics()
    #df.to_csv("data/hsbasic/stocklistbasic.csv", index=True, sep=',')
    #for i in range(6):
    #get_basic_detail_by_history(i+1,2018,2019)
    get_basic_detail_by_quater(2018,1)



