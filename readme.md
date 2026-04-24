# **MIN SUPERSET PDP**

## **Problem Goal**
The objective is to construct the smallest possible set P, such that every element of the multiset D can be represented as an absolute difference between two elements of P.

## **Instance**
A multiset of positive integers: 

$$D = \{d_1, d_2, \dots, d_k\}$$

## **Solution**

A set of non-negative integers:

$$P = \{p_1, p_2, \dots, p_m\}$$
Such that:
1.  **Coverage:** Every distance in $D$ is represented by at least one pair of points in $P$. 
    $$D \subseteq \{|p_i - p_j| : 1 \leq i < j \leq m\}$$
2.  **Optimality:** The number of points $m$ is **minimized**.

