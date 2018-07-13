# -*- coding: utf-8 -*-
import smtplib,time,getopt,sys  
from email.mime.text import MIMEText  
mailto_list=['wangpenghehe@qq.com','11861040@qq.com','3377499@qq.com','55695287@qq.com','zhoubinjason@gmail.com']
mailbcc_list=['2838919549@qq.com']
mailcc_list=['']
#mailto_list=['wangpenghehe@qq.com']
'''

11861040@qq.com
3377499@qq.com
55695287@qq.com
wangpenghehe@qq.com
zhoubinjason@gmail.com
'''
mail_host="smtp.qq.com:465" 
mail_user="wangpenghehe"  
mail_pass="tingting520"   
mail_postfix="qq.com"  
global message
global outfilename
outfilename=''
def GetOpt():
    global outfilename
    opts, args = getopt.getopt(sys.argv[1:], "hf:")
    for op, value in opts: 
        if op == "-f":
            outfilename = value 
        elif op == "-h": 
            usage() 
            sys.exit() 

def usage():
    print("add -f filname to specify a file")
    print("-h help")

def read_file():
    global outfilename
    if len(outfilename)<=0:
        outfilename=time.strftime('validurl/validurl-%Y-%m-%d',time.localtime(time.time()))+ '.txt'
    output = open(outfilename,"r")
    try:
        global message
        message=output.read()
    finally:
        output.close()




def send_mail(to_list,sub,content):
    me="WGQuant Notification"+"<"+mail_user+"@"+mail_postfix+">"
    msg = MIMEText(content,_subtype='html',_charset='utf-8')
    msg['Subject'] = sub  
    msg['From'] = me  
    msg['To'] = ";".join(to_list)  
    recieve = mailto_list
    recieve.extend(mailcc_list)
    recieve.extend(mailbcc_list) 
    try:  
        server = smtplib.SMTP_SSL()  
        server.connect(mail_host)  
        server.login(mail_user,mail_pass)  
        server.sendmail(me, recieve, msg.as_string())  
        server.close()  
        return True  
    except Exception as e:
        print(str(e)  )
        return False
        

def send_mail_withsub(sub,content):
    send_mail(mailto_list,sub,content)

if __name__ == '__main__': 
    GetOpt()
    read_file()
    global message
    strdate=outfilename[outfilename.find('-')+1:outfilename.find('.')]
    if send_mail(mailto_list,"Daily Quant Stock Selection", message):
        print("done")
    else:  
        print("faild")
