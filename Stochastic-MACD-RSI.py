import quantopian.algorithm as algo
import talib

def initialize(context):
    
    # STOCH DEFINITIONS
    context.k_list = []
    context.previous = False
    
    context.safe = sid(44849) #BNDX
    context.stable = sid(8554) # SPY
    context.growth = sid(22009) # SPYG
    context.bull = sid(37514) # TQQQ
    
    context.macd, context.rsi, context.stoch = [], False, False
    
    algo.schedule_function(
        trade,
        algo.date_rules.every_day(),
        algo.time_rules.market_open(),
    )
    
    algo.schedule_function(
        calculate_stoch,
        algo.date_rules.every_day(),
        algo.time_rules.market_close(),
    )
    algo.schedule_function(
        calculate_rsi,
        algo.date_rules.every_day(),
        algo.time_rules.market_close(),
    )
    algo.schedule_function(
        calculate_macd,
        algo.date_rules.every_day(),
        algo.time_rules.market_close(),
    )

def trade(context, data):
    if len(context.portfolio.positions) == 0:
           transact([], context.safe)
           
    if context.macd == [] or context.stoch == False or context.rsi == False:
        return print("Gathering Data")
        
    macd, rsi = context.macd, context.rsi
    stoch_k, stoch_d = context.stoch
           
    bought_safe = context.safe in context.portfolio.positions
    bought_stable = context.stable in context.portfolio.positions
    bought_growth = context.growth in context.portfolio.positions
    bought_bull = context.bull in context.portfolio.positions
           
    if bought_safe or bought_stable:
        if (stoch_k < 20 or stoch_d < 20) and macd[-1] > -1.8:
            transact([context.safe, context.stable], context.bull)
        elif macd[-3] < 0 and macd[-2] > 0:
            transact([context.safe, context.stable], context.growth)
        elif rsi < 40 and macd[-1] > -2:
            if (macd[-1] > macd[-2]) or macd[-1] > 0:
                transact([context.safe, context.stable], context.growth)
        
    if bought_growth:
        if macd[-1] < 1:
            if macd[-1] < -1.5:
                transact([context.growth], context.safe)
            else:
                transact([context.growth], context.stable)
        elif (stoch_k < 20 or stoch_d < 20) and macd[-1] > -1:
            transact([context.safe, context.stable], context.bull)
            
    if bought_bull or context.previous:
        if context.previous and (stoch_d < 80 or stoch_k < 80):
            context.previous = False
            transact([context.bull], context.stable)
        if stoch_d > 80 or stoch_k > 80:
            context.previous = True
            if stoch_k < stoch_d:
                context.previous = False
                transact([context.bull], context.growth)
        
        elif rsi > 60:
            context.previous = False
            transact([context.bull], context.stable)

def calculate_stoch(context, data):
    # Neccessary for indicator calculation inputs
    high_price = max(list(data.history(context.stable, 'high', 14, '1d')))
    low_price = min(list(data.history(context.stable, 'low', 14, '1d')))
    last_close = data.history(context.stable, 'close', 1, '1d').mean()
    
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

def calculate_macd(context, data):
    # MACD Indicator Creation
    prices = data.history(context.stable, 'close', 47, '1d')
    _, _, hist = talib.MACD(prices, fastperiod=12, slowperiod=26, signalperiod=9)
    context.macd = hist[-14:]

def calculate_rsi(context, data):
    # RSI
    prices = data.history(context.stable, 'close', 47, '1d')
    context.rsi = talib.RSI(prices,timeperiod=14)[-1]
    
def transact(sell, buy):
    for stock in sell:  
        order_target_percent(stock, 0)
    order_target_percent(buy, 1)
