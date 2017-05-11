"""
Author: Ian Doherty
Date: April 13, 2017

"""
import numpy as np
import pandas as pd
import math
import talib
import datetime

# Instrument Class
class Stock:
    # Creates default Stock
    def __init__(self, sid):
        self.sid = sid
        self.weight = 0
        self.signal_line = list()
        self.should_trade = False
        self.sentiment = list()
        self.rvi = Rvi(self.sid, '1m', 4, 19)
        self.rsi = Rsi(self.sid, '1m', 20)
        self.bbands = BBands(self.sid, '1m', 20)
        self.cci = Cci(self.sid, '1m', 20)
        self.sentiment_types = ['buy', 'hold', 'sell']
        pass

    # Stops trading instrument
    def stop_trading(self):
        self.should_trade = False
        pass

    # Print out Stock info
    def print_stock(self):
        # Get the current exchange time in EST timezone:
        exchange_time = pd.Timestamp(get_datetime()).tz_convert('US/Eastern')
        print ('CURRENT TIME: ' + str(exchange_time))
        #print ('SID: ' + str(self.sid))
        #print ('Price History: ' + str(self.minute_history))
        #print ('Numerators: ' + str(self.rvi.numerators))
        #print ('Denominators: ' + str(self.rvi.denominators))
        #print ('Weight: ' + str(self.weight))
        #print ('RVIS: ' + str(self.rvi.rvis))
        #print ('Signal Line: ' + str(self.rvi.signal_line))
        #print ('Tradable: ' + str(self.should_trade))
        print ('RSI price history: ' + str(self.rsi.price_history[-1]))
        print ('RSI: ' + str(self.rsi.rsi[-1]))
        #print ('BBANDS price history: ' + str(self.bbands.price_history[-1]))
        #print ('BBANDS' + str(self.bbands.bbands))
        #if (len(self.rvi.sentiment) > 0):
        #print ('RVI sentiment: ' + str(self.rvi.sentiment[-1]))
        print ('RSI sentiment: ' + str(self.rsi.sentiment))
        #print ('BBands sentiment: ' + str(self.bbands.sentiment))
        print ('Stock sentiment: ' + str(self.sentiment))
        pass

    # Get sentiment
    def get_sentiment(self):
        types = self.sentiment_types

        if (len(self.rvi.sentiment) > 0):
            rvi_sentiment = self.rvi.sentiment[-1]
        else:
            rvi_sentiment = 'hold'

        rsi_sentiment = self.rsi.sentiment[-1]
        bbands_sentiment = self.bbands.sentiment[-1]
        cci_sentiment = self.cci.sentiment[-1]

        if (len(self.sentiment) > 10):
            self.sentiment.pop(0)

        if  (
                            (rvi_sentiment == types[0]) &
                            (rsi_sentiment == types[0]) &
                        (cci_sentiment == types[0]) &
                    (bbands_sentiment == types[0])
        ):
            self.sentiment.append(types[0])
        elif (
                            (rvi_sentiment == types[2]) &
                            (rsi_sentiment == types[2]) &
                        (cci_sentiment == types[2]) &
                    (bbands_sentiment == types[2])
        ):
            self.sentiment.append(types[2])
        else:
            self.sentiment.append(types[1])
        pass

# RSI Class
class Rsi:
    # Create a new RSI
    def __init__(self, sid, unit, sample):
        self.sid = sid
        self.price_history = list()
        self.unit = unit
        self.sample = sample
        self.rsi = list()
        self.sentiment = list()
        self.sentiment_types = ['buy', 'hold', 'sell']
        pass

    # Get Price history based on initialiation variables
    def get_price_history(self, data):
        self.price_history = data.history(self.sid, 'close', self.sample + 2, self.unit)
        pass

    # Calculate RSI
    def get_rsi(self, data):
        self.get_price_history(data)
        self.rsi.append(talib.RSI(self.price_history)[-1])
        if(len(self.rsi) == 2):
            self.rsi.pop(0)
        self.get_sentiment()
        pass

    # Get sentiment
    def get_sentiment(self):
        types = self.sentiment_types
        rsi = self.rsi[-1]

        if (len(self.sentiment) > 10):
            self.sentiment.pop(0)

        if (rsi < 25):
            self.sentiment.append(types[0])
        elif (rsi > 65):
            self.sentiment.append(types[2])
        else:
            self.sentiment.append(types[1])
        pass
    pass



