import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import talib
import Series

df=ts.get_k_data('600600')
#df['MA10_rolling'] = pd.rolling_mean(df['close'],10)
df['MA10_rolling'] = Series.rolling(window=10,center=False).mean()
close = [float(x) for x in df['close']]

# 调用talib计算10日移动平均线的值
df['MA10_talib'] = talib.MA(np.array(close), timeperiod=10) 
df.tail(12)