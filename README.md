# PyOptionTree

PyOptionTree is a package desgined for implementing lattice models for option pricing.
The objective of this package is to provide an intuitive and easy-to-implement open-source tool for students, academics and practioners to run theoretical pricing of
various simple and exotic options. It is based on the Cox-Ross-Rubenstein market model, published by Cox et al in their 1979 paper "Option Pricing: A Simplified Approach".

The motivation behind creating an open-source python package for the Option Tree Pricing Model is that not only could the tree model be a viable method for deriving prices of path-dependent options, there is generally a gap in this area, as compared to the more popular Monte Carlo approach and the Finite Element Difference method, to be filled. In addition, there are many interesting papers exploring the use of a Tree model to price exotics. We aim to create packages based on those research, to create a useful tool that could help bring those methods to practice.

Version: v0.0.1

## Theory

### Binomial Tree Model
Cox et al. introduced an elegant yet simple model for the option pricing. First of all, the underlying asset price is assumed to follow a multiplicative binomial process over a discrete time periods. The price at the next period takes on two possible values, an "up" price in which the rate of return is positve, with a value of $u - 1$, and a "down" price whereby underlying asset has a negative rate of return of $d - 1$. 

## Features

### Underlying Asset Price Tree
In all tree models, the first step to solving for the option price is to evaluate the price dynamics of the underlying asset over time.
