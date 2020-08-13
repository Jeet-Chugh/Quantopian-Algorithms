# Import MACD Indicator
import talib

# DEFAULT IMPORTS
import quantopian.algorithm as algo

# CHOOSE A STOCK FOR A BULLISH / STABLE Scenario
# Personally, SPY for safety, SPXL for bullish

def initialize(context):
    
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

def macd_algo(context, data):
    # Allow for the Boolean Flags to be Changed by the Algo
    macd_list = context.macd_list
    bull,safety = context.macd_bull,context.macd_safety
    bullish,safe = context.bullish,context.safe
    
    # Buy into our Safety After All Positions are Closed
    if len(context.portfolio.positions) == 0:  order_target_percent(safety,1)
    
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
        order_target_percent(bull,1)
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
        order_target_percent(safety,1)
        safe,bullish = True,False
