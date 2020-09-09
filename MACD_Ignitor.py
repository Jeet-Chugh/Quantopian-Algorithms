import quantopian.algorithm as algo
import talib

def initialize(context):
    
    context.stock = sid(8554)
    context.bonds = sid(44849)
    
    context.macd_list = []
    
    algo.schedule_function(
        buy,
        algo.date_rules.every_day(),
        algo.time_rules.market_open()
    )

    algo.schedule_function(
        sell,
        algo.date_rules.every_day(),
        algo.time_rules.market_open(hours=6)
    )


def buy(context, data):
    price = data.history(context.stock, 'close', 40, '1d')
    macd_raw, signal, hist = talib.MACD(price, fastperiod=12, slowperiod=26, signalperiod=9)
    macd = hist[-1]
    
    context.macd_list.append(macd)
    if len(context.macd_list) > 3:
        del context.macd_list[0]
    if len(context.macd_list) == 3:
        print(context.macd_list)
        if context.macd_list[0] < 0 and context.macd_list[1] > 0 and context.macd_list[2] > 0:
            print('Buy')
            order_target_percent(context.bonds, 0)
            order_target_percent(context.stock, 1)

def sell(context, data):
    if context.stock in context.portfolio.positions:
        order_target_percent(context.stock, 0)
        order_target_percent(context.bonds, 1)
