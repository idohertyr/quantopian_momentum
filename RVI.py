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

numerator = ( a + (2 * b) + (2 * c) + d ) / 6

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
import math

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
    context.data = {}

    # Define RVI Relative Vigor Index
    context.rvi = 0

    # Numerator
    context.numerator = 0

    # Denominator
    context.denominator = 0
    pass

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
    # Perform operations every 4 mins
    context.count += 1
    if(context.count == 4):
        #print context.data
        context.count = 0
        update_context(context)

    else:
        context.data[context.stock] = update_data(context, data, context.stock)
    pass

def update_data(context, data, stock): # Gets OHLC for given stock
    data = data.history(stock, ['open', 'high', 'low', 'close'], 4, '1m')
    return data

def update_context(context):
    # Perform RVI calculation

    # Calculate RVI numerator
    context.numerator = get_rvi_numerator(context)
    print ('numerator ---' + str(context.numerator))

    # Calculate RVI denominator
    context.denominator = get_rvi_denominator(context)
    print ('denominator ---' + str(context.denominator))
    pass

def get_rvi(context):
    pass

# Returns numerator for RVI calculation
def get_rvi_numerator(context):
    # Perform numerator variables and assign corresponding local a, b, c, and d.
    for i in range(4):
        if (i == 0):
            a = (context.data[context.stock][3:]['close'] - context.data[context.stock][3:]['open'])
        if (i == 1):
            b = (context.data[context.stock][1:-2]['close'] - context.data[context.stock][1:-2]['open'])
        if (i == 2):
            c = (context.data[context.stock][2:-1]['close'] - context.data[context.stock][2:-1]['open'])
        if (i == 3):
            d = (context.data[context.stock][:-3]['close'] - context.data[context.stock][:-3]['open'])
    # Perform numerator calculation
    # numerator = ( a + (2 * b) + (2 * c) + d ) / 6
    numerator = ((float(a)+(2*float(b)) + (2*float(c)) + float(d))/6)
    numerator = check_data(numerator)
    return numerator

# Returns the denominator for RVI calculation
def get_rvi_denominator(context):
    # Perform denominator variables and assign correspong local e, f, g, and h
    for i in range(4):
        if (i == 0):
            e = (context.data[context.stock][3:]['high'] - context.data[context.stock][3:]['low'])
        if (i == 1):
            f = (context.data[context.stock][1:-2]['high'] - context.data[context.stock][1:-2]['low'])
        if (i == 2):
            g = (context.data[context.stock][2:-1]['high'] - context.data[context.stock][2:-1]['low'])
        if (i == 3):
            h = (context.data[context.stock][:-3]['high'] - context.data[context.stock][:-3]['low'])
    # Perform denominator calculation
    # denominator = ( e + (2 * f) + (2 * g) + h) / 6
    denominator = ((float(e)+(2*float(f))+(2*float(g))+float(h))/6)
    denominator = check_data(denominator)
    return denominator

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

