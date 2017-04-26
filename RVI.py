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
    # Rebalance every day, 1 hour after market open.
    # schedule_function(my_rebalance, date_rules.every_day(), time_rules.market_open())

    # Record tracking variables at the end of each day.
    # schedule_function(my_record_vars, date_rules.every_day(), time_rules.market_close())

    # Close Trading in last 30 minutes
    schedule_function(stop_trading, date_rules.every_day(), time_rules.market_close(minutes=30))

    # Define stock
    context.stock = sid(41968)

    # Minute timer for when to execute updates
    context.count = 0

    # Define RVI Relative Vigor Index
    context.rvis = list()

    # Define RVI Signal Line
    context.signal_line = list()

    # Selected RVI period
    context.periods = 0
    context.select_period = 20

    # Numerator
    context.numerators = list()

    # Denominator
    context.denominators = list()

    # Define weight
    context.weight = 0

    # Define trade boolean
    context.should_trade = False

    pass


def before_trading_start(context, data):
    """
    Called every day before market open.
    """
    context.should_trade = True


def my_assign_weights(context, data):
    """
    Assign weights to securities that we want to order.
    """
    # Get RVI indicator
    rvi = context.rvis[3:][0]
    signal_line = context.signal_line[0]

    # my_record_vars(context, rvi, signal_line)
    # log.info ('Current Price: ' + str(data.current(context.stock, 'price')))
    # log.info ('RVI: ' + str(rvi) + ' Signal Line: ' + str(signal_line))

    # If signal line is bearish
    if (signal_line > rvi):
        context.weight = 1
        # print ('bullish')
    else:
        context.weight = 0
        # print ('bearish')
    pass


def my_rebalance(context, data):
    """
    Execute orders according to our schedule_function() timing. 
    """
    stock = context.stock
    weight = context.weight

    if ((data.can_trade(stock)) & (len(get_open_orders()) == 0) & (context.should_trade)):
        # if bullish buy stock
        if (weight == 1):
            order_target_percent(stock, 1)
        else:
            order_target_value(stock, 0)
    pass


def my_record_vars(context, rvi, signal_line):
    """
    Plot variables at the end of each day.
    """
    record(RVI=rvi, Signal=signal_line, positions=(context.portfolio.positions_value / context.portfolio.starting_cash))
    pass


def handle_data(context, data):
    """
    Called every minute.
    """
    # Minute timer - every 4 mins
    context.count += 1
    if (context.count == 4):
        context.count = 0  # reset timer
        price_history = update_data(context.stock, data)  # Gets last four minutes of OHLC
        update_rvi_variables(context, context.stock, price_history)  # Calculates RVI
    else:
        pass

    # If there is enough data for Signal Line Calculation
    if (len(context.rvis) > 3):
        get_rvi_signal_line(context, context.rvis)
        my_assign_weights(context, data)
        my_rebalance(context, data)
        context.rvis.pop(0)

    pass


def update_data(stock, data):  # Gets OHLC for given stock, last 4 m
    history = data.history(stock, ['open', 'high', 'low', 'close'], 4, '1m')
    return history


# Performs Numerator and Denominator calculations for RVI, then adds
# them to a list size defined in initialize() (context.select_period)
def update_rvi_variables(context, stock, price_history):
    # Calculate RVI numerator
    numerator = get_ohlc_difference(stock, price_history, 'close', 'open')
    # print ('numerator ---' + str(numerator))

    # Calculate RVI denominator
    denominator = get_ohlc_difference(stock, price_history, 'high', 'low')
    # print ('denominator ---' + str(denominator))

    # Add Numerator and Denominator to their respective lists
    context.denominators.append(denominator)
    context.numerators.append(numerator)

    context.periods += 1

    # Check if there is enough select_period - get SMAs
    if (context.periods == context.select_period):
        # Moving average for select_period
        num_sma = np.average(context.numerators)
        den_sma = np.average(context.denominators)

        # Remove oldest
        context.numerators.pop(0)
        context.denominators.pop(0)

        context.periods -= 1

        # Update RVI list for Signal line
        context.rvis.append(num_sma / den_sma)

    pass


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
    differences = ((float(a) + (2 * float(b)) + (2 * float(c)) + float(d)) / 6)
    differences = check_data(differences)
    return differences


# Get Signal Line for RVI
# (RVI + (2 * i) + (2 * j) + k) / 6
def get_rvi_signal_line(context, rvis):
    if (len(context.signal_line) == 1):
        context.signal_line.pop(0)
    a = rvis[3:][0]
    b = rvis[2:3][0]
    c = rvis[1:2][0]
    d = rvis[:1][0]
    context.signal_line.append((float(a) + (2 * float(b)) + (2 * float(c)) + float(d)) / 6)
    pass


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