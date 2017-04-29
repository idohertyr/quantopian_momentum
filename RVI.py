"""
Author: Ian Doherty
Date: April 13, 2017

This algorithm trades using RVI.

"""
import numpy as np
import pandas as pd
import math
import talib

# Instrument Class
class Stock:
    # Creates default Stock
    def __init__(self, sid):
        self.sid = sid
        self.minute_sample = 4
        self.minute_history = list()
        self.weight = 0
        self.signal_line = list()
        self.should_trade = False
        self.rvi = RVI()
        self.rsi = RSI(self.sid, '1m', 20)
        pass

    # Gets OHLC data from the given data period
    def get_price_history(self, data):
        self.minute_history = data.history(self.sid, ['open', 'high', 'low', 'close'], self.minute_sample, '1m')
        pass

    # Stops trading instrument
    def stop_trading(self):
        self.should_trade = False
        pass

    # Print out Stock info
    def print_stock(self):
        #print ('SID: ' + str(self.sid))
        #print ('Price History: ' + str(self.minute_history))
        #print ('Numerators: ' + str(self.rvi.numerators))
        #print ('Denominators: ' + str(self.rvi.denominators))
        #print ('Weight: ' + str(self.weight))
        #print ('RVIS: ' + str(self.rvi.rvis))
        #print ('Signal Line: ' + str(self.rvi.signal_line))
        #print ('Tradable: ' + str(self.should_trade))
        #print ('RSI price history: ' + str(self.rsi.price_history))
        print ('RSI: ' + str(self.rsi.rsi))
        pass

# RSI Class
class RSI:
    # Create a new RSI
    def __init__(self, sid, unit, sample):
        self.sid = sid
        self.price_history = list()
        self.unit = unit
        self.sample = sample
        self.rsi = list()
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
        pass
    pass

# RVI Class
class RVI:
    def __init__(self):
        # Period Counter
        self.period = 0
        # RVI Select Period
        self.select_period = 19
        # RVI numerators
        self.numerators = list()
        # RVI denominators
        self.denominators = list()
        # RVI History
        self.rvis = list()
        # Signal line
        self.signal_line = list()

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
        return self.get_ohlc_difference(stock.minute_history, ohlc_type1, ohlc_type2)
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
        pass

    pass

def initialize(context):
    """
    Called once at the start of the algorithm.
    """

    # Close Trading in last 30 minutes
    schedule_function(stop_trading, date_rules.every_day(), time_rules.market_close(minutes=15))

    # Record variables
    schedule_function(my_record_vars, date_rules.every_day(), time_rules.market_close())

    # Create TVIX
    tvix = Stock(sid(40515))

    # Create XIV
    vix = Stock(sid(40516))

    # Enough data
    context.enough_data = 4

    # Security list
    context.securities = [tvix, vix]

    set_benchmark(context.securities[0].sid)
    set_benchmark(context.securities[0].sid)

    # Minute timer for when to execute updates
    context.count = 0

    pass

def before_trading_start(context, data):
    """
    Called every day before market open.
    """
    for stock in context.securities:
        stock.should_trade = True
    pass

def my_assign_weights(context, stock):
    """
    Assign weights to securities that we want to order.
    """
    # Get RVI indicator
    rvi = stock.rvi.rvis[3:][0]
    signal_line = stock.rvi.signal_line[0]
    rsi = stock.rsi.rsi
    default_weight = (float(1)/float(len(context.securities)))

    # If signal line is bearish
    if ((signal_line > rvi)):
        stock.print_stock()
        stock.weight = default_weight
        #print ('bullish')
    else:
        stock.weight = 0
        #print ('bearish')
    pass

def my_rebalance(context, stock, data):
    """
    Execute orders according to our schedule_function() timing. 
    """
    if ((data.can_trade(stock.sid)) &
            (len(get_open_orders(stock.sid)) == 0) &
            (stock.should_trade) &
            (context.portfolio.cash > 0)):
        order_target_percent(stock.sid, stock.weight)
    pass

def my_record_vars(context, data):
    """
    Plot variables at the end of each day.
    """
    record(TVIX = data.current(context.securities[0].sid, 'price'),
           XIV = data.current(context.securities[1].sid, 'price'))
    pass

def handle_data(context, data):
    """
    Called every minute.
    """
    # Minute timer - every 4 mins
    context.count += 1
    if(context.count == context.enough_data):
        context.count = 0 # reset timer
        for stock in context.securities:
            stock.get_price_history(data)
            stock.rsi.get_rsi(data)
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
                #stock.print_stock()
    pass

#TODO: Need to clean data.
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
