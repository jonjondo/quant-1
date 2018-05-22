__author__ = 'lottiwang'
import pandas as pb

df_total = pb.read_csv("data/hsbasic/stocklistbasic.csv",encoding='gbk')
df_cashflow_2017_q1 = pb.read_csv("data/hsbasic/hsstockcashflowability2017q1.csv",encoding='gbk')
#df_total.join(df_cashflow_2017_q1,on='code',how='left',lsuffix='_LEFT')
df_total = pb.merge(df_total,df_cashflow_2017_q1,on = 'code')
df_total.to_csv("data/hsbasic/join_ret.csv")
# import pandas as pd
# import numpy as np
# df1 = pd.DataFrame(np.array([['a', 5, 9], ['b', 4, 61], ['c', 24, 9]]),
#                    columns = ['name', 'attr11', 'attr12'])
# df2 = pd.DataFrame(np.array([['a', 5, 19], ['c', 14, 16], ['b', 4, 9]]),
#                    columns = ['name', 'attr21', 'attr22'])
# df3 = pd.DataFrame(np.array([['c', 15, 49], ['b', 4, 36], ['a', 14, 9]]),
#                    columns = ['name', 'attr31', 'attr32'])
# print(df1)
# print(df2)
# print(df3)
# print(pd.merge(pd.merge(df1, df2, on = 'name'), df3, on = 'name'))