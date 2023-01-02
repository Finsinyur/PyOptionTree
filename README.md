<p align="center">
    <img width=20% src="https://github.com/Finsinyur/PyOptionTree/blob/main/media/PyOp3_logo_v0.png?raw=true">
</p>

# PyOptionTree

PyOptionTree is a package designed for implementing lattice models for option pricing.

The objective of this package is to provide an intuitive and easy-to-implement open-source tool for students, academics and practioners to run theoretical pricing of
various simple and exotic options. The early version of the library shall focus on developing the Binomial Tree algorithm for option pricing, taking into account of dividends and various types of options.

As a start, the Binomial tree algorithm implemented is based on the Cox-Ross-Rubenstein market model, published by Cox et al in their 1979 paper "Option Pricing: A Simplified Approach". For future extension, other alternatives will be incorporated, such as the Rendleman-Bartter (RB) tree and various improvements. In further future, the package will aim to include Trinomial tree models and use cases beyond option pricing.

Version: v0.1.0

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

## Features
This section documents the features of PyOptionTree, with brief introduction of each features.
A comprehensive demonstration of the PyOptionTree may be found in the tutorials [here](https://github.com/Finsinyur/PyOptionTree/tree/main/tutorials).

### Underlying asset price dynamics
Similar to the basic approach to binomial tree option pricing, all impementation of option pricing starts with creating the binomial tree to illustrate the underlying asset price dynamics. The below image summarizes the implementation of the PyOptionTree.

<img width=50% src="https://github.com/Finsinyur/PyOptionTree/blob/main/tutorials/img/tut1_pic1.png?raw=true">

- Define expiry and number of discrete steps during the contract lifetime:

  - the most basic approach is a user-defined time-to-expiry, this is defined by the number of years; the number of discrete steps is flexible as long as it is a whole number
  - alternatively, user can define the spot date (current date) and the expiration date; this feature is created to fit real world analysis, in which users are given expiration date of the contract rather than the time-to-expiry; the number of discrete steps can be flexible (either user-defined or in numebr of days) in absence of an ex-div date
  - if an ex-div date is defined the number of discrete steps is then strictly in days

- Define type of binomial tree
  - At the moment, only two types of tree are supported, namely the CRR Tree and the RB Tree
  - Advanced tree models, including various improvements to the original tree models, trinomial tree, and other complex models will be introduced in future improvement

- Define upward and downward multipliers, $u$ and $d$
  - Users can directly define the upward multiplier $u$; depending on the type of tree defined, the corresponding downward multiplier $d$ will be calculated
  - Alternatively, to suit real-world analysis, user can provide the implied volatility $\sigma$; the $u$ and $d$ will be calculated based on the tree type

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


### Dividends and yield treatment
PyOptionTree supports inclusion of known dollar dividends (up to only one dividend payment during the option lifetime) and known yield.

- Known dollar dividends
  - Supports known dollar dividends occuring on and before the expiration date, during the life time of the contract
  - Due to non-recombining nature of the tree for dividends occuring midpoint, an approximation method is introduced to force tree recombination
  - Approximation method will be enhanced and improved based on known research papers in future improvement
  - Module will be enhanced to accomodate multiple known dollar dividends to account for option on dividend-paying asset with long time-to-expiry; at the moment, this needs to be approximated using dividend yield

- Known (dividend) yield
  - Natively supports inclusion of dividend yield
  - Suitable for pricing of currency options, with the foreign interest rate being the ```div_yield```

### European options
European option pricing is the core of binomial tree model. To initiate the European Option pricing, user needs to initialize the ```pyop3.european_option``` object by passing the ```pyop3.binomial_tree``` object and the strike price.

```bash
my_european_option = pyop3.european_option(asset_1, strike)
```

PyOptionTree computes option prices with two methods.

- Distinctly calling the ```call()``` or ```put()``` methods to derive call and put values respectively
  - by running the distinct methods, PyOptionTree will compute the entire option lattice to derive the option value


### American options

### Visualizing the tree

### Calibration



## Advantages of project

## Contributing

We welcome contributions from the community! More will be shared on how contributions to the package can be made.

PyOptionTree is currently maintained by:
- Caden Lee
- Kenn Ong
- Lora Lee


## Getting in touch
