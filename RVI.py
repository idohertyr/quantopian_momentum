"""
Author: Ian Doherty
Date: April 13, 2017

This algorithm trades using RVI.

"""

import numpy as np
import pandas as pd
import math

def initialize(context):
    """
    Called once at the start of the algorithm.
    """

    # Close Trading in last 30 minutes
    schedule_function(stop_trading, date_rules.every_day(), time_rules.market_close(hours=1))

    class Stock:
        def __init__(self, sid):
            self.sid = sid
            self.price_history = list()
            self.numerators = list()
            self.denominators = list()
            self.weight = 0
            # Define RVI Relative Vigor Index
            self.rvis = list()
            self.signal_line = list()
            pass
        pass

    # Create TVIX
    tvix = Stock(sid(40515))

    # Create XIV
    vix = Stock(sid(40516))

    # Define current period
    context.period = 0

    # Define price history data period
    context.data_period = 4

    # Define select period
    context.select_period = 19

    context.securities = [tvix, vix]

    # Minute timer for when to execute updates
    context.count = 0

    # Define trade boolean
    context.should_trade = False

    pass

def before_trading_start(context, data):
    """
    Called every day before market open.
    """
    context.should_trade = True

def my_assign_weights(stock):
    """
    Assign weights to securities that we want to order.
    """
    # Get RVI indicator
    rvi = stock.rvis[3:][0]
    signal_line = stock.signal_line[0]

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
        (context.should_trade) &
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
    if(context.count == context.data_period):
        context.count = 0 # reset timer
        for stock in context.securities:
            stock.price_history = update_price_history(context, stock.sid, data) # Gets OHLC
            stock.numerators = get_numerator(stock)
            stock.denominators = get_denominator(stock)
            stock = update_rvi_variables(context, stock) # Calculates RVI
        if ((len(stock.rvis) > 3)): # If there is enough data for Signal Line Calculation
            stock = get_rvi_signal_line(context, stock)
            my_assign_weights(stock)
            my_rebalance(context, stock, data)
            stock.rvis.pop(0)
    else:
        pass
    pass

def update_price_history(context, stock, data): # Gets OHLC for given stock, last 4
    history = data.history(stock, ['open', 'high', 'low', 'close'], context.data_period, '1m')
    return history

def get_numerator(stock):
    # Calculate RVI numerator
    numerator = get_ohlc_difference(stock.sid, stock.price_history, 'close', 'open')
    # Append to self numerators
    stock.numerators.append(numerator)
    # Return stock numerators
    return stock.numerators

def get_denominator(stock):
    # Calculate RVI denominator
    denominator = get_ohlc_difference(stock.sid, stock.price_history, 'high', 'low')
    # Append to self denominators
    stock.denominators.append(denominator)
    # Return stock denominators
    return stock.denominators

# Performs Numerator and Denominator calculations for RVI
def update_rvi_variables(context, stock):
    context.period += 1
    # Check if there is enough select_period - get SMAs
    if (context.period == context.select_period):
        # Moving average for select_period
        num_sma = np.average(stock.numerators)
        den_sma = np.average(stock.denominators)

        # Remove oldest
        stock.numerators.pop(0)
        stock.denominators.pop(0)

        context.period -= 1

        # Update RVI list for Signal line
        stock.rvis.append(num_sma/den_sma)
    return stock

# Returns OHLC difference - Numerator and Denominator for RVI Calculation
def get_ohlc_difference(stock, price_history, col1, col2):
    # Perform denominator variables and assign correspong local a, b, c, and d
    for i in range(4):
        if (i == 0):
            a = (price_history[3:][col1] - price_history[3:][col2])
        if (i == 1):
            b = (price_history[2:-1][col1] - price_history[2:-1][col2])
        if (i == 2):
            c = (price_history[1:-2][col1] - price_history[1:-2][col2])
        if (i == 3):
            d = (price_history[:-3][col1] - price_history[:-3][col2])
    # Formula = ( a + (2 * b) + (2 * c) + d ) / 6
    differences = ((float(a)+(2*float(b))+(2*float(c))+float(d))/6)
    differences = check_data(differences)
    return differences

# Get Signal Line for RVI
# (RVI + (2 * i) + (2 * j) + k) / 6
def get_rvi_signal_line(context, stock):
    if (len(stock.signal_line) == 1):
        stock.signal_line.pop(0)
    a = stock.rvis[3:][0]
    b = stock.rvis[2:3][0]
    c = stock.rvis[1:2][0]
    d = stock.rvis[:1][0]
    stock.signal_line.append((float(a)+(2*float(b))+(2*float(c))+float(d))/6)
    return stock
# Checks data for Nan
def check_data(data):
    if (type(data) == float):
        if ((math.isnan(data)) | (data == None)):
            return 0
        else:
            return data
    elif (type(data) == list):
        # replaces Nan values from list
        data = [0 if x != x else x for x in data]
        return data
    pass
# Stop trading 30 minutes for market close
def stop_trading(context, data):
    context.should_trade = False
    pass