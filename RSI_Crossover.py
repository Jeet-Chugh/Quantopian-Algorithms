# Used to Import the RSI Filter Indicator
import talib

def initialize(context):
    
    context.rsi_stock = sid(351) # AMD has a history of going Oversold -> Overbought
    context.rsi_safe = sid(8554) # SPY as a stock safety
    
    context.long_l,context.short_l = [],[]
    
    schedule_function(rsi_algo, date_rules.every_day(), 
                    time_rules.market_close(hours=1))
   
def rsi_algo(context, data):
    stock,safe = context.rsi_stock,context.rsi_safe
    long_l,short_l = context.long_l,context.short_l
        
    # RSI
    prices = data.history(stock, 'close', 47, '1d')
    rsi = talib.RSI(prices,timeperiod=14)[-1]
    
    bought = stock in context.portfolio.positions
    
    if (rsi < 36 and not bought) or long_l:
        long_l.append(rsi)
        if len(long_l) >= 2:
            if rsi < 36 and long_l[-1] > long_l[-2]:
                order_target_percent(safe,0)
                order_target_percent(stock,1)
                long_l = []
        elif long_l[-1] > 36:
            order_target_percent(safe,0)
            order_target_percent(stock,1)
            long_l = []
    
    if (rsi > 68 and bought) or short_l:
        short_l.append(rsi)
        if len(short_l) >= 2:
            if rsi > 68 and short_l[-1] < short_l[-2]:
                order_target_percent(stock,0)
                order_target_percent(safe,1)
                short_l = []
        elif short_l[-1] < 68:
            order_target_percent(stock,0)
            order_target_percent(safe,1)
            short_l = []
