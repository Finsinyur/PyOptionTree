from . import binomial_tree, european_option, american_option, base_conditions
from inspect import signature
from scipy.optimize import brentq


def calibrate_european(V, S0, K, r, T, N = 50, calibrate_range = (1.0001,10.0), call = True, freq_by = "N", **kwds):
    r"""
    Function to calibrate parameters to match the market price of European option.
    The function will take in all available parameters and calibrate to match the market price by finding
    the closest possible value of upward movement u, and thereby the calibrated implied vol.
    
    Parameters
    ----------
    V : float
        The option market price.
        
    S0 : float
         The underlying asset spot price.
    
    K : float
        The option strike price.
        
    r : float
        The relevant interest rate (annualized).
    
    T : float or string
        If float, this represents the time to expiry (in years). If string, this would be the date of expiry.
    
    N : Int
        Number of time step. Default is 50 to ensure convergence.
    
    calibrate_range : tuple or list
                      contains the minimum guess of u and the maximum guess of u, in this order.
    
    call : boolean
           If True, the option to calibrate is a call option. Otherwise it is a put option.
           
    freq_by : str
              Can take either "days" or "N". If "N", number of timestep is defined by user's input. If "days", function will take the number of days
              between spot date and expiry date. Default "N".   
    
    kwds : optional keywords. 
           See pyop3.binomial_tree() and pyop3.base_conditions.base_asset() for a description of optional keywords.
           
    Output
    ----------
    pyop3.binomial_tree object

    Examples
    --------
    >>> S0 = 366.02
    >>> V = 6.35
    >>> K = 366
    >>> r = 0.014216

    >>> spot_date = '01-12-2020'
    >>> T = '18-12-2020'
    >>> ex_div_date = '18-12-2020'
    
    calibrated_res = pyop3_test.calibrate_european(V, S0, K, r, T, call = False, div = 1.58,\
                                          spot_date=spot_date, ex_div_date = ex_div_date)
        
    calibrated_res.underlying_asset_summary()
    print(calibrated_res.u)

    """
    div_valid_kwds = signature(base_conditions.base_asset).parameters.keys()
    div_kwds = {k: v for k, v in kwds.items() if k in div_valid_kwds}
    
    bt_valid_kwds = signature(binomial_tree).parameters.keys()
    bt_kwds = {k: v for k, v in kwds.items() if k in bt_valid_kwds}

    bt_kwds.pop('sigma', None)
    bt_kwds.pop('u', None)
    
    option = 'call' if call == True else 'put'
    u = brentq(lambda x: european_option(binomial_tree(S0, r, T, u = x, N = N, freq_by = freq_by, **bt_kwds, **div_kwds),\
                                                       K).fast_put_call()[option] - V,\
               calibrate_range[0], calibrate_range[1])
        
    
    return binomial_tree(S0, r, T, u = u, N = N,**bt_kwds, **div_kwds)

