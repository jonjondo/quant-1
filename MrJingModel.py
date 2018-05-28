__author__ = 'lottiwang'

import pandas as pb
import os
import chardet
path='data/hsbasic/'


colOutPutName = {
	'code'   : '股票代码',
    'name'   : '股票名称',
    'industry':'所属行业',
    'pe':'市盈率',
    'pb':'市静率',
    'peg':'市盈率相对盈利增长比率',
    'timeToMarket'   : '上市时间',
    'business_income_good':'主营业务收入',
    'nprg_good'   : '净利润增长率',
    'profits_yoy_good'   : '净利润率',
    'gross_profit_rate_good'   : '毛利率增长',
    'roe_good'   : '净资产收益率',
    'cashflowratio_good'   : '现金流',
    'total_rate'   : '综合评定'
}


class MrJingStockModel:
    def __init__(self):
        self.df_basic = pb.read_csv(os.path.join(path,"stocklistbasic.csv"),usecols=['code', 'name','industry','pe','pb','timeToMarket'])
        self.df_basic = self.df_basic.drop_duplicates(['code'])

    def select_high_roe_and_gross_growth_stock(self,roe_rate,gross_rate,net_rate,business_income_rate):
        df=pb.read_csv(os.path.join(path,"total_cn_stock_benefit_ability.csv"))

        #净资产收益率计算逻辑
        position_roe_gold = (df['roe_2017q4'] > roe_rate) & (df['roe_2016q4'] > roe_rate) & (df['roe_2015q4'] > roe_rate)
        df.loc[position_roe_gold[(position_roe_gold == True) & (position_roe_gold.shift() == False)].index, 'roe_good'] = 1


        #计算毛利率增长逻辑
        position_gross_profit_gold = (df['gross_profit_rate_2017q4'] > gross_rate) & (df['gross_profit_rate_2016q4'] > gross_rate) & (df['gross_profit_rate_2015q4'] > gross_rate)
        df.loc[position_gross_profit_gold[(position_gross_profit_gold == True) & (position_gross_profit_gold.shift() == False)].index, 'gross_profit_rate_good'] = 1

        #净利润率计算逻辑
        position_net_gold = (df['net_profit_ratio_2017q4'] > net_rate) & (df['net_profit_ratio_2016q4'] > net_rate) & (df['net_profit_ratio_2015q4'] > net_rate)
        df.loc[position_net_gold[(position_net_gold == True) & (position_net_gold.shift() == False)].index, 'net_profit_ratio_good'] = 1

         #主营业务收入
        #position_roe_gold_2017 = (df['business_income_2017q4'] > df['business_income_2017q3']) & (df['business_income_2017q3'] > df['business_income_2017q2']) & (df['business_income_2017q2'] > df['business_income_2017q1'])
        #position_roe_gold_2016 = (df['business_income_2016q4'] > df['business_income_2016q3']) & (df['business_income_2016q3'] > df['business_income_2016q2']) & (df['business_income_2016q2'] > df['business_income_2016q1'])
        #position_gold = (position_roe_gold_2017 & position_roe_gold_2016) |  ((df['business_income_2017q4'] - df['business_income_2016q4'])/df['business_income_2016q4'] * 100 > rate)
        #df.loc[position_gold[(position_gold == True) & (position_gold.shift() == False)].index, 'business_income_good'] = 1
        position_net_gold = (((df['business_income_2017q4'] - df['business_income_2016q4'])/df['business_income_2016q4'] * 100 > business_income_rate) & \
                                 ((df['business_income_2016q4'] - df['business_income_2015q4'])/df['business_income_2016q4'] * 100 > business_income_rate))
        df.loc[position_net_gold[(position_net_gold == True) & (position_net_gold.shift() == False)].index, 'business_income_good'] = 1


        #df.loc[position_gold[(position_gold == False) & (position_gold.shift() == True)].index, 'roe_good'] = 0
        df_ret = df[(df['roe_good'] == 1) & (df['gross_profit_rate_good'] == 1) &  (df['net_profit_ratio_good'] == 1) & (df['business_income_good'] == 1)]
        df_ret.to_csv(os.path.join(path,"MrJingModelSelection.csv"),columns=['code','name_x','industry','pe'])
    def select_high_nprg_growth_stock(self,rate):
        pass


if __name__ == "__main__":
    mjsm=MrJingStockModel()
    #roe_rate,gross_rate,net_rate,business_income_rate
    #净资产收益率，毛利率，净利润率，主营业务收入的四个指标
    mjsm.select_high_roe_and_gross_growth_stock(15,40,20,25)