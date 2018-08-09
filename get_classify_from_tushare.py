import tushare as ts
import matplotlib.pyplot as plt
import numpy as np
import talib
import pandas as pb
import os
path='data/hsbasic/'

'''
df=ts.get_k_data('600600')
#df['MA10_rolling'] = pd.rolling_mean(df['close'],10)
df['MA10_rolling'] = Series.rolling(window=10,center=False).mean()
close = [float(x) for x in df['close']]

# 调用talib计算10日移动平均线的值
df['MA10_talib'] = talib.MA(np.array(close), timeperiod=10) 
df.tail(12)
'''
def save_classify():
    df = ts.get_industry_classified()
    write = pb.ExcelWriter(os.path.join(path,"行业与概念分类.xlsx"))
    df.to_excel(write,sheet_name='行业分类',index=False)
    df2 = ts.get_concept_classified()
    df2.to_excel(write,sheet_name='概念分类',index=False)
    write.save()

if __name__ == "__main__":
    save_classify()