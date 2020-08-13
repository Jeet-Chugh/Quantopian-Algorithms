import quantopian.algorithm as algo
import talib
# Put Your tickers along with the SID Below:
stocks = {"AAPL" : sid(24), "MACD" : sid(4707), "MSFT" : sid(5061), "ORCL" : sid(5692), "GOOG" : sid(46631)}
weight = 1/len(stocks.keys()) # Weightage for Buying Stocks
stop_loss = 0.08 # Percentage of Stop Loss

def initialize(context):
    
    context.SL = StopLoss_Manager(pct_trail=0.05)
    
    # Weightage for buying SPY between sells
    context.spy = 0
    # Trade Everyday at market close
    algo.schedule_function(
        trade,
        algo.date_rules.every_day(),
        algo.time_rules.market_close(),
    )

def trade(context, data):
    for ticker,stock in stocks.items():
        
        long_term = data.history(stock,'price',110,'1d')
        price = data.history(stock,'price',1,'1d')[-1]
        bought = stock in context.portfolio.positions
        
        if not bought and price == min(long_term):
            context.spy -= weight
            order_target_percent(sid(8554),context.spy)
            order_target_percent(stock,weight)
            
        elif bought and price > list(sorted(long_term))[-5] and long_term[-1] < long_term[-2]:
            order_target_percent(stock,0)
            context.spy += weight
            order_target_percent(sid(8554),context.spy)
            
    if len(context.portfolio.positions) == 0:
        context.spy = 1
        order_target_percent(sid(8554),context.spy)
    else:
        context.SL.manage_orders(context, data)
        
class StopLoss_Manager:
    """
    Example Usage:
        context.SL = StopLoss_Manager(pct_init=0.005, pct_trail=0.03)
        context.SL.manage_orders(context, data)
    """
                
    def set_params(self, **params):
        """
        Set values of parameters:
        
        pct_init (optional float between 0 and 1):
            - After opening a new position, this value 
              is the percentage above or below price, 
              where the first stop will be place. 
        pct_trail (optional float between 0 and 1):
            - For any existing position the price of the stop 
              will be trailed by this percentage.
        """
        additionals = set(params.keys()).difference(set(self.params.keys()))
        if len(additionals)>1:
            log.warn('Got additional parameter, which will be ignored!')
            del params[additionals]
        self.params.update(params)
       
    def manage_orders(self, context, data):
        self._refresh_amounts(context)
                
        for sec in self.stops.index:
            cancel_order(self.stops['id'][sec])
            if self._np.isnan(self.stops['price'][sec]):
                stop = (1-self.params['pct_init'])*data.current(sec, 'close')
            else:
                o = self._np.sign(self.stops['amount'][sec])
                new_stop = (1-o*self.params['pct_trail'])*data.current(sec, 'close')
                stop = o*max(o*self.stops['price'][sec], o*new_stop)
                
            self.stops.loc[sec, 'price'] = stop           
            self.stops.loc[sec, 'id'] = order(sec, -self.stops['amount'][sec], style=StopOrder(stop))
 
    def __init__(self, **params):
        self._import()
        self.params = {'pct_init': 0.01, 'pct_trail': 0.03}
        self.stops = self._pd.DataFrame(columns=['amount', 'price', 'id'])        
        self.set_params(**params)        
    
    def _refresh_amounts(self, context):
        # Reset position amounts
        self.stops.loc[:, 'amount'] = 0.
        
        # Get open orders and remember amounts for any order with no defined stop.
        open_orders = get_open_orders()
        new_amounts = []
        for sec in open_orders:
            for order in open_orders[sec]:
                if order.stop is None:
                    new_amounts.append((sec, order.amount))                
            
        # Get amounts from portfolio positions.
        for sec in context.portfolio.positions:
            new_amounts.append((sec, context.portfolio.positions[sec].amount))
            
        # Sum amounts up.
        for (sec, amount) in new_amounts:
            if not sec in self.stops.index:
                self.stops.loc[sec, 'amount'] = amount
            else:
                self.stops.loc[sec, 'amount'] = +amount
            
        # Drop securities, with no position/order any more. 
        drop = self.stops['amount'] == 0.
        self.stops.drop(self.stops.index[drop], inplace=True)
        
    def _import(self):
        import numpy
        self._np = numpy
        import pandas
        self._pd = pandas
