import quantopian.algorithm as algo

import talib

import numpy as np
import pandas

# MACD SWING ALGORITHM
spy = sid(8554) # SPY
growth = sid(37514) # SPXL
bonds = sid(8554) # SPY

def initialize(context):
    
    algo.schedule_function(
        gather_data,
        algo.date_rules.week_start(),
        algo.time_rules.market_open(minutes=65),
    )
    
    algo.schedule_function(
        trade,
        algo.date_rules.every_day(),
        algo.time_rules.market_open(),
    )
    
    context.macd = None

def gather_data(context, data):
    
    Fast, Slow, Sig = 12, 26, 9
    bars = (Fast + Slow + Sig)*5

    C = data.history(spy, 'price', bars, '1d')  
    C_w = C.resample('1W').last()  
    
    macd, signal, hist = talib.MACD(C_w, Fast, Slow, Sig)

    record(macd = macd[-1], signal = signal[-1], hist = hist[-1])
    context.macd = hist[-1]
        
def trade(context, data):
    
    if context.macd == None:
        return
    
    pos = context.portfolio.positions
    
    if len(pos) == 0:
        if context.macd > 0:
            order_target_percent(growth, 1)
        elif context.macd < 0:
            order_target_percent(bonds, 1)
            
    elif growth in pos:
        if context.macd < 0:
            order_target_percent(growth, 0)
            order_target_percent(bonds, 1)
    
    elif bonds in pos:
        if context.macd > 0:
            order_target_percent(bonds, 0)
            order_target_percent(growth, 1)
