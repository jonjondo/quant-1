__author__ = 'lottiwang'

import pandas as pb
import os
import chardet
path='data/hsbasic/'


colOutPutName = {
	'code'   : '股票代码',
    'name'   : '股票名称',
    'timeToMarket'   : '上市时间',
    'nprg_good'   : '净利润增长率',
    'profits_yoy_good'   : '净利润率',
    'gross_profit_rate_good'   : '毛利率增长',
    'roe_good'   : '净资金收益率',
    'cashflowratio_good'   : '现金流',
    'total_rate'   : '综合评定'
}



def changeOutPutColName(df):
	columns = df.columns
	df.rename(columns=lambda x: colOutPutName.get(x, x), inplace = True)
	return df








df_basic = pb.read_csv(os.path.join(path,"stocklistbasic.csv"),usecols=['code', 'name','timeToMarket'])
df_basic = df_basic.drop_duplicates(['code'])

def calculate_profits_yoy_increase(rate):
    # stock_name = df_basic.loc[(df_basic.code == stock_id)]['name'].values
    # time_market = df_basic.loc[(df_basic.code == stock_id)]['timeToMarket'].values
    # print("代码%s,名称%s 上市日期为%s "%(stock_id,stock_name,time_market))
    try:
        for filename in os.listdir(path):
            if 'quaterreport' in filename:
                print("Processing file %s" %os.path.join(path,filename))
                with open(os.path.join(path,filename), 'rb') as f:
                    result = chardet.detect(f.read())
                df = pb.read_csv(os.path.join(path,filename),encoding=result['encoding'])
                df['code'].astype('str')
                #print(df.columns.values.tolist())
                df = df.drop_duplicates(['code'])
                for stock_id in df_basic['code']:
                    if len(df.loc[(df['code'] == stock_id)]['profits_yoy'].values) > 0:
                        profits_yoy = df.loc[(df['code']  == stock_id)]['profits_yoy'].values[0]
                        #print(profits_yoy)
                    df_basic.loc[(df_basic['code'] == stock_id),'profits_yoy_'+filename[-10:-4]] = profits_yoy
                    #print("%s,%s %s"%(df_basic['code'].values[0],stock_id,profits_yoy))
                    profits_yoy = ""
                    # stock_data.loc[kdj_position_die[(kdj_position_die == False) & (kdj_position_die.shift() == True)].index, 'KDJ_金叉死叉'] = -1
                #print(df_basic)
            df_basic.to_csv(os.path.join(path,'A股净利润同比.csv'))
    except Exception as e:
        print(e.message)



#测试用的一个函数,暂时别管，大概意思是算了下条件筛选。
def select_yoyo_profits_ret():

     #print(df)
     position_gold = (df['profits_yoy_2017q4'] > df['profits_yoy_2017q3']) & (df['profits_yoy_2017q3'] > df['profits_yoy_2017q2']) & (df['profits_yoy_2017q2'] > df['profits_yoy_2017q1'])
     df.loc[position_gold[(position_gold == True) & (position_gold.shift() == False)].index, '优质'] = 1
     df2=df[df['优质'] == 1]
     df2.to_csv(os.path.join(path,"2017利润率优质股.csv"))




def select_high_nprg_growth_stock(rate):
    df=pb.read_csv(os.path.join(path,"total_cn_stock_growth_ability.csv"))
    position_gold_2017 = (df['nprg_2017q4'] > df['nprg_2017q3']) & (df['nprg_2017q3'] > df['nprg_2017q2']) & (df['nprg_2017q2'] > df['nprg_2017q1'])
    position_gold_2016 = (df['nprg_2016q4'] > df['nprg_2016q3']) & (df['nprg_2016q3'] > df['nprg_2016q2']) & (df['nprg_2016q2'] > df['nprg_2016q1'])
    position_gold = position_gold_2017 & position_gold_2016 | (df['nprg_2017q4'] - df['nprg_2016q4'] > rate)
    df.loc[position_gold[(position_gold == True) & (position_gold.shift() == False)].index, 'nprg_good'] = 1
    #df.loc[position_gold[(position_gold == False) & (position_gold.shift() == True)].index, 'nprg_good'] = 0
    #df2=df[df['优质'] == 1]
    #df2.to_csv(os.path.join(path,"连续两年利润率增长表.csv"),columns=['code','name_x','timeToMarket','nprg_2017q1','nprg_2017q2','nprg_2017q3','nprg_2017q4','nprg_2018q1'])
    return  df

