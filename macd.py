import matplotlib.pyplot as plt
import numpy as np
import talib
import tushare as ts






def my_macd(price, fastperiod=12, slowperiod=26, signalperiod=9):
    macdDIFF, macdDEA, macd = talib.MACDEXT(price, fastperiod=fastperiod, fastmatype=1, slowperiod=slowperiod, slowmatype=1, signalperiod=signalperiod, signalmatype=1)
    macd = macd * 2
    return macdDIFF, macdDEA, macd





if __name__ == "__main__":
    df=ts.get_k_data('600600',start='2018-01-01')
    close = [float(x) for x in df['close']]
    # 调用talib计算指数移动平均线的值
    df['EMA12'] = talib.EMA(np.array(close), timeperiod=6)
    df['EMA26'] = talib.EMA(np.array(close), timeperiod=12)
     # 调用talib计算MACD指标
    df['MACD'],df['MACDsignal'],df['MACDhist'] = talib.MACD(np.array(close),
                                fastperiod=6, slowperiod=12, signalperiod=9)
    df['my_MACD'],df['my_MACDsignal'],df['my_MACDhist'] = my_macd(df['close'].values,
                                fastperiod=6, slowperiod=12, signalperiod=9)
    print(df.tail(12))


    fig = plt.figure(figsize=[18,5])
    #plt.plot(df.index,df['MACD'],label='macd dif')
    #plt.plot(df.index,df['MACDsignal'],label='signal dea')
    plt.plot(df.index,df['MACDhist'] ,label='MACD')
    #plt.plot(df.index,df['my_MACD'],label='my dif')
    #plt.plot(df.index,df['my_MACDsignal'],label='my dea')
    plt.plot(df.index,df['my_MACDhist'],label='my bar')
    plt.legend(loc='best')
    #plt.plot(df)
    plt.grid()
    #记得加这一句，不然不会显示图像
    plt.show()
