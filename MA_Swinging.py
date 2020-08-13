import quantopian.algorithm as algo

stocks = [sid(24),sid(5061),sid(351),sid(19725),sid(3951),sid(46631)]
def initialize(context):
    
    algo.schedule_function(
        trade,
        algo.date_rules.every_day(),
        algo.time_rules.market_open(hours=1),
    )

def trade(context,data):
    global spy,stocks
    
    weight = 1 / len(stocks)
    
    for stock in stocks:
    
        ma_20 = data.history(stock, 'close', 24,'1d').mean()  
        ma_42 = data.history(stock, 'close', 42,'1d').mean()
    
        open_price = data.history(stock, 'close', 1, '1d').mean()
    
        bought = stock in context.portfolio.positions
        
        if open_price > ma_20 and open_price > ma_42 and not bought:
            order_target_percent(stock,weight)
        
        if open_price < ma_20 and bought:
            order_target_percent(stock,0)
