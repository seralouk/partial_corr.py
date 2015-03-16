#!/usr/bin/env python
from sys import stdin, stderr
from optparse import OptionParser
import numpy as np
from scipy import stats, linalg


"""
Partial Correlation in Python (clone of Matlab's partialcorr)

This uses the linear regression approach to compute the partial 
correlation (might be slow for a huge number of variables). The 
algorithm is detailed here:

    http://en.wikipedia.org/wiki/Partial_correlation#Using_linear_regression

Taking X and Y two variables of interest and Z the matrix with all the variable minus {X, Y},
the algorithm can be summarized as

    1) perform a normal linear least-squares regression with X as the target and Z as the predictor
    2) calculate the residuals in Step #1
    3) perform a normal linear least-squares regression with Y as the target and Z as the predictor
    4) calculate the residuals in Step #3
    5) calculate the correlation coefficient between the residuals from Steps #2 and #4; 

    The result is the partial correlation between X and Y while controlling for the effect of Z


Date: Nov 2014
Author: Fabian Pedregosa-Izquierdo, f@bianp.net
Testing: Valentina Borghesani, valentinaborghesani@gmail.com

Date: March 2015:
Modified by: Ivan Molineris, ivan.molineris@gmail.com
"""


def partial_corr(C):
    """
    Returns the sample linear partial correlation coefficients between pairs of variables in C, controlling 
    for the remaining variables in C.


    Parameters
    ----------
    C : array-like, shape (n, p)
        Array with the different variables. Each column of C is taken as a variable


    Returns
    -------
    P : array-like, shape (p, p)
        P[i, j] contains the partial correlation of C[:, i] and C[:, j] controlling
        for the remaining variables in C.
    """
    
    C = np.asarray(C)
    p = C.shape[1]
    P_corr = np.zeros((p, p), dtype=np.float)
    for i in range(p):
        P_corr[i, i] = 1
        for j in range(i+1, p):
            idx = np.ones(p, dtype=np.bool)
            idx[i] = False
            idx[j] = False
            beta_i = linalg.lstsq(C[:, idx], C[:, j])[0]
            beta_j = linalg.lstsq(C[:, idx], C[:, i])[0]

            res_j = C[:, j] - C[:, idx].dot( beta_i)
            res_i = C[:, i] - C[:, idx].dot(beta_j)
            
            corr = stats.pearsonr(res_i, res_j)[0]
            P_corr[i, j] = corr
            P_corr[j, i] = corr
        
    return P_corr



def main():
	usage = '''%prog < STDIN
Returns the sample linear partial correlation coefficients between pairs of rows in the STDIN, controlling 
for the remaining variables in STDIN.

The first column of each row of the input matrix is intended as row_id
	'''
	parser = OptionParser(usage=usage)
	
	options, args = parser.parse_args()
	
	if len(args) != 0:
		exit('Unexpected argument number.')
	
	cols_len=None
	matrix=[]
	row_ids=[]
	for line in stdin:
		cols = line.rstrip().split('\t')
		row_ids.append(cols.pop(0))
		cols = [float(c) for c in cols]
		if cols_len is None:
			cols_len = len(cols)
		assert cols_len == len(cols)
		matrix.append(cols)
	
    	matrix = np.asarray(matrix)
	matrix = matrix.T
	C=partial_corr(matrix)
	for i,k in enumerate(row_ids):
		for j,l in enumerate(row_ids):
			if j>i:
				print row_ids[i], row_ids[j], C[i,j]

if __name__ == '__main__':
	main()
