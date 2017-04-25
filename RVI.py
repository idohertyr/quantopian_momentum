"""
Author: Ian Doherty
Date: April 13, 2017

This algorithm is made to evaluate momentum and to produce a trading strategy based on
Momentum. This algorithm serves as an area to test momentum strategies separate from
any real trading strategy.

Momentum Tools: [RVI, ]

Relative Vigor Index
=====================
INPUTS: 
    OHLC prices

RVI
===========
a = close - open
b = close - open // one bar prior to a
c = close - open // one bar prior to b
d = close - open // one bar prior to c

numerator = ( a + (2 * b) + (2 * g) + h) / 6

e = high - low // of bar a
f = high - low // of bar b
g = high - low // of bar c
h = high - low // of bar d

denominator = ( e + (2 * f) + (2 * g) + h) / 6

Current period selected = 20

RVI = SMA of numerator for selected period /
        SMA of denominator for selected period
        
SIGNAL_LINE
===========
i = RVI // one bar prior
j = RVI // one bar prior to i
k = RVI // one bar prior to j

SIGNAL_LINE = (RVI + (2 * i) + (2 * j) + k) / 6


"""

import numpy as np
import talib
import pandas as pd

def initialize(context):
    """
    Called once at the start of the algorithm.
    """
    # Rebalance every day, 1 hour after market open.
    #schedule_function(my_rebalance, date_rules.every_day(), time_rules.market_open())

    # Record tracking variables at the end of each day.
    schedule_function(my_record_vars, date_rules.every_day(), time_rules.market_close())

    # Define stock
    context.stock = sid(41968)

    # Update data every 5 seconds.
    context.count = 0

    # Define data structure
    context.data = []

    # Define RVI Relative Vigor Index
    context.rvi = 0

def before_trading_start(context, data):
    """
    Called every day before market open.
    """

def my_assign_weights(context, data):
    """
    Assign weights to securities that we want to order.
    """
    pass

def my_rebalance(context, data):
    """
    Execute orders according to our schedule_function() timing. 
    """
    pass

def my_record_vars(context, data):
    """
    Plot variables at the end of each day.
    """
    pass

def handle_data(context, data):
    """
    Called every minute.
    """
    pass

def update_data(context, data, stock): # Gets OHLC for given stock
    data = data.history(stock, ['open', 'high', 'low', 'close'], 1, '1m')
    return data

def get_rvi(context):
    pass