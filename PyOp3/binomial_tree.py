# -*- coding: utf-8 -*-
"""
Created on Fri Dec  9 02:08:04 2022

@author: leeca
"""
import numpy as np
import warnings

import base_conditions
from dateutil import parser

class fit_tree:
    '''
    Instance variables:
        
    - ``S0`` - float
    - ``r`` - float
    - ``T`` - float or str
    - ``N``  - int
    - ``u`` - float or None
    - ``sigma`` - float or None
    - ``div_info`` - tuple or list
    - ``spot_date`` - str or None
    Public methods:
        
    - ``underlying_asset_summary()`` - print summary of underlying asset information
    - ``underlying_asset_tree()`` - generate a binomial tree of the underlyng asset price
    '''
    
    def __init__(self, S0, r, T, N, u = None, sigma = None, divi_info = (0, 0, None, None), spot_date = None):
        """
            
        :param S0: underlying asset spot price at t = 0
        :type S0: float
        :param r: current interest rate, annualized
        :type r: float
        :param T: Either time to expiry (in year) or expiry date
        :type T: float or str
        :param N: Number of steps in the binomial tree. 
        :type N: int
        :param u: The upward move per step, as per CRR model. Default None
        :type u: float
        :param sigma: Implied volatility. Default None
        :type sigma: float
        :param divi_info: A collection of 4 items, representing Known Dollar Dividends, Dividend Yield, Ex-div date and Div step
        :type divi_info: tuple or list
        :param spot_date: Spot date. Default None. If assigned, T needs to be the expiry date
        :type spot_date: str
        """
        
        assert (len(divi_info) == 4) and isinstance(divi_info, (tuple, list)), "divi_info needs to be a tuple or list type with 4 items!"
        assert bool(u) ^ bool(sigma), 'Please assign non-None values to either only u or sigma!' # assert using XOR logic gate
        assert (N > 0) & (type(N) == int), 'N needs to be an integer with value greater than 0!'

        if spot_date == None:
            assert (T > 0), 'Spot date undefined! T needs to be greater than 0!'
            self.time_to_expiry = T
        else:
            
            time_to_exp = parser.parse(T) - parser.parse(spot_date)
            assert time_to_exp.days >= 0, 'Spot date needs to be before T, the expiry date!'
            self.time_to_expiry = time_to_exp.days/365
        
        div, div_yield, ex_div_date, ex_div_step = divi_info # unpack collection into the respective items
        
        self.underlying_asset = base_conditions.base_asset(S0, div, div_yield, ex_div_date, ex_div_step)
        self.interest_rate = base_conditions.base_rate(r).rate
        
        self.spot_date = spot_date
        self.step = N
        self.delta_t = self.time_to_expiry/N # step differential
        
        
        self.u = u if u != None else np.exp(sigma * np.sqrt(self.delta_t)) # calculate u (if not provided)
        self.implied_vol = sigma if sigma != None else np.log(u) / np.sqrt(self.delta_t)
        
        if 0 < self.u <= 1:
            warnings.warn(''''Bad "u" defined! 
                          For "u" that is non-negative and is lesser than 1, 
                          "u" will behave like "d" in a Binomial tree, vice versa.''')
        elif self.u <= 0:
            raise ValueError('"u" cannot be zero or negative!')
            
        self.d = 1/self.u
        
    def underlying_asset_summary(self):
        """
        Method to provide info on underlying asset.
        Returns
        -------
        None.
        """
        
        print('UNDERLYING ASSET SUMMARY\n\
              +--------------------------------+\n\
              Spot price: \t ${:.2f}\n\
              Time to expiry: \t {} years\n\
              interest rate: \t {:.2f}%\n\
              implied vol: \t {:.2f}%\n\
              '.format(self.underlying_asset.spot_price,\
              self.time_to_expiry,\
              self.interest_rate*100,\
              self.implied_vol*100))
        
        self.underlying_asset.dividend_info()
        
    def underlying_asset_tree(self):
        """
        Method to generate a matrix that illustrate the binomial tree model of the underlying asset.
        Returns
        -------
        Numpy array.
        """
        S = np.zeros([self.step+1,self.step+1])
        
        S[:, -1] = self.underlying_asset.spot_price*self.u**(np.arange(self.step, -1, -1))* self.d**(np.arange(0, self.step+1, 1))
        
        for i in np.arange(self.step-1, -1, -1):
            S[:i+1,i] = self.underlying_asset.spot_price*self.u**(np.arange(i, -1, -1))* self.d**(np.arange(0, i+1, 1))
        
        if self.underlying_asset.dividend_dollar != 0:
            dividends = self.__dividend_tree__()
            S -= dividends
        elif self.underlying_asset.dividend_yield != 0:
            S *= (1 - self.underlying_asset.dividend_yield)
            
        return S
    
    def __dividend_tree__(self):
        """
        Method to generate a matrix that illustrate the binomial tree model of the dividend.
        Only applies to known dollar dividends scenario.
        Returns
        -------
        Numpy array.
        """
        if self.underlying_asset.ex_div_date != None:
            div_day = self.underlying_asset.ex_div_date - self.spot_date
            div_step = div_day.days / self.delta_t
        elif self.underlying_asset.ex_div_step != None:
            div_step = self.underlying_asset.ex_div_step
        else:
            return np.zeros((self.step + 1,self.step + 1))
        
        logic_matrix_1 = np.ones((self.step + 1,self.step + 1))
        for col in range(self.step + 1):
            if col < div_step:
                logic_matrix_1[:, col] = 0
        
        logic_matrix_2 = np.ones((self.step + 1,self.step + 1))
        for col in range(self.step + 1):
            logic_matrix_2[col, :self.step + 1 -col] = self.u
            logic_matrix_2[col, self.step + 1 -col:] = self.d
        
        logic_matrix_3 = logic_matrix_1*logic_matrix_2
        logic_matrix_3[:,div_step] = 1
        logic_matrix_3[:,div_step:] = logic_matrix_3[:,div_step:].cumprod(axis =1)
        
        logic_matrix_4 = np.triu(np.ones((self.step + 1)))
        logic_matrix_5 = np.multiply(logic_matrix_3, logic_matrix_4)
        
        return self.underlying_asset.dividend_dollar * logic_matrix_5
