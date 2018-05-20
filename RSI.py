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
fig = plt.figure(figsize=[18,5])
plt.plot(df.index,df['RSI'],label='RSI')
plt.plot(df.index,df['MOM'],label='MOB')
# plt.plot(df.index,mydif,label='my dif')
# plt.plot(df.index,mydea,label='my dea')
# plt.plot(df.index,mybar,label='my bar')
plt.legend(loc='best')
#plt.plot(df)
plt.grid()
#记得加这一句，不然不会显示图像
plt.show()