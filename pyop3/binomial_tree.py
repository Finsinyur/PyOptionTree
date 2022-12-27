import numpy as np
import warnings
from inspect import signature

from . import base_conditions
from dateutil import parser

class binomial_tree:
    '''
    Instance variables:
        
    - ``S0`` - float
    - ``r`` - float
    - ``T`` - float or str
    - ``N``  - int
    - ``u`` - float or None
    - ``sigma`` - float or None
    - ``spot_date`` - str or None
    - ``day_first`` - boolean
    - ``freq_by`` - str

    Public methods:
        
    - ``underlying_asset_summary()`` - print summary of underlying asset information
    - ``underlying_asset_tree()`` - generate a binomial tree of the underlyng asset price
    '''
    def __init__(self, S0, r, T, N = 4, u = None, sigma = None, spot_date = None, dayfirst = True, freq_by = 'N', **kwds):
        
        """
            
        :param S0: underlying asset spot price at t = 0
        :type S0: float
        :param r: current interest rate, annualized
        :type r: float
        :param T: Either time to expiry (in year) or expiry date
        :type T: float or str
        :param N: Number of steps in the binomial tree. Default N = 4 
        :type N: int
        :param u: The upward move per step, as per CRR model. Default None
        :type u: float
        :param sigma: Implied volatility. Default None
        :type sigma: float
        :param spot_date: Spot date. Default None. If assigned, T needs to be the expiry date
        :type spot_date: str
        :param freq_by: Define how discrete time step is determined, either by "N" (user-defined) or "days". Default 'N'. 
        :type freq_by: str
        :param div: known dollar dividend. Default 0
        :type div: float
        :param div_yield: known dividend yield. Default 0
        :type div_yield: float
        :param ex_div_date: Ex-dividend date. Default None
        :type ex_div_date: str
        :param ex_div_step: Number of steps from t = 0 in which Ex-dividend occurs. Default None
        :type ex_div_date: int

        """
        assert bool(u) ^ bool(sigma), 'Please assign non-None values to either only u or sigma!' # assert using XOR logic gate
        assert freq_by in ['N', 'days'], 'Current supported frequencies are by user defined time step N or days'
        
        if freq_by == 'N':
            0
        else:
            assert (spot_date != None) & (type(T) == str),\
                'freq_by is selected to be based on days, please define both spot_date and T (as the expiry date)!'

        if spot_date == None:
            assert (T > 0), 'Spot date undefined! T needs to be greater than 0!'
            self.time_to_expiry = T
        else:
            spot_date = parser.parse(spot_date, dayfirst = dayfirst)
            time_to_exp = parser.parse(T, dayfirst = dayfirst) - spot_date
            assert time_to_exp.days >= 0, 'Spot date needs to be before T, the expiry date!'
            self.time_to_expiry = time_to_exp.days/365
        
        if freq_by == 'days':
            N = time_to_exp.days
        
        valid_kwds = signature(base_conditions.base_asset).parameters.keys()
        div_kwds = {k: v for k, v in kwds.items() if k in valid_kwds}
        #div, div_yield, ex_div_date, ex_div_step = divi_info # unpack collection into the respective items
        
        self.freq_by = freq_by
        self.underlying_asset = base_conditions.base_asset(S0, dayfirst = dayfirst, **div_kwds)
        self.interest_rate = base_conditions.base_rate(r).rate
        
        self.spot_date = spot_date
        self.step = N
        self.delta_t = self.time_to_expiry/N # step differential
        
        
        self.u = u if u != None else np.exp(sigma * np.sqrt(self.delta_t)) # calculate u (if not provided)
        self.implied_vol = sigma if sigma != None else np.log(u) / np.sqrt(self.delta_t)
        
        if 0 < self.u <= 1:
            warnings.warn('''Bad "u" defined! 
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
              Time to expiry: \t {:.4f} years\n\
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
            S *= (1 - self.underlying_asset.dividend_yield*self.delta_t)
            
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
            div_step = div_day.days 
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
    


class european_option:
    '''
    Instance variables:
        
    - ``underlying_asset`` - pyop3.binomial_tree object
    - ``strike`` - float
    - ``cont_disc` - bool

    Public methods:
        
    - ``call()`` - calculate call opton value and generate call option tree
    - ``put()`` - calculate put opton value and generate put option tree
    '''
    
    def __init__(self, underlying_asset, strike, cont_disc = True):
        """
            
        :param underlying_asset: underlying asset binomial_tree object
        :type S0: pyop3.binomial_tree
        :param strike: strike price of the option
        :type strike: float
        :param cont_disc: define discounting method - continoues or discrete. Default True
        :type cont_disc: boolean
        

        """
        self.asset_tree = underlying_asset.underlying_asset_tree()
        self.strike = strike
        self.u = underlying_asset.u
        self.d = underlying_asset.d
        self.r = underlying_asset.interest_rate
        self.step = underlying_asset.step
        self.time_to_expiry = underlying_asset.time_to_expiry
        self.delta_t = underlying_asset.delta_t 
        self.disc_factor = np.exp(-self.r * self.delta_t) if cont_disc==True else 1/(1+self.r*self.delta_t)
        self.risk_neutral_prob = (1/self.disc_factor - self.d)/(self.u - self.d)
        
        self.call_value = None
        self.call_option = None
        self.put_value = None
        self.put_option = None
        
    def call(self):
        """
        Method to to calculate call option value.
        During the running of the method, derived call option value and call optiion tree
        are assigned to the object's call_value and call_option attributes respectively.

        Returns
        -------
        Numpy array.

        """
        V = np.zeros([self.step+1,self.step+1])
        
        V[:, -1] = np.maximum(0, self.asset_tree[:,-1] - self.strike)
        
        
        for i in np.arange(self.step-1, -1, -1):
            V[:i+1,i] = self.disc_factor*(self.risk_neutral_prob*V[:i+1,i+1] + (1-self.risk_neutral_prob)*V[1:i+2,i+1])
            
        self.call_option = V
        self.call_value = V[0,0]
        return V
    
    def put(self):
        """
        Method to to calculate put option value.
        During the running of the method, derived put option value and put optiion tree
        are assigned to the object's put_value and put_option attributes respectively.

        Returns
        -------
        Numpy array.
        """

        V = np.zeros([self.step+1,self.step+1])
        
        V[:, -1] = np.maximum(0, self.strike - self.asset_tree[:,-1])
        
        
        for i in np.arange(self.step-1, -1, -1):
            V[:i+1,i] = self.disc_factor*(self.risk_neutral_prob*V[:i+1,i+1] + (1-self.risk_neutral_prob)*V[1:i+2,i+1])
            
        self.put_option = V
        self.put_value = V[0,0]
        return V


    
