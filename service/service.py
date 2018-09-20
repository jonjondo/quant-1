from flask import Flask
from ServiceCore import  *
from flask import render_template
import time
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/viewdmi2/<stock>')
def viewdmi2(stock):
    stock = stock.upper()
    if "US" in stock or "SH" in stock or "SZ" in stock or "HK" in stock:
        wgs=WhiteGuardStockCore()
        wgs.start_connect('118.89.22.76',11111)
        wgs.get_stock_dmi_my_signal(stock,'2018-1-1',time.strftime("%Y-%m-%d",time.localtime(time.time())))

        wgs.clear_quote()
        return '<img src=../static/' + stock + '.png +><img>'
    else:
        return  '不认识这个代码'
@app.route('/hsi/')
def hsi():
    with open('hsi.txt', 'r') as f2:
        strContent = f2.read()
        buy = strContent.split(',')[0]
        sell = strContent.split(',')[1]
    return render_template("hsi.html",date= time.strftime("%Y-%m-%d",time.localtime(time.time())),buy=buy,sell=sell)

if __name__ == '__main__':
    app.run(
        host = '0.0.0.0',
        port = 8100,
    )