def select_high_profits_yoy_growth_stock(rate):
    df=pb.read_csv(os.path.join(path,"total_profits_yoy.csv"))
    position_gold_2017 = (df['profits_yoy_2017q4'] > df['profits_yoy_2017q3']) & (df['profits_yoy_2017q3'] > df['profits_yoy_2017q2']) & (df['profits_yoy_2017q2'] > df['profits_yoy_2017q1'])
    position_gold_2016 = (df['profits_yoy_2016q4'] > df['profits_yoy_2016q3']) & (df['profits_yoy_2016q3'] > df['profits_yoy_2016q2']) & (df['profits_yoy_2016q2'] > df['profits_yoy_2016q1'])
    position_gold = position_gold_2017 | position_gold_2016
    df.loc[position_gold[(position_gold == True) & (position_gold.shift() == False)].index, 'profits_yoy_good'] = 1
    #df.loc[position_gold[(position_gold == False) & (position_gold.shift() == True)].index, 'profits_yoy_good'] = 0
    #df2=df[df['优质'] == 1]
    #df2.to_csv(os.path.join(path,"连续两年利润率同比增长表.csv"),columns=['code','name','timeToMarket','profits_yoy_2017q1','profits_yoy_2017q2','profits_yoy_2017q3','profits_yoy_2017q4','profits_yoy_2018q1'])
    return  df

def select_high_roe_gross_profits_stock(rate):
    df=pb.read_csv(os.path.join(path,"total_cn_stock_benefit_ability.csv"))
    #计算毛利率增长逻辑
    position_gold_2017 = (df['gross_profit_rate_2017q4'] > df['gross_profit_rate_2017q3']) & (df['gross_profit_rate_2017q3'] > df['gross_profit_rate_2017q2']) & (df['gross_profit_rate_2017q2'] > df['gross_profit_rate_2017q1'])
    position_gold_2016 = (df['gross_profit_rate_2016q4'] > df['gross_profit_rate_2016q3']) & (df['gross_profit_rate_2016q3'] > df['gross_profit_rate_2016q2']) & (df['gross_profit_rate_2016q2'] > df['gross_profit_rate_2016q1'])
    position_gold = position_gold_2017 & position_gold_2016 | (df['gross_profit_rate_2017q4'] > df['gross_profit_rate_2016q4'])
    df.loc[position_gold[(position_gold == True) & (position_gold.shift() == False)].index, 'gross_profit_rate_good'] = 1
    #df.loc[position_gold[(position_gold == False) & (position_gold.shift() == True)].index, 'gross_profit_rate_good'] = 0



    #净资产收益率计算逻辑
    position_roe_gold_2017 = (df['roe_2017q4'] > df['roe_2017q3']) & (df['roe_2017q3'] > df['roe_2017q2']) & (df['roe_2017q2'] > df['roe_2017q1'])
    position_roe_gold_2016 = (df['roe_2016q4'] > df['roe_2016q3']) & (df['roe_2016q3'] > df['roe_2016q2']) & (df['roe_2016q2'] > df['roe_2016q1'])
    position_gold = (position_roe_gold_2017 & position_roe_gold_2016) |(df['roe_2017q4'] - df['roe_2016q4'] > rate)

    df.loc[position_gold[(position_gold == True) & (position_gold.shift() == False)].index, 'roe_good'] = 1
    #df.loc[position_gold[(position_gold == False) & (position_gold.shift() == True)].index, 'roe_good'] = 0


    df2=df.loc[(df['code']) >0,['code','gross_profit_rate_good','roe_good']]
    #df2=df.loc[True,['code','name_x','gross_profit_rate_good']]
    #print(df2)
    #df2.to_csv(os.path.join(path,"连续两年利润率同比增长表.csv"),columns=['code','name','timeToMarket','profits_yoy_2017q1','profits_yoy_2017q2','profits_yoy_2017q3','profits_yoy_2017q4','profits_yoy_2018q1'])
    return  df2


