class american_option:
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
        Backwardation - call option value is calculated by, first, working on the hypothetical option value at terminal node. 
        From every terminal node to its penultimate node, penultimate option value is the higher of intrinsic value at node (S-K) and the interest-rate discounted expected value evaluated using risk-neutral probability. 
        The pattern repeats until the initial option value. 

        Returns
        -------
        Numpy array.
        """
        V = np.zeros([self.step+1,self.step+1])
        
        #find V[:,-1]
        for row in np.arange(0,self.step+1):
            V[row,self.step+1] = self.asset_tree[0,N+1] - self.strike
        
        #find V[:-2] and before, all the way to V0
        
        for row in np.arange(0, self.step-1):
            for col in np.arange(self.step-1,-1,-1):
                V[row,col] = np.maximum((self.asset_tree[row,col]-self.strike), 
                                        self.disc_factor*(self.risk_neutral_prob*self.asset_tree[row,col+1]+
                                                          (1-self.risk_neutral_prob)*self.asset_tree[row+1,col+1]))
            
        self.call_option = V
        self.call_value = V[0,0]
        return V
    
    def put(self):
        """
        Method to to calculate put option value.
        Similar to the evaluation of call option value, backwardation is employed.
        However, intrinsic value of put option is (K-S) instead.
        
        Returns
        -------
        Numpy array.
        """

        V = np.zeros([self.step+1,self.step+1])
        
        #find V[:,-1]
        for row in np.arange(0,self.step+1):
            V[row,self.step+1] = self.strike - self.asset_tree[0,N+1] 
        
        #find V[:-2] and before, all the way to V0
        
        for row in np.arange(0, self.step-1):
            for col in np.arange(self.step-1,-1,-1):
                V[row,col] = np.maximum((self.strike - self.asset_tree[row,col]), 
                                        self.disc_factor*(self.risk_neutral_prob*self.asset_tree[row,col+1]+
                                                          (1-self.risk_neutral_prob)*self.asset_tree[row+1,col+1]))
                
        self.put_option = V
        self.put_value = V[0,0]
        return V
