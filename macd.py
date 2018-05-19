import matplotlib.pyplot as plt
import numpy as np
import talib
import tushare as ts
df=ts.get_k_data('600600')
close = [float(x) for x in df['close']]
# 调用talib计算指数移动平均线的值
df['EMA12'] = talib.EMA(np.array(close), timeperiod=6)  
df['EMA26'] = talib.EMA(np.array(close), timeperiod=12)   
 # 调用talib计算MACD指标
df['MACD'],df['MACDsignal'],df['MACDhist'] = talib.MACD(np.array(close),
                            fastperiod=6, slowperiod=12, signalperiod=9)   
print(df.tail(12))
plt.plot(df)
plt.show()