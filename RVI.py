"""
Author: Ian Doherty
Date: April 13, 2017

This algorithm trades using RVI.

"""
import numpy as np
import pandas as pd
import math

# Stock or Tool Class
class Stock:
    def __init__(self, sid):
        self.sid = sid
        # Price history data period
        self.data_sample = 4
        self.price_history = list()
        self.weight = 0
        self.signal_line = list()
        self.should_trade = False
        self.rvi = RVI()
        pass

    def get_price_history(self, data): # Gets OHLC for given stock for given data period.
        self.price_history = data.history(self.sid, ['open', 'high', 'low', 'close'], self.data_sample, '1m')
        pass
    pass

    # Print out Stock info
    def print_stock(self):
        #print ('SID: ' + str(self.sid))
        #print ('Price History: ' + str(self.price_history))
        #print ('Numerators: ' + str(self.rvi.numerators))
        #print ('Denominators: ' + str(self.rvi.denominators))
        #print ('Weight: ' + str(self.weight))
        #print ('RVIS: ' + str(self.rvi.rvis))
        #print ('Signal Line: ' + str(self.rvi.signal_line))
        #print ('Tradable: ' + str(self.should_trade))
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
    def get_ohlc_difference(self, price_history, ohlc_type1, ohlc_type2):
        # Perform denominator variables and assign correspong local a, b, c, and d
        for i in range(4):
            if (i == 0):
                a = (price_history[3:][ohlc_type1] - price_history[3:][ohlc_type2])
            if (i == 1):
                b = (price_history[2:-1][ohlc_type1] - price_history[2:-1][ohlc_type2])
            if (i == 2):
                c = (price_history[1:-2][ohlc_type1] - price_history[1:-2][ohlc_type2])
            if (i == 3):
                d = (price_history[:-3][ohlc_type1] - price_history[:-3][ohlc_type2])
        # Formula = ( a + (2 * b) + (2 * c) + d ) / 6
        differences = ((float(a)+(2*float(b))+(2*float(c))+float(d))/6)
        differences = check_data(differences)
        return differences

    def get_factors(self, stock, ohlc_type1, ohlc_type2):
        return self.get_ohlc_difference(stock.price_history, ohlc_type1, ohlc_type2)

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

    # Get Signal Line for RVI
    # (RVI + (2 * i) + (2 * j) + k) / 6
    def get_rvi_signal_line(self):
        if (len(self.signal_line) == 1):
            self.signal_line.pop(0)
        a = self.rvis[3:][0]
        b = self.rvis[2:3][0]
        c = self.rvis[1:2][0]
        d = self.rvis[:1][0]
        self.signal_line.append(check_data(float(a)+(2*float(b))+(2*float(c))+float(d))/6)
    pass

def initialize(context):
    """
    Called once at the start of the algorithm.
    """

    # Close Trading in last 30 minutes
    schedule_function(stop_trading, date_rules.every_day(), time_rules.market_close(minutes=15))

    # Create TVIX
    tvix = Stock(sid(40515))

    # Create XIV
    vix = Stock(sid(40516))

    # Enough data
    context.enough_data = 4

    # Security list
    context.securities = [tvix, vix]

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

def my_assign_weights(stock):
    """
    Assign weights to securities that we want to order.
    """
    # Get RVI indicator
    rvi = stock.rvi.rvis[3:][0]
    signal_line = stock.rvi.signal_line[0]

    # If signal line is bearish
    if (signal_line > rvi):
        stock.weight = 1
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

def my_record_vars(context, rvi, signal_line):
    """
    Plot variables at the end of each day.
    """
    record(RVI = rvi, Signal = signal_line, positions = (context.portfolio.positions_value/context.portfolio.starting_cash))
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
            stock.rvi.numerators.append(stock.rvi.get_factors(stock, 'close', 'open'))
            stock.rvi.denominators.append(stock.rvi.get_factors(stock, 'high', 'low'))
            stock.rvi.rvis.append(check_data(stock.rvi.update_rvi_variables(stock)))
            if ((len(stock.rvi.rvis) > 3)): # If there is enough data for Signal Line Calculation
                stock.rvi.get_rvi_signal_line()
                my_assign_weights(stock)
                my_rebalance(context, stock, data)
                stock.rvi.rvis.pop(0)
            else:
                pass
            stock.print_stock()
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
        stock.should_trade = False
    pass
