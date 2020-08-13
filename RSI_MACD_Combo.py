import talib
import quantopian.algorithm as algo

def initialize(context):
    # Stop Loss Usage for Selling in large Dips
    context.sl_track = []
    context.stop_loss = 0.02 # Percent/Day that Triggers Stop Loss
    
    # ============================================================================
    
    # MACD ALGO
    context.macd_bull = sid(37514) # SPXL (3x Bull S&P500)
    context.macd_safety = sid(8554) # SPY (S&P500 Index Fund)
    # Run Algo everyday at Market Open
    algo.schedule_function(macd_algo, 
                           date_rule=algo.date_rules.every_day(),
                           time_rule=algo.time_rules.market_open()
    )
    
    # Daily MACD Tracker, used later in algo
    context.macd_list = []
    
    # Globally Declare Boolean "Flags"
    context.bullish, context.safe = False, True
    
    
    # ============================================================================
    
    
    # RSI ALGO
    context.rsi_stock = sid(37514) # AMD has a history of going Oversold -> Overbought, using SPXL FOR NOW
    context.rsi_safe = sid(8554) # SPY as a stock safety
    
    context.long_l,context.short_l = [],[]
    
    schedule_function(rsi_algo, date_rules.every_day(), 
                    time_rules.market_close(hours=1))
    
    schedule_function(stop_loss, date_rules.every_day(), 
                    time_rules.market_close(minutes=1))
   
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
                order_target_percent(stock,0.5)
                long_l = []
        elif long_l[-1] > 36:
            order_target_percent(safe,0)
            order_target_percent(stock,0.5)
            long_l = []
    
    if (rsi > 68 and bought) or short_l:
        short_l.append(rsi)
        if len(short_l) >= 2:
            if rsi > 68 and short_l[-1] < short_l[-2]:
                order_target_percent(stock,0)
                order_target_percent(safe,0.5)
                short_l = []
        elif short_l[-1] < 68:
            order_target_percent(stock,0)
            order_target_percent(safe,0.5)
            short_l = []
            

def macd_algo(context, data):
    # Allow for the Boolean Flags to be Changed by the Algo
    bull,safety = context.macd_bull,context.macd_safety
    bullish,safe = context.bullish,context.safe
    
    # Buy into our Safety After All Positions are Closed
    if len(context.portfolio.positions) == 0:  order_target_percent(safety,0.5)
    
    # Price Data used for the MACD Indicator Calculations
    # Should Always track Low-Volatility, which is our Safety Stock
    price = data.history(safety, 'close', 40, '1d')
    
    # MACD Indicator Creation
    macd_raw, signal, hist = talib.MACD(price, fastperiod=12, slowperiod=26, signalperiod=9)
    #  Tracking the Recent Histogram Variable, which tracks trend.
    #  Risk Tolerance can be increased or decreased down below
    macd = hist[-1]
    
    # Add to MACD_List if stock shows Bull Flag
    if macd > 0:  context.macd_list.append(macd)
    elif macd < 0:  context.macd_list = []
    
    # CONDITIONS FOR WHEN WE ARE INVESTED IN Safety
    # Buy into Bull if Hist > Risk Tolerance
    if safe and macd >= 0.35:
        order_target_percent(safety,0)
        order_target_percent(bull,0.5)
        safe,bull = False,True
    
    # Use conditions if we are Bullish for > 2 Days
    conditions = len(context.macd_list) >= 2
    if conditions:
        # Daily ROT (rate of change) of MACD Histogram
        difference = context.macd_list[-2] - context.macd_list[-1]
    
    # CONDITIONS FOR WHEN WE ARE INVESTED IN BULL
    # If conditions over risk tolerance 2, or MACD bearish, buy into Safety
    if bullish and ((conditions and difference >= 0.07) or (macd <= 0.35)):
        order_target_percent(bull,0)
        order_target_percent(safety,0.5)
        safe,bullish = True,False
        
def stop_loss(context, data):
    context.sl_track.append(context.portfolio.portfolio_value)
    
    if len(context.sl_track) > 1:
        if context.sl_track[-2] - context.sl_track[-1] > context.stop_loss * context.sl_track[-2]:
            # Liquidate Risky MACD Positions
            order_target_percent(context.macd_safety, 0)
            order_target_percent(context.macd_bull, 0.5)
            
            # Liquidate Risky RSI Positions
            order_target_percent(context.rsi_safe, 0)
            order_target_percent(context.rsi_stock, 0.5)