# RVI Class
class Rvi:
    def __init__(self, sid, unit, sample, select_period):
        # SID
        self.sid = sid
        # Price history candle type
        self.unit = unit
        # Sample
        self.sample = sample
        # Price History
        self.prce_history = list()
        # Period Counter
        self.period = 0
        # RVI Select Period
        self.select_period = select_period
        # RVI numerators
        self.numerators = list()
        # RVI denominators
        self.denominators = list()
        # RVI History
        self.rvis = list()
        # Signal line
        self.signal_line = list()
        # Self Sentiment
        self.sentiment = list()
        self.sentiment_types = ['buy', 'hold', 'sell']
        pass

    # Get price history
    def get_price_history(self, data):
        self.price_history = data.history(self.sid, ['open', 'high', 'low', 'close'], self.sample, self.unit)
        pass

    # Returns OHLC difference - Numerator and Denominator for RVI Calculation
    def get_ohlc_difference(self, minute_history, ohlc_type1, ohlc_type2):
        # Perform denominator variables and assign correspong local a, b, c, and d
        for i in range(4):
            if (i == 0):
                a = (minute_history[3:][ohlc_type1] - minute_history[3:][ohlc_type2])
            if (i == 1):
                b = (minute_history[2:-1][ohlc_type1] - minute_history[2:-1][ohlc_type2])
            if (i == 2):
                c = (minute_history[1:-2][ohlc_type1] - minute_history[1:-2][ohlc_type2])
            if (i == 3):
                d = (minute_history[:-3][ohlc_type1] - minute_history[:-3][ohlc_type2])
        # Formula = ( a + (2 * b) + (2 * c) + d ) / 6
        differences = ((float(a)+(2*float(b))+(2*float(c))+float(d))/6)
        differences = check_data(differences)
        return differences

    def get_factors(self, stock, ohlc_type1, ohlc_type2):
        return self.get_ohlc_difference(stock.rvi.price_history, ohlc_type1, ohlc_type2)
        pass

    # Performs Numerator and Denominator calculations for RVI
    def update_rvi_variables(self, stock):
        stock.rvi.period += 1
        # Check if there is enough select_period - get SMAs
        if (stock.rvi.period == stock.rvi.select_period):
            # Moving average for select_period
            num_sma = np.average(stock.rvi.numerators)
            den_sma = np.average(stock.rvi.denominators)

            # Remove oldest
            stock.rvi.numerators.pop(0)
            stock.rvi.denominators.pop(0)

            stock.rvi.period -= 1

            # Return RVI
            return(num_sma/den_sma)
        else:
            return float()
        pass


    # Get Signal Line for RVI
    def get_rvi_signal_line(self):
        if (len(self.signal_line) == 1):
            self.signal_line.pop(0)
        a = self.rvis[3:][0]
        b = self.rvis[2:3][0]
        c = self.rvis[1:2][0]
        d = self.rvis[:1][0]
        self.signal_line.append(check_data(float(a)+(2*float(b))+(2*float(c))+float(d))/6)
        self.get_sentiment()
        pass

    # Get sentiment
    def get_sentiment(self):
        types = self.sentiment_types
        rvi = self.rvis[3:][0]
        signal_line = self.signal_line[0]

        if (len(self.sentiment) > 20):
            self.sentiment.pop(0)

        if ((signal_line > rvi) & (rvi < 0)):
            self.sentiment.append(types[0])
            #log.info('RVI bull ' + str(signal_line) + str(rvi))
        elif ((signal_line < rvi) & (rvi > 0)):
            self.sentiment.append(types[2])
            #log.info('RVI bear ' + str(signal_line) + str(rvi))
        else:
            self.sentiment.append(types[1])

    pass

# Bollinger Band Class
class BBands:
    def __init__(self, sid, unit, sample):
        # SID
        self.sid = sid
        # Price history
        self.price_history = list()
        # Price history unit
        self.unit = unit
        # Price history sample size
        self.sample = sample
        # Bollinger Bands
        self.bbands = list()
        # Sentiment
        self.sentiment = list()
        self.sentiment_types = ['buy', 'hold', 'sell']
        pass

    def get_price_history(self, data):
        self.price_history = data.history(self.sid, 'close', self.sample + 2, self.unit)
        pass

    def get_bbands(self, data):
        self.get_price_history(data)
        upper, middle, lower = talib.BBANDS(
            self.price_history,
            timeperiod = self.sample,
            nbdevup = 2,
            nbdevdn = 2,
            matype = 0)
        self.bbands = [upper[-1], middle[-1], lower[-1]]
        self.get_sentiment()
        pass

    # Get sentiment
    def get_sentiment(self):
        types = self.sentiment_types
        upper = self.bbands[0]
        middle = self.bbands[1]
        lower = self.bbands[2]
        price = self.price_history[-1]

        if (len(self.sentiment) > 10):
            self.sentiment.pop(0)

        if (price < lower):
            self.sentiment.append(types[0])
        elif (price > upper):
            self.sentiment.append(types[2])
        else:
            self.sentiment.append(types[1])
        pass
    pass

