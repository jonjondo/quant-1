__author__ = 'lottiwang'

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine
Base = declarative_base()

class User(Base):
    # 表的名字
    __tablename__ = 'wxuser'
    # 表的结构
    id = Column(Integer, primary_key=True,autoincrement=True)
    useropenid = Column(String(30))
    name = Column(String(20))
    remark = Column(String(20))
    groupid = Column(String(20))
    subscribe  = Column(Integer)

    __table_args__ = (
    UniqueConstraint('id', 'useropenid', name='uix_id_useropenid'),
    Index('ix_id_useropenid', 'useropenid', 'name'),
)


class Stock(Base):
    # 表的名字
    __tablename__ = 'stock'
    # 表的结构
    id = Column(Integer, primary_key=True,autoincrement=True)
    stockcode = Column(String(10))
    stockname = Column(String(25))
    industyid = Column(String(20))
    marketid = Column(String(20))
    operation  = Column(Integer)

    __table_args__ = (
    UniqueConstraint('id', 'stockcode', name='uix_id_stockcode'),
    Index('ix_id_stockcode', 'stockcode', 'stockname'),
)


class StockRecord(Base):
    # 表的名字
    __tablename__ = 'stockrecord'
    # 表的结构
    id = Column(Integer, primary_key=True,autoincrement=True)
    stockid = Column(String(10))
    stockname = Column(String(25))
    userid = Column(String(30))
    operation  = Column(Integer)
    recordtime = Column(Integer)
    noticestatus = Column(Integer)

    __table_args__ = (
    UniqueConstraint('id', 'stockid', name='uix_id_stockid'),
    Index('ix_id_stockid', 'stockid', 'stockid','userid'),
)


engine = create_engine('mysql+pymysql://root:langzm@localhost:3306/quant')
Base.metadata.create_all(engine)