def calibrate_american(V, S0, K, r, T, N = 50, calibrate_range = (1.0001,10.0), call = True, freq_by = "N", **kwds):
    r"""
    Function to calibrate parameters to match the market price of American option.
    The function will take in all available parameters and calibrate to match the market price by finding
    the closest possible value of upward movement u, and thereby the calibrated implied vol.
    
    Parameters
    ----------
    V : float
        The option market price.
        
    S0 : float
         The underlying asset spot price.
    
    K : float
        The option strike price.
        
    r : float
        The relevant interest rate (annualized).
    
    T : float or string
        If float, this represents the time to expiry (in years). If string, this would be the date of expiry.
    
    N : Int
        Number of time step. Default is 50 to ensure convergence.
    
    calibrate_range : tuple or list
                      contains the minimum guess of u and the maximum guess of u, in this order.
    
    call : boolean
           If True, the option to calibrate is a call option. Otherwise it is a put option.
           
    freq_by : str
              Can take either "days" or "N". If "N", number of timestep is defined by user's input. If "days", function will take the number of days
              between spot date and expiry date. Default "N".   
    
    kwds : optional keywords. 
           See pyop3.binomial_tree() and pyop3.base_conditions.base_asset() for a description of optional keywords.
           
    Output
    ----------
    pyop3.binomial_tree object

    Examples
    --------
    >>> S0 = 366.02
    >>> V = 6.35
    >>> K = 366
    >>> r = 0.014216

    >>> spot_date = '01-12-2020'
    >>> T = '18-12-2020'
    >>> ex_div_date = '18-12-2020'
    
    calibrated_res = pyop3_test.calibrate_american(V, S0, K, r, T, call = False, div = 1.58,\
                                          spot_date=spot_date, ex_div_date = ex_div_date)
        
    calibrated_res.underlying_asset_summary()
    print(calibrated_res.u)

    """
    
    div_valid_kwds = signature(base_conditions.base_asset).parameters.keys()
    div_kwds = {k: v for k, v in kwds.items() if k in div_valid_kwds}
    
    bt_valid_kwds = signature(binomial_tree).parameters.keys()
    bt_kwds = {k: v for k, v in kwds.items() if k in bt_valid_kwds}
    bt_kwds.pop('sigma', None)
    bt_kwds.pop('u', None)
    
    if call == True:
        u = brentq(lambda x: american_option(binomial_tree(S0, r, T, u = x, freq_by = freq_by, N = N, **bt_kwds, **div_kwds),\
                                                           K).call() - V, calibrate_range[0], calibrate_range[1])
    else:
        u = brentq(lambda x: american_option(binomial_tree(S0, r, T, u = x, freq_by = freq_by, N = N, **bt_kwds, **div_kwds),\
                                                           K).put() - V, calibrate_range[0], calibrate_range[1])
    
    return binomial_tree(S0, r, T, u = u, freq_by = freq_by, N = N, **bt_kwds, **div_kwds)


def deamericanization(V, S0, K, r, T, N = 50, calibrate_range = (1.0001,10.0), call = True, freq_by = "N", **kwds):
    r"""
    Function to "deamericanize" an American option given its market price, and find the equivalent European Option.
        
    Parameters
    ----------
    V : float
        The option market price.
        
    S0 : float
         The underlying asset spot price.
    
    K : float
        The option strike price.
        
    r : float
        The relevant interest rate (annualized).
    
    T : float or string
        If float, this represents the time to expiry (in years). If string, this would be the date of expiry.
        
    N : Int
        Number of time step. Default is 50 to ensure convergence.
    
    calibrate_range : tuple or list
                      contains the minimum guess of u and the maximum guess of u, in this order.
    
    call : boolean
           If True, the option to calibrate is a call option. Otherwise it is a put option.
           
    freq_by : str
              Can take either "days" or "N". If "N", number of timestep is defined by user's input. If "days", function will take the number of days
              between spot date and expiry date. Default "N".      
    
    kwds : optional keywords. 
           See pyop3.binomial_tree() and pyop3.base_conditions.base_asset() for a description of optional keywords.
           
    Output
    ----------
    Dictionary.

    Examples
    --------
    >>> S0 = 366.02
    >>> V = 6.35
    >>> K = 366
    >>> r = 0.014216

    >>> spot_date = '01-12-2020'
    >>> T = '18-12-2020'
    >>> ex_div_date = '18-12-2020'
    
    res = pyop3_test.deamericanization(V, S0, K, r, T, call = False, div = 1.58,\
                                          spot_date=spot_date, ex_div_date = ex_div_date)

    """
    option = "call" if call == True else "put"
    div_valid_kwds = signature(base_conditions.base_asset).parameters.keys()
    div_kwds = {k: v for k, v in kwds.items() if k in div_valid_kwds}
    
    bt_valid_kwds = signature(binomial_tree).parameters.keys()
    bt_kwds = {k: v for k, v in kwds.items() if k in bt_valid_kwds}
    
    underlying_asset = calibrate_american(V, S0, K, r, T, N = N, calibrate_range = (1.0001,10.0), call = call, freq_by = freq_by, **bt_kwds, **div_kwds)
    
    equivalent_eu_option = european_option(underlying_asset, K).fast_put_call()[option]
    
    res = {'underlying_asset': underlying_asset,
           'calibrated u': underlying_asset.u,
           'calibrated impl. vol': underlying_asset.implied_vol,
           'Equivalent European Option value':equivalent_eu_option,
           'Early Exercise Premium': V - equivalent_eu_option}
    
    return res
