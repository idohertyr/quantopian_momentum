"""
Author: Ian Doherty
Date: April 13, 2017
"""

def initialize(context):
    """
    Called once at the start of the algorithm.
    """
    # Rebalance every day, 1 hour after market open.
    schedule_function(my_rebalance, date_rules.every_day(), time_rules.market_open())

    # Record tracking variables at the end of each day.
    schedule_function(my_record_vars, date_rules.every_day(), time_rules.market_close())

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

def get_ohlc(stock, data): # Gets OHLC for given stock
    data = data.history(stock, ['open', 'high', 'low', 'close'], 1, '1m')
    return data