def select_high_cash_ratio_stock(rate):
    df=pb.read_csv(os.path.join(path,"total_cn_stock_cash_flow.csv")) #cashflowratio
    position_gold_2017 = (df['cashflowratio_2017q4'] > df['cashflowratio_2017q3']) & (df['cashflowratio_2017q3'] > df['cashflowratio_2017q2']) & (df['cashflowratio_2017q2'] > df['cashflowratio_2017q1'])
    position_gold_2016 = (df['cashflowratio_2016q4'] > df['cashflowratio_2016q3']) & (df['cashflowratio_2016q3'] > df['cashflowratio_2016q2']) & (df['cashflowratio_2016q2'] > df['cashflowratio_2016q1'])
    position_gold = position_gold_2017 & position_gold_2016 | (df['cashflowratio_2017q4'] - df['cashflowratio_2016q4'] > rate)
    df.loc[position_gold[(position_gold == True) & (position_gold.shift() == False)].index, 'cashflowratio_good'] = 1
    #df.loc[position_gold[(position_gold == False) & (position_gold.shift() == True)].index, 'cashflowratio_good'] = 0
    df2=df.loc[(df['code']) >0,['code','cashflowratio_good']]
    #df2=df.loc[True,['code','name_x','gross_profit_rate_good']]
    #print(df2)
    #df2.to_csv(os.path.join(path,"连续两年利润率同比增长表.csv"),columns=['code','name','timeToMarket','profits_yoy_2017q1','profits_yoy_2017q2','profits_yoy_2017q3','profits_yoy_2017q4','profits_yoy_2018q1'])
    return  df2


def merge_canslim_c_result():
    df=pb.merge(df_basic,select_high_nprg_growth_stock(15),on='code',how='left')
    df=pb.merge(df,select_high_profits_yoy_growth_stock(0),on='code',how='left')
    df=pb.merge(df,select_high_roe_gross_profits_stock(15),on='code',how='left')
    df=pb.merge(df,select_high_cash_ratio_stock(10),on='code',how='left')
    #df.reset_index(drop=True).drop_duplicates(['code'])
    df['code']=df['code'].astype(str).str.zfill(6)
    df['gross_profit_rate_good'].astype('float')
    df['profits_yoy_good'].astype('float')
    df['nprg_good'].astype('float')
    df['roe_good'].astype('float')
    df['cashflowratio_good'].astype('float')
    df = df.fillna(0)
    #value = (df['gross_profit_rate_good'] + df['profits_yoy_good'] + df['nprg_good'] + df['roe_good'] + df['cashflowratio_good'] >= 4)
    #print(df['gross_profit_rate_good'].values + df['profits_yoy_good'].values + df['nprg_good'].values + df['roe_good'].values + df['cashflowratio_good'].values)
    #df.loc[value[(value == True) & (value.shift() == False)].index, 'total_rate'] = ""
    #df['total_rate'] = df.apply(lambda x: x['gross_profit_rate_good'] + x['profits_yoy_good']+ x['nprg_good']+ x['roe_good']+ df['cashflowratio_good'] , axis=1)
    df['total_rate'] = df['gross_profit_rate_good'] + df['profits_yoy_good'] + df['nprg_good'] + df['roe_good'] + df['cashflowratio_good']
    df= df.sort_values(by=['total_rate'],ascending=False)
    #df = changeOutPutColName(df)
    print(df)
    df[df['total_rate'] >= 3].to_csv(os.path.join(path,"利润率增长优质标底.csv"),columns=['code','name_x','timeToMarket','nprg_good','profits_yoy_good','gross_profit_rate_good','roe_good','cashflowratio_good','total_rate'])


if __name__ == "__main__":
    #calculate_profits_yoy_increase()
    #select_yoyo_profits_ret()
    #select_high_gross_profits_stock()
    merge_canslim_c_result()
    #print(df)
