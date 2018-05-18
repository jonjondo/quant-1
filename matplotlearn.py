# 导入futuquant api
import futuquant as ft

# 实例化行情上下文对象
quote_ctx = ft.OpenQuoteContext(host="119.29.141.202", port=11111)

# 上下文控制
quote_ctx.start()              # 开启异步数据接收
quote_ctx.stop()               # 停止异步数据接收
quote_ctx.set_handler(handler) # 设置用于异步处理数据的回调对象

# 低频数据接口
quote_ctx.get_trading_days(market, start_date=None, end_date=None)    # 获取交易日
quote_ctx.get_stock_basicinfo(market, stock_type='STOCK')             # 获取股票信息
quote_ctx.get_history_kline(code, start=None, end=None, ktype='K_DAY', autype='qfq')  # 获取历史K线
quote_ctx.get_autype_list(code_list)                                  # 获取复权因子
quote_ctx.get_market_snapshot(code_list)                              # 获取市场快照
quote_ctx.get_plate_list(market, plate_class)                         # 获取板块集合下的子板块列表
quote_ctx.get_plate_stock(market, stock_code)                         # 获取板块下的股票列表

# 高频数据接口
quote_ctx.get_stock_quote(code_list) # 获取报价
quote_ctx.get_rt_ticker(code, num)   # 获取逐笔
quote_ctx.get_cur_kline(code, num, ktype=' K_DAY', autype='qfq') # 获取当前K线
quote_ctx.get_order_book(code)       # 获取摆盘
quote_ctx.get_rt_data(code)          # 获取分时数据
quote_ctx.get_broker_queue(code)     # 获取经纪队列


# 实例化港股交易上下文对象
trade_hk_ctx = ft.OpenHKTradeContext(host="119.29.141.202", port=11111)

# 实例化美股交易上下文对象
trade_us_ctx = ft.OpenUSTradeContext(host="119.29.141.202", port=11111)

# 交易接口列表
ret_code, ret_data = trade_hk_ctx.unlock_trade(password='123456')                # 解锁接口
ret_code, ret_data = trade_hk_ctx.place_order(price, qty, strcode, orderside, ordertype=0, envtype=0) # 下单接口
ret_code, ret_data = trade_hk_ctx.set_order_status(status, orderid=0, envtype=0) # 设置订单状态
ret_code, ret_data = trade_hk_ctx.change_order(price, qty, orderid=0, envtype=0) # 修改订单
ret_code, ret_data = trade_hk_ctx.accinfo_query(envtype=0)                       # 查询账户信息
ret_code, ret_data = trade_hk_ctx.order_list_query(statusfilter="", envtype=0)   # 查询订单列表
ret_code, ret_data = trade_hk_ctx.position_list_query(envtype=0)                 # 查询持仓列表
ret_code, ret_data = trade_hk_ctx.deal_list_query(envtype=0)                     # 查询成交列表
