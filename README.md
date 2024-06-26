<p align="center">
    <img width=20% src="https://github.com/Finsinyur/PyOptionTree/blob/main/media/PyOp3_logo_v0.png?raw=true">
</p>

# PyOptionTree

PyOptionTree is a package designed for implementing lattice models for option pricing.

The objective of this package is to provide an intuitive and easy-to-implement open-source tool for students, academics and practioners to run theoretical pricing of
various simple and exotic options. The early version of the library shall focus on developing the Binomial Tree algorithm for option pricing, taking into account of dividends and various types of options.


Version: v0.2.3.

## Table of contents

-   [Getting started](#getting-started)
-   [A quick example](#a-quick-example)
-   [Overview of Binomial tree option pricing models](#overview-of-binomial-tree-option-pricing-models)
-   [Features](#features)
    -   [Underlying asset price dynamics](#underlying-asset-price-dynamics)
    -   [Trading days](#trading-days)
    -   [Dividends and yield treatment](#dividends-and-yield-treatment)
    -   [European options](#european-options)
    -   [American options](#american-options)
    -   [Visualizing the tree](#visualizing-the-tree)
    -   [Calibration](#calibration)
    -   [Exotic options](#exotic-options)
-   [Advantages of PyOptionTree](#advantages-of-pyoptiontree)
-   [Contributing](#contributing)
-   [Getting in touch](#getting-in-touch)

## Getting Started

PyOptionTree is currently available on the test environment only. While we are working to push out the project into production, we welcome users to try the test version and provide us feedback on the library.

For test version, one can download the package by:

```bash
pip install -i https://test.pypi.org/simple/ PyOptionTree
```

## A quick example

Here is a quick example of setting up the tree model. Here, we will show how one can initialize the underlying asset and plot the binomial tree of the underlying asset price dynamics.

```bash
import pyop3

# Initialize the binomial tree object
asset_1 = pyop3.binomial_tree(300, 0.08, 0.3333, sigma = 0.3)

# View underlying asset information
asset_1.underlying_asset_summary()

```

The output of the above:

```bash
UNDERLYING ASSET SUMMARY
        +--------------------------------+
              Spot price: 	 $300.00
              Time to expiry: 	 0.3333 years
              interest rate: 	 8.00%
              implied vol: 	 30.00%
              
No dividend payment expected during the course of the contract.
```

To retrieve the raw version of the underlying asset price lattice:

```bash
# Generate lattice of the underlying asset prices
asset_1_tree = asset_1.underlying_asset_tree()
print(asset_1_tree)
```

Output:

```bash
[[300.         327.13753696 356.72989363 388.99912921 424.18739004]
 [  0.         275.11364436 300.         327.13753696 356.72989363]
 [  0.           0.         252.29172437 275.11364436 300.        ]
 [  0.           0.           0.         231.36298578 252.29172437]
 [  0.           0.           0.           0.         212.17038062]]
```

The raw version of the underlying asset lattice is convenient for computation, but is hard for users to read.
PyOptionTree has a function which allows one to plot the tree:
```bash
# Visualize the tree in a graphic for better illustration
pyop3.tree_planter.show_tree(asset_1_tree, "Binomial Tree Price Development of Underlying Asset")
```

Output:

<img width=50% src="https://github.com/Finsinyur/PyOptionTree/blob/main/media/example_asset%20tree.png?raw=true">

## Overview of Binomial tree option pricing models

The Binomial tree algorithm was first introduced by Cox et. al in their 1979 paper "Option Pricing: A Simplified Approach". The tree model, famously known as the Cox-Ross-Rubinstein Tree (or CRR Tree for short) offers readers a simple-to-understand approach to option pricing while adhering to the no-arbitrage condition. Its simplistic and elegant approach may be what caused its to be mistaken as the predecessor of the Black-Scholes model (which was infact founded in 1973) by beginners. It also doesn't help that the CRR Tree is commonly used as the primer to option pricing for most financial mathematics and derivatives courses.

The steps to applying the binomial tree pricing algorithm are fairly straightforward; starting with the spot price $S_0$, to price a European option,
1. Define the upward multiplier $u$, which results in a price level $S_{(1,2)}^u$ which is higher than $S_0$, and the corresponding downward multiplier $d$ to get the lower price level $S_{(1,1)}^d$; these represents the potential upside and downside of the underlying asset, which gives us two states in the next time step
2. With $u$ and $d$ defined, calculate the risk neutral probability of an upward movement $p$; $p$ is risk-neutral as the discounted mean of the two states in the next time step will be equal to the current price 
3. Now work forward into the next $N$ steps; this creates a lattice where each node represents a price level, starting with $S_0$, and from each node there exists two branches that lead to two states - one the upside state $S_{(i,j)}^u$ and the other the downside state $S_{(i,j)}^d$; $i$ refers to the time step of the node, $j$ refers to the node number in that time step
4. Apply the option payoff function at time $T$ on all the terminal states represented by the terminal nodes
5. Finally, work backwards by taking the discounted mean of option payoff at the terminal nodes; this will give us the required option value

The Cox-Ross-Rubinstein (CRR) Tree suggests a binomial model in which the price of the underlying asset can, at each point in time, move up by a factor of $u$ and down by a factor of $d$, which $d = \frac{1}{u}$. With these parameters, the log-tree is such that it is symmetrical about the spot price at time 0. Relating to the Black-Scholes model, we find

$$u = e^{\sigma \sqrt{T}}, d = e^{- \sigma \sqrt{T}}, p = \frac{e^{r \Delta t} - d}{u - d}$$

In the same year, Rendleman and Bartter also provided their suggestions of the Binomial tree option pricing algorithm. It looks similar to that of the CRR tree, except that it restricts the risk-neutral probability to $p = 0.5$. This means that the log-tree is no longer symmetrical about the spot price at time 0.

$$p = \frac{1}{2}, u = e^{(r-0.5\sigma^2)\Delta t + \sigma \sqrt{\Delta t}}, d = e^{(r-0.5\sigma^2)\Delta t - \sigma \sqrt{\Delta t}}$$

The RB tree has upward and downward movements similar to the discrete version of the Black-Schole model of asset price dynamic, which takes the form

$$S_{t + \Delta t} = S_0e^{(r - 0.5 \sigma^2)\Delta t + \sigma (W_{t+\Delta t} - W_t)}$$

```pyop3``` currently allows implementation of both the CRR tree and the RB tree. In order to support both academic and practical use-cases, ```pyop3``` has incorporated the following features.

## Features
This section documents the features of PyOptionTree, with brief introduction of each features.
A comprehensive demonstration of the PyOptionTree may be found in the tutorials [here](https://github.com/Finsinyur/PyOptionTree/tree/main/tutorials).

### Underlying asset price dynamics
Similar to the basic approach to binomial tree option pricing, all impementation of option pricing starts with creating the binomial tree to illustrate the underlying asset price dynamics. The below image summarizes the implementation of the PyOptionTree.

<img width=50% src="https://github.com/Finsinyur/PyOptionTree/blob/main/tutorials/img/tut1_pic1.png?raw=true">

- Define expiry and number of discrete steps during the contract lifetime:

  - the most basic approach is a user-defined time-to-expiry, this is defined by the number of years; the number of discrete steps is flexible as long as it is a whole number; by default the number of time step is 4
  - alternatively, user can define the spot date (current date) and the expiration date; this feature is created to fit real world analysis, in which users are given expiration date of the contract rather than the time-to-expiry; the number of discrete steps can be flexible (either user-defined or in numebr of days) in absence of an ex-div date
  - if an ex-div date is defined the number of discrete steps would be calculated and rounded off to the nearest whole number

- Define type of binomial tree
  - At the moment, only two types of tree are supported, namely the CRR Tree and the RB Tree
  - Advanced tree models, including various improvements to the original tree models, trinomial tree, and other complex models will be introduced in future improvement

- Define upward and downward multipliers, $u$ and $d$
  - Users can directly define the upward multiplier $u$; depending on the type of tree defined, the corresponding downward multiplier $d$ will be calculated
  - Alternatively, to suit real-world analysis, user can provide the implied volatility $\sigma$; the $u$ and $d$ will be calculated based on the tree type
  
- yield rate (dividend yield rate, foreign interest rate)
  - At the moment, ```pyop3``` does not support yield rate; this limits application to strictly equity-liked assets
  - This will be part of the improvement pipeline

### Trading days
Embedded into the PyOptionTree library and also callable as a function, PyOptionTree offers a simple-to-use solution for calculating the number of trading days between two distinct dates. User simply needs to provide the start date, end date, and a collection of trading holidays for this to work.

```bash
nbr_trading_days = pyop3.tools.get_trading_days('01-12-2020', '10-01-2021',\
                                                trading_holidays = ['24-12-2020', '25-12-2020',\
                                                                    '31-12-2020', '01-01-2021'])
print(nbr_trading_days)
```

Output:
```bash
25
```

Future improvement to the function may include connecting to a reliable trading calendar source to automatically retrieve the trading holidays.


### Dividends treatment
PyOptionTree supports inclusion of known dollar dividends (up to only one dividend payment during the option lifetime) and known yield.

- Known dollar dividends
  - Supports known dollar dividends occuring on and before the expiration date, during the life time of the contract
  - When applied, user <b>must</b> define either the ex-dividend date ```ex_div_date``` or the step which ex-div occurs ```ex_div_step```
  - Due to non-recombining nature of the tree for dividends occuring midpoint, an approximation method is introduced to force tree recombination
  - Approximation method will be enhanced and improved based on known research papers in future improvement
  - Module will be enhanced to accomodate multiple known dollar dividends to account for option on dividend-paying asset with long time-to-expiry


### European options
European option pricing is the core of binomial tree model. To initiate the European Option pricing, user needs to initialize the ```pyop3.european_option``` object by passing the ```pyop3.binomial_tree``` object and the strike price.

```bash
strike = 300
my_european_option = pyop3.european_option(asset_1, strike)
```

PyOptionTree computes option prices with two methods.

- Distinctly calling the ```call()``` or ```put()``` methods to derive call and put values respectively
  - by running the distinct methods, PyOptionTree will compute the entire option lattice to derive the option value
  - after the methods are called, option value can be called for with the attributes ```call_value``` and ```put_value``` respectively

```bash
# To calculate call value, we need to first run the .call() method of the option object
asset_1_options.call()
print(asset_1_options.call_value)
```

Output
```bash
23.377924012466476
```

Do note that the option price above is likely inaccurate as we are using the default number of time steps (4) which is not sufficient to converge to the analytical solution.

- Calculate both call and put option values using the ```fast_put_call()``` method
  - Uniquely for European options, the option value can be derive solely with the terminal option payoffs without having to work backward
  - PyOptionTree works directly on the terminal call option payoff to arrive at the call option value
  - Once calculated, PyOptionTree will make use of put-call parity to get the respective put option value
  - This reduces the execution time by 80%
  - The method returns a dictionary of call and put values; the values are also assigned to the respective object attributes
  - No option lattice is created in this implementation

```bash
# Calculate call and put option values using fast method
my_european_option.fast_put_call()
```
Output
```bash
{'call': 23.377924012466476, 'put': 15.484427768048135}
```

### American options
Binomial tree option pricing model really shines when it comes to deriving the value of American options.
Similar to the European option, user needs to initialize the ```pyop3.american_option``` object by passing the ```pyop3.binomial_tree``` object and the strike price.
As American options requires working backwards on every nodes in each time step, there is only one method to calculate call and put options, which is by explicitly calling the ```call()``` and ```put()``` methods.

### Visualizing the tree
One value PyOptionTree offers its users is that the rendering of the binomial tree can be easily called by using its function ```pyop3.tree_planter.show_tree()```.
User simply needs to pass the numpy array which represents the lattice. The function currently offers some customizations, including setting the title of the plot, changing the node colors, among others.

This function builds on top of ```networkx``` and ```matplotlib.pyplot``` libraries. The function currently does not work with subplots.

### Calibration
To enhance usability of PyOptionTree, two calibrations are embedded in the functionalities.

- Calibrating to market data
  - Users are able to calibrate the binomial tree model to the market prices
  - PyOptionTree supports calibrating of American and European options
  - The output of the calibration is a ```pyop3.binomial_tree``` object with the calibrated ```u``` and ```implied_vol```
  - The calibrated values can be used to price more exotic options

- Deamericanization
  - Building on top of the calibration, PyOptionTree also supports deamericanization of American options to derive at the equivalent European option prices

### Exotic options
Exotic options are currently in the project pipeline and will be released in due time.


## Advantages of PyOptionTree
- designed to be easy-to-use by users with varied python programming experience
- incorporated concepts based on intensive academic research papers
- structured to accomodate practical implementations
- interoperable with proprietary models via Python

## Contributing

We welcome contributions from the community! More will be shared on how contributions to the package can be made.

PyOptionTree is currently maintained by:
- Caden Lee



## Getting in touch

If you experience any problem with PyOptionTree, please raise a GitHub issue.
You may get in touch with me at: caden.finsinyur@gmail.com
