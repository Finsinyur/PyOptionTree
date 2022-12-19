# -*- coding: utf-8 -*-
"""
Created on Tue Dec 20 00:17:09 2022

@author: leeca
"""

import networkx as nx
import matplotlib.pyplot as plt

def visualize_tree(tree, plot_title = 'Binomial Tree'):
    r"""
    Function to visualize binomial tree model, in order to translate matrix into 
    something user-friendly.
    
    :param tree: The binomial tree, presented in a matrix.
    :type tree: np.ndarray
    :param plot_title: User-defined plot title.
    :type tree: Str.

    :return: None

    """
    
    # Determine the number of time periods, excluding 0
    N = len(tree) - 1
    
    # Define figure size. Min. size is 8 by 8.
    if N < 8:
        plt.figure(figsize = (8,8))
    else:
        plt.figure(figsize = (N,N))
    
    # Insert Plot title
    plt.title(plot_title)
    
    # Initialize Networkx Graph
    G=nx.Graph()
    
    # Iterate across time periods, from i = 0 till i = N-1
    for i in range(0,N):
        
        # Iterate across states, from state j = 1 to j = i+1
        for j in range(1,i+2):
            
            G.add_edge((i,j),(i+1,j)) # add an "up" branch
            G.add_edge((i,j),(i+1,j+1)) # add a "down" branch

    position={} #dictionary with nodes position
    
    # Realigning the position of the nodes, with the centre being the middle state of the last period
    for node in G.nodes():
        position[node]=(node[0],N+2+node[0]-2*node[1])
    
    # Plot network graph
    nx.draw(G, position)
    
    # Insert X-axis label
    plt.text(-1, -1, s = "Period N")
    
    # Insert prices to each node
    for j in range(N+1):
        for i in range(j+1):
            x, y = position[(j, i+1)]
            plt.text(x-0.25, y + 0.5, s = '${:.2f}'.format(tree[i,j]))
        plt.text(x, - 1, s = x)
            
    plt.show()
            
            
        