import quantopian.algorithm as algo

stock = sid(8554)
percent = 1

def initialize(context):
    
    algo.schedule_function(
        trade,
        algo.date_rules.every_day(),
        algo.time_rules.market_open(),
    )

def trade(context, data):
    
    stock_data = data.history(stock, 'close', 2, '1d')
    
    if stock_data[-2] - stock_data[-1] > stock_data[-2]/(100/percent):
        order_value(stock, 1000)
