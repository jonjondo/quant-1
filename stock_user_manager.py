__author__ = 'lottiwang'
from data_orm import *
import time
import pandas as pd
import chardet
import wechat_assit as wa
session=''
userlist=[]
stocklist=[]

class StockUserMgr:
    def __init__(self):
        self.engine = create_engine('mysql+pymysql://root:langzm@localhost:3306/quant')
        # 创建DBSession类型
        DBSession = sessionmaker(bind=self.engine)
        self.session = DBSession()
    def __del__(self):
        self.session.close()

    def get_all_stock_ids(self):
        stocks = self.session.query(Stock)
        return list(map((lambda stock: stock.stockcode), stocks))


    def add_stock_record(self,stock_code,stock_name,wxuser_openid,operation):
        stock = self.session.query(Stock).filter(Stock.stockcode == stock_code).first()
        user = self.session.query(User).filter(User.useropenid == wxuser_openid).first()
        if stock !=  None and user != None:
            stockrecord = self.session.query(StockRecord).filter(StockRecord.stockid == stock_code,StockRecord.userid == wxuser_openid).first()
            if stockrecord == None:
                '''
                stockid = Column(Integer,ForeignKey('stock.id'))
                userid = Column(Integer,ForeignKey('wxuser.id'))
                operation  = Column(Integer)
                recordtime = Column(Integer)
                '''
                s=StockRecord(stockid=stock_code,stockname=stock_name,userid=wxuser_openid,operation=operation,recordtime=int(time.time()),noticestatus=0)
                self.session.add(s)
            self.session.commit()
        else:
            print("%s或者%s不存在，需要先添加股票信息"%(stock_code,wxuser_openid))

    def add_stock(self,stock_code,stock_name,industry,marcket,oper):
        '''
        stockcode = Column(String(10))
        stockname = Column(String(25))
        industyid = Column(String(20))
        marketid = Column(String(20))
        operation  = Column(Integer)
        :return:
        '''
        stock = self.session.query(Stock).filter(Stock.stockcode == stock_code).first()
        if stock == None:
            s=Stock(stockcode=stock_code,stockname=stock_name,industyid=industry,marketid=marcket,operation=int(oper))
            self.session.add(s)
        self.session.commit()

    def add_stockrecord_from_csv(self,file):
        df = pd.DataFrame()
        try:
            with open(file, 'rb') as f:
                    result = chardet.detect(f.read())
                    df = pd.read_csv(file,encoding=result['encoding'])
        except:
            print("尝试读取文件%s失败 in add_stockrecord_from_csv ，跳过...."%file)
        '''
               for i in range(len(df.index)):
                        PDM=df.ix[i,'PDM']
                        MDM=df.ix[i,'MDM']
                        if PDM<0 or PDM<MDM:
                            df.ix[i,'DPD']=0
                        else:
                            df.ix[i,'DPD']=PDM
                        if MDM<0 or MDM<PDM:
                            df.ix[i,'DMD']=0
                        else:
                            df.ix[i,'DMD']=MDM
        '''
        for i in range(len(df.index)):
            #print(df.ix[i,'code'],df.ix[i,'stock_name'],df.ix[i,'industry'],df.ix[i,'market'],df.ix[i,'operation'])
            #print(type(df.ix[i,'code']),df.ix[i,'stock_name'],df.ix[i,'industry'],df.ix[i,'market'],df.ix[i,'operation'].astype('int'))
            self.add_stock(df.ix[i,'code'],df.ix[i,'stock_name'],df.ix[i,'industry'].astype(str),df.ix[i,'market'].astype(str),df.ix[i,'operation'].astype(str))
            #add_stock_record(df.ix[i,'code'],df.ix[i,'useropenid'],0)
            self.add_stock_record(df.ix[i,'code'],df.ix[i,'stock_name'],df.ix[i,'useropenid'],df.ix[i,'operation'].astype(str))
    def search_stockrecord_by_stockcode(self,stock_code,advice_oper):
        stockrecord = self.session.query(StockRecord).filter(StockRecord.stockid == stock_code).all()
        if stockrecord != None:
            for sr in stockrecord:
                #print(sr.stockid,sr.userid,sr.operation)
                if sr.operation != advice_oper:
                    self.update_stock_operation(stock_code,advice_oper)
                    oper='WAIT'
                    if advice_oper == -1:
                        oper='SELL'
                    elif advice_oper == 1:
                        oper='BUY'
                    else:
                        oper='WAIT'
                    #print(sr.userid,sr.stockid,search_stockname_by_stockcode(sr.stockid),'--',oper)
                    if sr.noticestatus == 0:
                        wa.send_template_msg(sr.userid,sr.stockid,sr.stockname,'--',oper)

    def search_stockrecord_by_stockcode_semi_rt(self,stock_code, semi_rt_oper, hints):
        stockrecord = self.session.query(StockRecord).filter(StockRecord.stockid == stock_code).all()
        if stockrecord != None:
            for sr in stockrecord:
                #print(sr.stockid,sr.userid,sr.operation)
                oper='WAIT'
                if sr.operation == -1:
                    oper='SELL'
                elif sr.operation == 1:
                    oper='BUY'
                else:
                    oper='WAIT'
                #print(sr.userid,sr.stockid,search_stockname_by_stockcode(sr.stockid),'--',oper)
                if ("" != semi_rt_oper and semi_rt_oper != oper):
                    if semi_rt_oper == 'SELL':
                        oper_value = -1
                    elif semi_rt_oper == 'BUY':
                        oper_value = 1
                    else:
                        oper_value = 0
                    self.update_stock_operation(sr.stockid,oper_value)
                    if semi_rt_oper != 'WAIT' and  sr.noticestatus == 0:
                        wa.send_template_msg_with_hints(sr.userid,sr.stockid,sr.stockname,'--',semi_rt_oper,hints)

    def search_stockname_by_stockcode(self,stock_code):
        stock = self.session.query(Stock).filter(Stock.stockcode == stock_code).first()
        if stock != None:
            return stock.stockname
    def update_stock_operation(self,stock_code,operation):
        stockrecord = self.session.query(StockRecord).filter(StockRecord.stockid == stock_code).update({StockRecord.operation:operation})
        # if stockrecord != None:
        #     for sr in stockrecord:
        #         sr.operation = operation
        self.session.commit()

if __name__ == "__main__":
    # 初始化数据库连接

    sm = StockUserMgr()
    sm.add_stockrecord_from_csv('data/stockimport.csv')
    #stocklist = session.query(Stock).all()
    #userlist = session.query(User).all()
    #search_stockrecord_by_stockcode('SZ.300338')
    #search_stockrecord_by_stockcode('SH.600279')
