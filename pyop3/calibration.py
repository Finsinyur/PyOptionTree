# -*- coding: utf-8 -*-
"""
Created on Mon Jan  2 00:07:19 2023

@author: leeca
"""

from . import binomial_tree, european_option, american_option, base_conditions
from inspect import signature
from scipy.optimize import brentq


def calibrate_european(V, S0, K, r, T, calibrate_range = (1.0001,10.0), call = True, **kwds):
    div_valid_kwds = signature(base_conditions.base_asset).parameters.keys()
    div_kwds = {k: v for k, v in kwds.items() if k in div_valid_kwds}
    
    bt_valid_kwds = signature(binomial_tree).parameters.keys()
    bt_kwds = {k: v for k, v in kwds.items() if k in bt_valid_kwds}

    bt_kwds.pop('sigma', None)
    bt_kwds.pop('u', None)
    
    option = 'call' if call == True else 'put'
    u = brentq(lambda x: european_option(binomial_tree(S0, r, T, u = x, freq_by = 'days', **bt_kwds, **div_kwds),\
                                                       K).fast_put_call()[option] - V,\
               calibrate_range[0], calibrate_range[1])
        
    
    return binomial_tree(S0, r, T, u = u, **bt_kwds, **div_kwds)

def calibrate_american(V, S0, K, r, T, calibrate_range = (1.0001,10.0), call = True, **kwds):
    
    div_valid_kwds = signature(base_conditions.base_asset).parameters.keys()
    div_kwds = {k: v for k, v in kwds.items() if k in div_valid_kwds}
    
    bt_valid_kwds = signature(binomial_tree).parameters.keys()
    bt_kwds = {k: v for k, v in kwds.items() if k in bt_valid_kwds}
    bt_kwds.pop('sigma', None)
    bt_kwds.pop('u', None)
    
    if call == True:
        u = brentq(lambda x: american_option(binomial_tree(S0, r, T, u = x, freq_by = 'days', **bt_kwds, **div_kwds),\
                                                           K).call() - V, calibrate_range[0], calibrate_range[1])
    else:
        u = brentq(lambda x: american_option(binomial_tree(S0, r, T, u = x, freq_by = 'days', **bt_kwds, **div_kwds),\
                                                           K).put() - V, calibrate_range[0], calibrate_range[1])
    
    return binomial_tree(S0, r, T, u = u, freq_by = 'days', **bt_kwds, **div_kwds)
    
def deamericanization(V, S0, K, r, T, calibrate_range = (1.0001,10.0), call = True, **kwds):
    option = "call" if call == True else "put"
    div_valid_kwds = signature(base_conditions.base_asset).parameters.keys()
    div_kwds = {k: v for k, v in kwds.items() if k in div_valid_kwds}
    
    bt_valid_kwds = signature(binomial_tree).parameters.keys()
    bt_kwds = {k: v for k, v in kwds.items() if k in bt_valid_kwds}
    
    underlying_asset = calibrate_american(V, S0, K, r, T, calibrate_range = (1.0001,10.0), call = True, **bt_kwds, **div_kwds)
    
    equivalent_eu_option = european_option(underlying_asset, K).fast_put_call()[option]
    
    res = {'underlying_asset': underlying_asset,
           'calibrated u': underlying_asset.u,
           'calibrated impl. vol': underlying_asset.implied_vol,
           'Equivalent European Option value':equivalent_eu_option,
           'Early Exercise Premium': V - equivalent_eu_option}
    
    return res