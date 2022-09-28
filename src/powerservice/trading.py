"""
Module that contains the get trades functionality. This module will generate a random set of dummy positions.
"""
import random
import logging
import datetime
import uuid

import numpy as np
import pandas as pd
import math


def check_if_valid_date(date: str):
    """
    Verify that the date format matches d/m/y
    :param date: str date in d/m/y format
    :return: True or False
    """
    date_format = "%d/%m/%Y"

    """ Warning to any non python devs reading this code..
        In Python the only way to test a valid date is with a try catch. Yep, it sux.
    """
    if not isinstance(date, str):
        return False

    try:
        datetime.datetime.strptime(date, date_format)
        valid_date = True
    except ValueError:
        valid_date = False

    return valid_date


def random_nan(x):
    """
    Replace x with a nan, if the random number == 1
    """
    if random.randrange(0, 15) == 1:
        x = np.nan

    return x


def generate_new_random_trade_position(date: str):
    """ Generates a new random trade position with the date, period sequence and volume sequence
    :param date: Date in d/m/y format
    :return: dict with data
    """

    period_list = [random_nan(i.strftime("%H:%M")) for i in pd.date_range("00:00", "23:59", freq="5min").time]
    volume = [random_nan(x) for x in random.sample(range(0, 500), len(period_list))]

    open_trade_position = {"date": date,
                           "time": period_list,
                           "volume": volume,
                           "id": uuid.uuid4().hex
                           }

    return open_trade_position


def get_trades(date: str):
    """
    Generate some random number of open trade positions
    :param date: date in d/m/y format
    :return:
    """

    if not check_if_valid_date(date=date):
        error_msg = "The supplied date {} is invalid.Please supply a date in the format d/m/Y.".format(date)
        logging.error(error_msg)
        raise ValueError(error_msg)

    # a randomly chosen number of open trades
    number_of_open_trades = random.randint(1, 101)
    logging.info("Generated" + str(number_of_open_trades) + " open trades randomly.")

    open_trades_list = []
    # Generate a list of open trade dicts
    for open_trade in range(0, number_of_open_trades):
        open_trades_list.append(generate_new_random_trade_position(date=date))

    return open_trades_list

def data_quality_check(df):
    
    df[['hour', 'minutes']] = df['time'].str.split(':', expand=True)

    # Derive quality check fields
    df['time_is_nan'] = pd.to_numeric(df['hour']).apply(lambda x: True if math.isnan(x) else False)
    df['date_is_valid'] = df['date'].apply(lambda x: check_if_valid_date(x))
    df['missing_vol_values'] = pd.to_numeric(df['volume']).apply(lambda x: True if math.isnan(x) else False)
    
    dq_dict = {'Time Interval Check': {
                # Check time values if NaN (Invalid) else Valid
                'Valid': len(df.loc[df['time_is_nan'] == False].index), 
                'Invalid': len(df.loc[df['time_is_nan'] ==True].index),
                'Total': len(df.index)
            },
           'Correct Time Format': {
                # Check date values
                'Valid': len(df.loc[df['date_is_valid'] == True].index), 
                'Invalid': len(df.loc[df['date_is_valid'] == False].index), 
                'Total': len(df.index)
            },
           'Missing Volume Values': {
                # Check volume if NaN (Invalid) else Valid
                'Valid': len(df.loc[df['missing_vol_values'] == False].index), 
                'Invalid': len(df.loc[df['missing_vol_values'] == True].index), 
                'Total': len(df.index)
            },
        }
    
    df = pd.DataFrame.from_dict(dq_dict)
            
    return df

def summarise_data(df):    
    
    """ Derive hours from local time, 
        subtract 1 to align with business day (23:00 to 22:00),
        Append :00 to get back to local time, 
        Summarise volume by local time.
    """
    # Derive hours, minutes
    df[['hour', 'minutes']] = df['time'].str.split(':', expand=True)   
    
    # Fill NaN with previous hour
    df['hour'].fillna(method='pad', inplace=True)

    # Align hour to business clock
    df['hour'] = pd.to_numeric(df['hour']) - 1
    df.loc[df['hour'] == -1,'hour'] = 23
    df['hour'] = df['hour'].apply(lambda x: str(x)+':00' if x >= 10 else '0'+str(x)+':00')

    # Group Volume by Time and rename columns to business header
    df = df.groupby(['hour'], sort=False, as_index=False)['volume'].aggregate(sum)
    df.columns = ['Local Time', 'Volume']

    return df

def save_csv(df, path, index=False):
    # Save df as csv    
    df.to_csv(path, index=index)


if __name__ == '__main__':
    trades = get_trades(date='01/03/2022')
    df = pd.DataFrame(trades[0])
    print(df)
    