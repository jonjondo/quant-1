# -*- coding: utf-8 -*-

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
        return allusers[0]
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

def add_news(title,html_content):
    access_token,expires_in = get_token_info()
    print(access_token)
    post_url(access_token)
    posturl = 'https://api.weixin.qq.com/cgi-bin/material/add_news?access_token=%s' %access_token
    msg_content = {}
    post_data={}
    msg_content['content'] = html_content
    msg_content['title'] = title
    msg_content['thumb_media_id'] = "f9IEOv60y96L4b6UdeCoHhsaVL9MhZGOiR-Xh6Gqd_U"
    msg_content['author'] = "朗天星量化机器人"
    msg_content['digest'] = "以下是结果，仅供参考和学习分享"
    msg_content['show_cover_pic'] = 1
    msg_content['content_source_url'] = ""
    msg_content['need_open_comment'] = 0
    msg_content['content'] = 1
    post_data['articles'] = []
    post_data['articles'].append(msg_content)
    post_data=json.dumps(post_data)
    print(post_data)
    r = requests.post(posturl,data=post_data)
    result = r.json()
    print(result)


    '''
     “articles”:[{
     “title”: TITLE,
     “thumb_media_id”: THUMB_MEDIA_ID,
     “author”: AUTHOR, “digest” : DIGEST,
     “show_cover_pic”: SHOW_COVER_PIC（0/1）,
     “content” : CONTENT,
     “content_source_url”: CONTENT_SOURCE_URL,
     “need_open_comment” : NEED_OPEN_COMMENT（0/1）,
     “only_fans_can_comment” : ONLY_FANS_CAN_COMMENT（0/1） }]
     //若新增的是多图文素材，则此处应有几段articles结构，最多8段
    '''


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
    #post_url_freshing[1] = 'https://api.weixin.qq.com/cgi-bin/material/add_news?access_token=%s' %access_token
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
def get_pic_list():
    access_token,expires_in = get_token_info()
    print(access_token)
    post_data={}
    post_data['type'] = "image"
    post_data['offset'] = 0
    post_data['count'] = 10
    post_data=json.dumps(post_data)
    print(post_data)
    posturl = "https://api.weixin.qq.com/cgi-bin/material/batchget_material?access_token=%s"%access_token
    r = requests.post(posturl,data=post_data)
    js =  r.json()
    print(js)
    '''
    {'item': [{'media_id': 'f9IEOv60y96L4b6UdeCoHqrh0mcAlJ2jr7VkLOUAFIQ', 'name': 'Aè\x82¡.jpg', 'update_time': 1531441412, 'url': 'http://mmbiz.qpic.cn/mmbiz_jpg/5KMQniarxwicLsEQLyTDrIS0J3JPCIKcX7OHtr5qkVKvGvH6qBwzCZtnBSqbEEiaeEcicUucibXHHqcbZoYIFnS50Ow/0?wx_fmt=jpeg'}, {'media_id': 'f9IEOv60y96L4b6UdeCoHhsaVL9MhZGOiR-Xh6Gqd_U', 'name': 'æ¸¯è\x82¡.jpg', 'update_time': 1531441412, 'url': 'http://mmbiz.qpic.cn/mmbiz_jpg/5KMQniarxwicLsEQLyTDrIS0J3JPCIKcX7N0Ato4xWCSic0HG97sM9xkwIpCLpI7yiaT07TtSYicnaaqqycmtArFy8w/0?wx_fmt=jpeg'}, {'media_id': 'f9IEOv60y96L4b6UdeCoHsor75hdIKkllAaO983LE6Y', 'name': 'ç¾\x8eè\x82¡.jpg', 'update_time': 1531441412, 'url': 'http://mmbiz.qpic.cn/mmbiz_jpg/5KMQniarxwicLsEQLyTDrIS0J3JPCIKcX7tewLgmMXFYNwedWbMdibycmYMTF78fDlFXiaTIaXf7pbn5iahhOgz8DVA/0?wx_fmt=jpeg'}], 'total_count': 3, 'item_count': 3}
    '''

if __name__ == "__main__":
    sendmsgtoalluser("Best Wishes From Gua")
    #add_news("hahahahahahaha","wangpengpengpnpagnasklfjaklds")
    #get_pic_list()
