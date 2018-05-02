import tushare as ts
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import talib

df=ts.get_k_data('600600')
close = [float(x) for x in df['close']]
df['RSI']=talib.RSI(np.array(close), timeperiod=12)     #RSI的天数一般是6、12、24
df['MOM']=talib.MOM(np.array(close), timeperiod=5)
df.tail(12)