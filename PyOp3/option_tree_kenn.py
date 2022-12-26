import binomial_tree
import numpy as np
import base_conditions
import pandas as pd

#def option_tree(S0,r,T,N,K,u,opt='european',call=True,cont_disc=False):
def european_option_tree(self):
    #determine d
    self.d=1/self.u
    
    #initialise the asset and option matrix
    V=np.zeros([self.step+1,self.step+1])
    S=np.zeros((self.step+1,self.step+1)) # Caden: We already created a class that can generate underlying asset lattice, we can just make use of that
    
    #discount factor
    disc = np.exp(-self.r*delta_T) if cont_disc==True else 1/((1+self.r)**(self.step) #to confirm the formula 
    # Caden: formula is not correct. for continuous discounting: np.exp(-self.r*delta_T); for non-cont., should be 1/(1+self.r*self.delta_t)
    
    #find ST first
    #S[:,-1] = self.underlying_asset.spot_price_price*self.d**(np.arange(self.step,-1,-1))*self.u**(np.arange(0,self.step+1,1))                                           
    # Redundant; could make use of underlying_asset_tree
    tree = fit_tree(self)
    S = tree.underlying_asset_tree()
    terminal_node = S[:,-1]
                                                        
    #set the terminal price
    #V[:,-1] = np.maximum(0, disc*(self.spot_price-K)) if call == True else np.maximum(0, disc*(K-self.spot_price))
    self.underlying_asset
    V[:,-1] = np.maximum(0, disc*(terminal_node-K)) if call == True else np.maximum(0, disc*(K-terminal_node))                                                          
    # At terminal node, should be strike - terminal spot price, which should be the last col of the underlying asset tree
    
    #risk-neutral probability
    p=(1/disc-self.d)/(self.u-self.d) if cont_disc==True else (1+r-d)/(u-d) # should be cont_disc == True
    
    for i in np.arange(N-1,-1,-1):
        V[:i+1,i]= disc*(V[1:i+2,i+1]*p+V[:i+1,i+1]*(1-p))
    
    # We can split European and American; 
        if opt=='european':
    # Recall: if option is American, the value of option at t is the bigger of the discounted value at t+1 or the difference between spot price and strike.
            if call==True:
                V[:i+1,i]= np.maximum(V[:i+1,i],S[:i+1,i]-K)
            else:
                V[:i+1,i]= np.maximum(V[:i+1,i],K-S[:i+1,i])
        #else: 
            #american_option_tree(self) #insert function of america option? 
    
    return V
