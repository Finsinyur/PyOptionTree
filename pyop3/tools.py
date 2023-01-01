# -*- coding: utf-8 -*-
"""
Created on Sun Jan  1 23:15:59 2023

@author: leeca
"""

import numpy as np
from dateutil import parser

def get_trading_days(start, end, trading_holidays = None, dayfirst = True):
    
    start_date = parser.parse(start, dayfirst = dayfirst).date()
    end_date = parser.parse(end, dayfirst = dayfirst).date()
    trading_days = np.busday_count(start_date, end_date)
    
    assert trading_days >0, "end_date must be later than start_date!"
    total_valid_exclusions = 0
    
    if trading_holidays != None:
        assert type(trading_holidays) in [str, list, tuple], "trading_holidays must be either a str type or list/tuple!"
        if type(trading_holidays) in [list, tuple]:
            exclusions = np.array([parser.parse(date).date() for date in trading_holidays])
        else:
            exclusions = np.array(parser.parse(trading_holidays).date())
            
        exclusions_after_start = exclusions >= start_date
        exclusions_before_end = exclusions <= end_date
        valid_exclusions = np.multiply(exclusions_after_start, exclusions_before_end)
        total_valid_exclusions += valid_exclusions.sum()
    
    trading_days -= total_valid_exclusions
    
    return trading_days
    
    