"""
Author: Ian Doherty
Date: April 13, 2017

This algorithm is made to evaluate momentum and to produce a trading strategy based on
Momentum. This algorithm serves as an area to test momentum strategies separate from
any real trading strategy.

Momentum Tools:
Relative Vigor Index


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
    high = 0.25
    low = -0.25
    rvi = context.rvi[-1]
    stock = context.stock

    if (pd.isnull(rvi) == False):
        if ((rvi > high) & (data.can_trade(stock))):
            order_target_percent(stock, 0)
        if ((rvi < low) & (data.can_trade(stock))):
            order_target_percent(stock, 1)

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
    context.count += 1
    if (context.count == 5): # Reset count and update data
        context.count = 0
        context.data = update_data(context, data)
        context.rvi = get_rvi(context)
        my_rebalance(context, data)
    pass

def update_data(context, data): # Gets OHLC for given stock
    stock = context.stock
    data = data.history(stock, ['open', 'high', 'low', 'close'], 1, '1m')
    return data

def get_rvi(context):
    return((context.data['close']-context.data['open'])/(context.data['high']-context.data['low']))