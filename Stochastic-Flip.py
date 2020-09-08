# Algo for Schedule_Function, Talib for MACD
import quantopian.algorithm as algo
import talib

def initialize(context):
    
    # Lists neccessary for keeping track of indicators
    context.k_list = []
    context.stoch = ()
    context.hist = 0
    # Stocks that I have choosen to use
    context.spy = sid(8554) # Safety Stock (QQQ, VTI)
    context.long_stock = sid(37514) # Bullish Stock (TQQQ, SPXL)
    
    # Calculates Indicators at EOD
    algo.schedule_function(
        calculate,
        algo.date_rules.every_day(),
        algo.time_rules.market_close()
    )
    
    # Trades at the Market Open
    algo.schedule_function(
        trade,
        algo.date_rules.every_day(),
        algo.time_rules.market_open(minutes=1)
    )

def trade(context, data):
    if context.stoch == ():
        return print("Gathering Stochastic Data")
    
    # Buy the Stock if Stochs < 20
    stoch_k, stoch_d = context.stoch
    if not context.long_stock in context.portfolio.positions:
        if stoch_k < 20 and stoch_d < 20 and context.hist[-1] > -2:
            order_target_percent(context.spy, 0)
            order_target_percent(context.long_stock, 1)
    # Sell when Stochs > 80
    elif context.long_stock in context.portfolio.positions:
        if stoch_k > 80 and stoch_d > 80:
            order_target_percent(context.long_stock, 0)
            order_target_percent(context.spy, 1)
    
def calculate(context, data):
    # Neccessary for indicator calculation inputs
    high_price = max(list(data.history(context.spy, 'high', 14, '1d')))
    low_price = min(list(data.history(context.spy, 'low', 14, '1d')))
    last_close = data.history(context.spy, 'close', 1, '1d').mean()
    
    # Calculates Stochastic Indicator
    stoch_k = 100 * ((last_close - low_price) / (high_price - low_price))
    # Add to the List, for the %K Value
    context.k_list.append(stoch_k)
    # Make sure the length of the %D list is always 3
    if len(context.k_list) > 3:
        del context.k_list[0]
    # Calculate %D, update context.stoch
    if len(context.k_list) == 3:
        stoch_d = sum(context.k_list) / len(context.k_list)
        context.stoch = (stoch_k, stoch_d)
    # Include MACD to make the algo semi-recession-proof
    price = data.history(context.spy, 'close', 40, '1d')
    macd_raw, signal, context.hist = talib.MACD(price, fastperiod=12, slowperiod=26, signalperiod=9)
