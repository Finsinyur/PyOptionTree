import copy
import numpy as np
import math
import warnings
from inspect import signature

from . import base_conditions
from . import tools
from dateutil import parser

class binomial_tree:
    """
    Instance variables:
        
    - ``S0`` - float. The spot price of underlying asset.
    - ``r`` - float. The interest rate used to discount future values.
    - ``T`` - float or str. The time to expiry in number of years (int), or the expiration date (str).
    - ``N``  - int. The number of discrete time steps until expiry. Default N = 4.
    - ``u`` - float or None. The upward return.
    - ``sigma`` - float or None. The implied volatility.
    - ``spot_date`` - str or None. The current date (used if T is defined to be a date)
    - ``day_first`` - boolean. Default True.
    - ``freq_by`` - str. Default "N". Can take either "N" or "days".
    - ``tree_type`` - str. Default "CRR". Can take either "CRR" (Cox-Ross-Rubinstein Tree) or "RB" (Rendleman Bartter Tree). 
    Public methods:
        
    - ``underlying_asset_summary()`` - print summary of underlying asset information
    - ``underlying_asset_tree()`` - generate a binomial tree of the underlyng asset price
    """
    def __init__(self, S0, r, T, N = 4, u = None, sigma = None, spot_date = None, trading_holidays = None, dayfirst = True, freq_by = 'N', tree_type = 'CRR', **kwds):
        
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
            assert (N > 0) & (type(N) == int), 'N must be an integer and is greater than 0!'
        else:
            assert (spot_date != None) & (type(T) == str),\
                'freq_by is selected to be based on days, please define both spot_date and T (as the expiry date)!'
                
        self.trading_holidays = trading_holidays
        
        if spot_date == None:
            assert (T > 0), 'Spot date undefined! T needs to be greater than 0!'
            self.time_to_expiry = T
        else:
            
            trading_days = tools.get_trading_days(spot_date, T, self.trading_holidays)
            self.time_to_expiry = trading_days/252
        
        if freq_by == 'days':
            N = trading_days
        
        valid_kwds = signature(base_conditions.base_asset).parameters.keys()
        div_kwds = {k: v for k, v in kwds.items() if k in valid_kwds}
        
        self.freq_by = freq_by
        self.tree_type = tree_type.upper()
        
        self.underlying_asset = base_conditions.base_asset(S0, dayfirst = dayfirst, **div_kwds)
        self.interest_rate = base_conditions.base_rate(r).rate
        
        self.spot_date = spot_date
        self.step = N
        self.delta_t = self.time_to_expiry/N # step differential
        
        if self.tree_type == 'CRR':
            self.u = u if u != None else np.exp(sigma * np.sqrt(self.delta_t)) # calculate u (if not provided)
            self.implied_vol = sigma if sigma != None else np.log(u) / np.sqrt(self.delta_t)
            self.d = 1/self.u
            
        elif self.tree_type == 'RB':
            self.u = u if u != None else np.exp((self.interest_rate - 0.5*np.power(sigma,2))*self.delta_t + sigma*np.sqrt(self.delta_t))
            if sigma != None:
                self.implied_vol = sigma 
            else:
                A = 1
                B = -2/np.sqrt(self.delta_t)
                C = 2/np.sqrt(self.delta_t) * (np.log(u) - self.interest_rate * self.delta_t)
                
                self.implied_vol = (-B + np.sqrt(np.power(B,2) - 4*A*C))/(2*A)
                
            self.d = np.exp((self.interest_rate  - 0.5*np.power(self.implied_vol,2))*self.delta_t - self.implied_vol * np.sqrt(self.delta_t))
        
        else:
            raise ValueError('Tree type {} not supported!'.format(self.tree_type))
        
        if 0 < self.u <= 1:
            warnings.warn('''Bad "u" defined! 
                          For "u" that is non-negative and is lesser than 1, 
                          "u" will behave like "d" in a Binomial tree, vice versa.''')
        elif self.u <= 0:
            raise ValueError('"u" cannot be zero or negative!')

            
        
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
    
    def copy(self):
        """
        Method to allow creation of a copy of the binomial_tree obj.
        
        Returns
        -------
        pyop3 binomial_tree.
        """
        return copy.copy(self)
    
    def __dividend_tree__(self):
        """
        Method to generate a matrix that illustrate the binomial tree model of the dividend.
        Only applies to known dollar dividends scenario.

        Returns
        -------
        Numpy array.

        """
        if self.underlying_asset.ex_div_date != None:
            div_step = tools.get_trading_days(self.spot_date, self.underlying_asset.ex_div_date, self.trading_holidays)
            
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
    """
    Instance variables:
        
    - ``underlying_asset`` - pyop3.binomial_tree object
    - ``strike`` - float
    - ``cont_disc` - bool

    Public methods:
        
    - ``call()`` - calculate call opton value and generate call option tree
    - ``put()`` - calculate put opton value and generate put option tree
    """
    
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
        self.tree_type = underlying_asset.tree_type
        
        if self.tree_type == 'CRR':
            self.risk_neutral_prob = (1/self.disc_factor - self.d)/(self.u - self.d) 
        elif self.tree_type == 'RB':
            self.risk_neutral_prob = 0.5
        
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
        Float.

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
        Method to calculate put option value.
        During the running of the method, derived put option value and put optiion tree
        are assigned to the object's put_value and put_option attributes respectively.

        Returns
        -------
        Float.
        """

        V = np.zeros([self.step+1,self.step+1])
        
        V[:, -1] = np.maximum(0, self.strike - self.asset_tree[:,-1])
        
        
        for i in np.arange(self.step-1, -1, -1):
            V[:i+1,i] = self.disc_factor*(self.risk_neutral_prob*V[:i+1,i+1] + (1-self.risk_neutral_prob)*V[1:i+2,i+1])
            
        self.put_option = V
        self.put_value = V[0,0]
        return V
    
    def fast_put_call(self):
        """
        Method to swiftly calculate both call and put option values.
        The method works directly on the terminal option payoff without creating the tree.
        Once the call value is derived directly, the put option is calculated using the call-put parity.
        Once method finishes the calculation, call and put option values are assigned to the respective attributes.

        Returns
        -------
        Dictionary.
        """
        
        probabilities = self.risk_neutral_prob**(np.arange(self.step, -1, -1))*(1 - self.risk_neutral_prob)**(np.arange(0, self.step+1, 1))
        
        freq_matrix = np.array([self.__nCr__(i) for i in range(self.step+1)])
        terminal_probabilities = np.multiply(probabilities, freq_matrix)
        
        terminal_call_values = np.maximum(0, self.asset_tree[:,-1] - self.strike)
        self.call_value = np.dot(terminal_call_values, terminal_probabilities) * np.power(self.disc_factor, self.step)
        self.call_put_parity()
        
        return {'call': self.call_value, 'put': self.put_value}
        
        
        
    def __nCr__(self,r):
        """
        Private method to calculate combination, to be used for fast_put_call().
        
        Returns
        -------
        Float.
        """
        return math.factorial(self.step)/(math.factorial(r) * math.factorial(self.step - r))
    
    def call_put_parity(self):
        """
        Method to calculate call or put option value, provided either call_value or put_value is computed.
        
        Returns
        -------
        None.
        """
        assert (self.call_value != None) or (self.put_value != None), 'Please calculate either call or put first!'
        if self.call_value != None:
            self.put_value = self.call_value + self.strike * np.power(self.disc_factor, self.step) - self.asset_tree[0,0]
        else:
            self.call_value = self.put_value + self.asset_tree[0,0] - self.strike * np.power(self.disc_factor, self.step)


class american_option:
    """
    Instance variables:
        
    - ``underlying_asset`` - pyop3.binomial_tree object
    - ``strike`` - float
    - ``cont_disc` - bool
    Public methods:
        
    - ``call()`` - calculate call opton value and generate call option tree
    - ``put()`` - calculate put opton value and generate put option tree
    """
    
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
        self.tree_type = underlying_asset.tree_type
        
        if self.tree_type == 'CRR':
            self.risk_neutral_prob = (1/self.disc_factor - self.d)/(self.u - self.d) 
        elif self.tree_type == 'RB':
            self.risk_neutral_prob = 0.5
        
        self.call_value = None
        self.call_option = None
        self.put_value = None
        self.put_option = None
        
    def call(self):
        """
        Method to to calculate call option value.
        Backwardation - call option value is calculated by, first, working on the hypothetical option value at terminal node. 
        From every terminal node to its penultimate node, penultimate option value is the higher of intrinsic value at node (S-K) and the interest-rate discounted expected value evaluated using risk-neutral probability. 
        The pattern repeats until the initial option value. 
        Returns
        -------
        Float.
        """
        V = np.zeros([self.step+1,self.step+1])
        
        #find V[:,-1]
        for row in np.arange(0,self.step+1):
            V[row,self.step] = np.maximum(0,self.asset_tree[row,self.step] - self.strike)
        
        #find V[:-2] and before, all the way to V0
        for col in np.arange(self.step-1,-1,-1):
            for row in np.arange(0,col+1):
                V[row,col] = np.maximum((self.asset_tree[row,col]-self.strike), 
                                        self.disc_factor*(self.risk_neutral_prob*V[row,col+1]+
                                                          (1-self.risk_neutral_prob)*V[row+1,col+1]))
            
        self.call_option = V
        self.call_value = V[0,0]
        return V[0,0]
    
    def put(self):
        """
        Method to to calculate put option value.
        Similar to the evaluation of call option value, backwardation is employed.
        However, intrinsic value of put option is (K-S) instead.
        
        Returns
        -------
        Float.
        """

        V = np.zeros([self.step+1,self.step+1])
        
        #find V[:,-1]
        for row in np.arange(0,self.step+1):
            V[row,self.step] = np.maximum(0,self.strike - self.asset_tree[row,self.step])
        
        #find V[:-2] and before, all the way to V0
        for col in np.arange(self.step-1,-1,-1):
            for row in np.arange(0,col+1):
                V[row,col] = np.maximum((self.strike-self.asset_tree[row,col]), 
                                        self.disc_factor*(self.risk_neutral_prob*V[row,col+1]+
                                                          (1-self.risk_neutral_prob)*V[row+1,col+1]))
            
        self.put_option = V
        self.put_value = V[0,0]
        return V[0,0]
