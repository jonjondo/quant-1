# -*- coding: utf-8 -*-
"""
Created on Mon Apr 03 21:24:18 2017

@author: Selay
"""

import requests
import json
import threading

access_token = ''
expires_in = ''
post_url_freshing = ['']
# 字典allusers用于存储 由 索引名和openID构成的键值对
# 微信关注‘测试号’时，会生成openID用于与对应微信账号通讯
# 索引名 是为了便于自己识别和管理而对openID起的别名
allusers = {'王鹏':'o48rB0tHYGOfpB9_eqInFV1OX3h0','==':'o48rB0qa3htdR_RzzG7seKSuEPsY'}

def usersto(users = None):
    if users == None:
        return allusers['王鹏']
    elif users == "All":
        return ','.join(set(allusers.values()))
    else:
        if isinstance(users,list):
            usersinfo = []
            for user in users:
                usersinfo.append(allusers[user])
            return ','.join(set(usersinfo))
        else:
            print("'users' must be a list!")
            return

def json_post_data_generator(content='Hi!你好！',users = None):
    msg_content = {}
    msg_content['content'] = content
    post_data = {}
    post_data['text'] = msg_content
    post_data['touser'] = "%s" % usersto(users)
    post_data['toparty'] = ''
    post_data['msgtype'] = 'text'
    post_data['agentid'] = '9'
    post_data['safe'] = '0'
    #由于字典格式不能被识别，需要转换成json然后在作post请求
    #注：如果要发送的消息内容有中文的话，第三个参数一定要设为False
    return json.dumps(post_data)



def json_post_data_generator_by_openid(content='Hi!你好！',openid = None):
    msg_content = {}
    msg_content['content'] = content
    post_data = {}
    post_data['text'] = msg_content
    post_data['touser'] = "%s" % (openid)
    post_data['toparty'] = ''
    post_data['msgtype'] = 'text'
    post_data['agentid'] = '9'
    post_data['safe'] = '0'
    #由于字典格式不能被识别，需要转换成json然后在作post请求
    #注：如果要发送的消息内容有中文的话，第三个参数一定要设为False
    return json.dumps(post_data)

# 需将此处的APPID,APPSECRET换为自己‘测试号管理’页面内显示的内容
def appInfos():
    APPID = "wx8e5ae8389bb42ffe"
    APPSECRET = "772cba9ec8991bc97b145a240c9f48af"
    return (APPID,APPSECRET)

def get_token_info():
    APPInfo = appInfos()
    r = requests.get("https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" % APPInfo)
    #print "Accessing %s" %r.url
    js =  r.json()
    if "errcode" not in js:
        access_token = js["access_token"]
        expires_in = js["expires_in"]
    else:
        print("Can not get the access_token")
        print(js)
        quit()
    return access_token,expires_in



def post_url(access_token):
    timer = threading.Timer(1000,post_url)
    timer.start()
    post_url_freshing[0] = 'https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=%s' %access_token
    print(post_url_freshing[0])

#post_url()


def get_user_list(access_token):
    r= requests.get("https://api.weixin.qq.com/cgi-bin/user/get?access_token=%s&next_openid="%access_token)
    js =  r.json()
    print(js)
    if "errcode" not in js:
        allopenid = js["data"]
        next_openid = js["next_openid"]
        print(allopenid)
    else:
        print("Can not get the userlist")
        print(js)
        quit()
    return  allopenid

def sender(text_str,user_lis = None):
    posturl = post_url_freshing[0]
    #print(posturl)
    post_data = json_post_data_generator(content=text_str,users = ['=='])
    #print(post_data)
    r = requests.post(posturl,data=post_data)
    result = r.json()
    if result["errcode"] == 0:
        print("Sent successfully")
    else:
        print (result["errmsg"])


def sendmsgtoalluser(text_str):
    access_token,expires_in = get_token_info()
    print(access_token)
    post_url(access_token)
    openidlist = get_user_list(access_token)
    posturl = post_url_freshing[0]
    for id in openidlist['openid']:
        post_data = json_post_data_generator_by_openid(content=text_str,openid = id)
    #print(post_data)
        r = requests.post(posturl,data=post_data)
        result = r.json()
        if result["errcode"] == 0:
            print("Sent successfully")
        else:
            print (result["errmsg"])

if __name__ == "__main__":
    sendmsgtoalluser("Best Wishes From Gua")