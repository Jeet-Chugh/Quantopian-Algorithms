import quantopian.algorithm as algo
from quantopian.algorithm import attach_pipeline, pipeline_output  
from quantopian.pipeline import Pipeline  
from quantopian.pipeline.factors import AverageDollarVolume
from quantopian.pipeline.data.builtin import USEquityPricing
import talib

def initialize(context):
    
    context.num_of_stocks = 5
    context.weight = 1 / context.num_of_stocks
    
    context.short, context.buy = False, False
    context.stop_trading = False
    
    algo.schedule_function(
        rebalance,
        algo.date_rules.every_day(),
        algo.time_rules.market_open(hours=6)
    )
    algo.schedule_function(
        resume_trading,
        algo.date_rules.every_day(),
        algo.time_rules.market_close()
    )
    
    algo.attach_pipeline(high_volume_screener(context), 'screener')
    
def handle_data(context, data):
    if context.stop_trading:  return
    weight = context.weight
    
    for stock in context.stocks:
        bought = stock in context.portfolio.positions
        try:
            price_history = data.history(stock, 'close', 50, '1m')
            ema_5 = talib.EMA(price_history, timeperiod = 5)[-1]
            ema_8 = talib.EMA(price_history, timeperiod = 8)[-1]
            ema_13 = talib.EMA(price_history, timeperiod = 13)[-1]
        except:  return
        if not bought:
            if ema_5 > ema_13 and ema_8 > ema_13 and ema_5 > ema_8:
                context.buy = True
                order_target_percent(stock, weight)
            elif ema_5 < ema_13 and ema_8 < ema_13 and ema_5 < ema_8:
                context.short = True
                order_target_percent(stock, -weight)
        elif bought:
            if context.short:
                if ema_5 > ema_8:
                    context.short = False
                    order_target_percent(stock, 0)
            elif context.buy:
                if ema_5 < ema_8:
                    context.buy = False
                    order_target_percent(stock, 0)
    
def rebalance(context, data):
    context.stop_trading = True
    for stock in context.portfolio.positions:
        order_target_percent(stock, 0)

def before_trading_start(context, data):
    
    context.output = algo.pipeline_output('screener')
    context.stocks = context.output.index
    
def high_volume_screener(context):
    
    pipe = Pipeline()
    
    last_close = USEquityPricing.close.latest
    under_10 = last_close < 5
    dollar_volume = AverageDollarVolume(window_length=3).top(context.num_of_stocks, mask=under_10)
    
    screens = dollar_volume
    pipe.set_screen(screens)
    
    return pipe

def resume_trading(context, data):  context.stop_trading = False
