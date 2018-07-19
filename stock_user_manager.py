__author__ = 'lottiwang'
from data_orm import *
import time
import pandas as pd
import chardet

session=''
def add_stock_record(stock_code,wxuser_openid,operation):
    stock = session.query(Stock).filter(Stock.stockcode == stock_code).first()
    user = session.query(User).filter(User.useropenid == wxuser_openid).first()
    if stock !=  None and user != None:
        stockrecord = session.query(StockRecord).filter(StockRecord.stockid == stock_code).first()
        if stockrecord == None:
            '''
            stockid = Column(Integer,ForeignKey('stock.id'))
            userid = Column(Integer,ForeignKey('wxuser.id'))
            operation  = Column(Integer)
            recordtime = Column(Integer)
            '''
            s=StockRecord(stockid=stock_code,userid=wxuser_openid,operation=operation,recordtime=time.strftime("%Y%m%d %H:%M",time.localtime(time.time())))
            session.add(s)
        session.commit()
    else:
        print("%s或者%s不存在，需要先添加股票信息"%(stock_code,wxuser_openid))

def add_stock(stock_code,stock_name,industry,marcket,oper):
    '''
    stockcode = Column(String(10))
    stockname = Column(String(25))
    industyid = Column(String(20))
    marketid = Column(String(20))
    operation  = Column(Integer)
    :return:
    '''
    stock = session.query(Stock).filter(Stock.stockcode == stock_code).first()
    if stock == None:
        s=Stock(stockcode=stock_code,stockname=stock_name,industyid=industry,marketid=marcket,operation=int(oper))
        session.add(s)
    session.commit()

def add_stockrecord_from_csv(file):
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
        add_stock(df.ix[i,'code'],df.ix[i,'stock_name'],df.ix[i,'industry'],df.ix[i,'market'],df.ix[i,'operation'])
        add_stock_record(df.ix[i,'code'],df.ix[i,'stock_name'],int(df.ix[i,'operation']))



if __name__ == "__main__":
    # 初始化数据库连接
    engine = create_engine('mysql+pymysql://root:@localhost:3306/quant')
    # 创建DBSession类型
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    add_stockrecord_from_csv('data/stockimport.csv')
