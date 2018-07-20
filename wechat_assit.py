__author__ = 'lottiwang'
from wechatpy import WeChatClient
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import create_engine
from data_orm import *
import time
APPID = "wx8e5ae8389bb42ffe"
APPSECRET = "772cba9ec8991bc97b145a240c9f48af"
session = None


client = WeChatClient('wx8e5ae8389bb42ffe', '772cba9ec8991bc97b145a240c9f48af')

def update_wechat_userinfo(client,session):
    user = client.user.get_followers()
    print(user)

    user_info = client.user.get_batch(user['data']['openid'])
    print(user_info)
    for info in user_info:
        user = session.query(User).filter(User.useropenid == info['openid']).first()
        if user == None:
            u=User(useropenid=info['openid'],name=info['nickname'],remark=info['remark'],groupid=info['groupid'],subscribe=info['subscribe'])
            session.add(u)
    session.commit()


def search_user_by_name(username):
    # 创建Query查询, filter是where条件, 最后调用one()返回唯一行, 如果调用all()则返回所有行.
    user = session.query(User).filter(User.name==username).one()
    print('name:', user.name)
    print('openid:', user.useropenid)
    session.close()

def send_template_msg(userid,stockname,stockid,price,operation):
    data={}
    if operation == 'SELL':
        caption = '您关注的股票触发卖出提醒'
        opcolor = "#00FF00"
        tmpid = 'MHyi8np240SK4TD5tLqWPhna9Bg2Xdh9dUUsJAouqsc'
    else:
        caption = '您关注的股票触发买入提醒'
        opcolor = "#FF0000"
        tmpid = '2ab6uPK6RdLotx4599G-Cpo3Br_yrNuUeUf9tzovxE0'

    data['first']={'value':caption,'color':opcolor}
    data['keyword1']={'value': stockname,'color':"#173177"}
    data['keyword2']={'value': stockid,'color':"#173177"}
    data['keyword3']={'value': operation,'color':opcolor}
    data['keyword4']={'value': price,'color':"#173177"}
    data['keyword5']={'value': time.strftime("%Y%m%d %H:%M",time.localtime(time.time()))}
    data['remark']={'value':'以上信息只提示一次，不会反复，建议仅供参考','color':"#FF0000"}
    '''
    {{first.DATA}}
    股票名称：{{keyword1.DATA}}
    股票代码：{{keyword2.DATA}}
    操作类型：{{keyword3.DATA}}
    卖出价格：{{keyword4.DATA}}
    交易时间：{{keyword5.DATA}}
    {{remark.DATA}}
    '''

    client.message.send_template(userid,tmpid,data,None,None)

if __name__ == "__main__":
    client = WeChatClient('wx8e5ae8389bb42ffe', '772cba9ec8991bc97b145a240c9f48af')
    # 初始化数据库连接
    engine = create_engine('mysql+pymysql://root:langzm@localhost:3306/quant?charset=utf8')
    # 创建DBSession类型
    DBSession = sessionmaker(bind=engine)
    session = DBSession()
    update_wechat_userinfo(client,session)
    session.close()
    #search_user_by_name('==')
    #send_template_msg('o48rB0jO_sMoLTa7iuco_T0l3Ucw','舍图控股','HK.08392',0.89,'SELL')
    #send_template_msg('o48rB0sXHkHtzJreikUonwvJBJB0','新城发展控股','HK.01030',6.5,'BUY')