# CCI Class
class Cci:
    def __init__(self, sid, unit, sample):
        self.sid = sid
        self.unit = unit
        self.sample = sample
        self.highs = list()
        self.lows = list()
        self.closes = list()
        self.ccis = list()
        self.sentiment = list()
        self.sentiment_types = ['buy', 'hold', 'sell']
        pass

    def get_price_history(self, data):
        self.closes = data.history(self.sid, 'close', self.sample + 2, self.unit)
        self.highs = data.history(self.sid, 'high', self.sample + 2, self.unit)
        self.lows = data.history(self.sid, 'low', self.sample + 2, self.unit)
        pass

    def get_cci(self, data):
        if(len(self.ccis) == 10):
            self.ccis.pop(0)

        self.get_price_history(data)
        cci = talib.CCI(self.highs.values, self.lows.values, self.closes.values, self.sample)[-1]
        self.ccis.append(cci)
        self.get_sentiment()

    def get_sentiment(self):
        types = self.sentiment_types
        cci = self.ccis[-1]

        if(len(self.sentiment) > 10):
            self.sentiment.pop(0)

        if (cci < -200):
            self.sentiment.append(types[0])
        elif (cci > 200):
            self.sentiment.append(types[2])
        else:
            self.sentiment.append(types[1])

        pass
    pass

def initialize(context):
    """
    Called once at the start of the algorithm.
    """

    # Close Trading in last 15 minutes
    schedule_function(stop_trading, date_rules.every_day(), time_rules.market_close(minutes=15))

    # Record variables
    schedule_function(my_record_vars, date_rules.every_day(), time_rules.market_close())

    # Create TVIX
    tvix = Stock(sid(40515))

    # Create XIV
    xiv = Stock(sid(40516))

    # Enough data
    context.enough_data = 4

    # Security list
    context.securities = [tvix, xiv]

    set_benchmark(context.securities[0].sid)

    # Minute timer for when to execute updates
    context.count = 0

    # Prevents any short positions from being opened
    set_long_only()

    # Limits the absolute magnitude of any position held by the algorithm
    #set_max_position_size(context.securities[0].sid, max_notional=50000)
    #set_max_position_size(context.securities[1].sid, max_notional=50000)

    # Set commission price
    set_commission(commission.PerTrade(cost=0.00))

    # Trade up to 50% of stock volume in a bar
    #set_slippage(slippage.FixedSlippage(spread=0.5))

    pass

def start_trading(context, data):
    print ('-----------START TRADING -----------')
    for stock in context.securities:
        stock.should_trade = True
    pass

def before_trading_start(context, data):
    """
    Called every day before market open.
    """
    start_trading(context, data)
    pass

def my_assign_weights(context, stock):
    """
    Assign weights to securities that we want to order.
    """
    types = stock.sentiment_types

    # Get indicator sentiments
    stock.get_sentiment()
    sentiment = stock.sentiment[-1]

    default_weight = (float(1)/float(len(context.securities)))

    # If signal line is bearish
    if ((sentiment == types[0]) &
            stock.should_trade):
        stock.weight = default_weight
        log.info ('BUYING+++++++++++++++++++++++++++++++++++++++ ' + str(stock.sid))
        #stock.print_stock()
    elif ((sentiment == types[2]) &
              stock.should_trade):
        stock.weight = 0
        log.info ('SELLING--------------------------------------- ' + str(stock.sid))
        #stock.print_stock()
    else:
        pass
        #print ('holding')
    pass

def my_rebalance(context, stock, data):
    """
    Execute orders according to our schedule_function() timing. 
    """
    if ((data.can_trade(stock.sid)) &
            (stock.should_trade) &
            (len(get_open_orders(stock.sid)) == 0)):
        order_target_percent(stock.sid, stock.weight)
    pass

def my_record_vars(context, data):
    """
    Plot variables at the end of each day.
    """
    record(
        TVIX = context.portfolio.positions[context.securities[0].sid].amount,
        XIV = context.portfolio.positions[context.securities[1].sid].amount
    )
    pass

def handle_data(context, data):
    """
    Called every minute.
    """
    # Minute timer - every 4 mins
    context.count += 1

    for stock in context.securities:
        stock.rsi.get_rsi(data)
        stock.bbands.get_bbands(data)
        stock.cci.get_cci(data)
        if(context.count == context.enough_data):
            context.count = 0 # reset timer
            stock.rvi.get_price_history(data)
            stock.rvi.numerators.append(stock.rvi.get_factors(stock, 'close', 'open'))
            stock.rvi.denominators.append(stock.rvi.get_factors(stock, 'high', 'low'))
            stock.rvi.rvis.append(check_data(stock.rvi.update_rvi_variables(stock)))
            if ((len(stock.rvi.rvis) > 3)): # If there is enough data for Signal Line Calculation
                stock.rvi.get_rvi_signal_line()
                my_assign_weights(context, stock)
                my_rebalance(context, stock, data)
                stock.rvi.rvis.pop(0)
            else:
                pass
        my_assign_weights(context, stock)
        my_rebalance(context, stock, data)
    pass

# TODO: Need to check for Nan, None..
def check_data(data):
    new = list()
    if (type(data) == list): # replaces Nan values from list
        for item in data:
            if (item):
                new.append(item)
        return new
    elif data is not None:
        return data
    else:
        return float()


def stop_trading(context, data):
    for stock in context.securities:
        stock.stop_trading()
    pass
