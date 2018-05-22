__author__ = 'lottiwang'
import pandas as pb
import os
import chardet

path='data/hsbasic/'
def get_total_report(report_type,out_file_name):
    try:
        df_basic = pb.read_csv(os.path.join(path,"stocklistbasic.csv"))
        for filename in os.listdir(path):
            if report_type in filename:
                print("Processing file %s" %os.path.join(path,filename))
                with open(os.path.join(path,filename), 'rb') as f:
                    result = chardet.detect(f.read())
                df = pb.read_csv(os.path.join(path,filename),encoding=result['encoding'])
                for i in range(3,df.columns.size):
                    #df.columns.values[i]=df.columns.values[i] + '_' +filename[-10:-4]
                    df = df.rename(columns={df.columns.values[i]: df.columns.values[i] + '_' +filename[-10:-4]})
                #print(df.columns.values.tolist())
                #print(df)
                df_basic = pb.merge(df_basic,df,on='code')
        df_basic = df_basic.drop_duplicates(['code'])
        df_basic.to_csv(os.path.join(path,out_file_name))
        print("file %s saved!"%os.path.join(path,out_file_name))
    except Exception as e:
        print(e.message)
if __name__ == "__main__":
    get_total_report('cashflow','total_cn_stock_cash_flow.csv')
    get_total_report('benefitability','total_cn_stock_benefit_ability.csv')
    get_total_report('debtability','total_cn_stock_debt_ability.csv')
    get_total_report('growthability','total_cn_stock_growth_ability.csv')
    get_total_report('operationability','total_cn_stock_operation_ability.csv')
    get_total_report('quaterreport','total_cn_stock_quater_report.csv')




 # df_cashflow_2017_q1 = pb.read_csv("data/hsbasic/cnstockcashflowability2017q1.csv")
# df_cashflow_2017_q2 = pb.read_csv("data/hsbasic/cnstockcashflowability2017q2.csv")
# df_cashflow_2017_q3 = pb.read_csv("data/hsbasic/cnstockcashflowability2017q3.csv")
# df_cashflow_2017_q4 = pb.read_csv("data/hsbasic/cnstockcashflowability2017q4.csv")
# #df_total.join(df_cashflow_2017_q1,on='code',how='left',lsuffix='_LEFT')
# df_total = pb.merge(pb.merge(pb.merge(pb.merge(df_total,df_cashflow_2017_q1,on = 'code'),df_cashflow_2017_q2,on = 'code'),df_cashflow_2017_q3,on = 'code'),df_cashflow_2017_q4,on = 'code')
# df_total.to_csv("data/hsbasic/join_ret.csv")
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