#!/usr/bin/env python
from visualize import *

def lambda_hist(*names):
	lambdas = [0] * 32
	for name in names:
		for indiv in read_this_pop(name, 200, 10):
			lambdas[indiv[0].count('1')] += 1
	paper_lambdas = [ 0,  0,  0,  0,  0,  0,  0,  0,
	                  0,  0,  2, 16, 21, 37, 39, 31,
						  31, 15,  6,  2,  0,  0,  0,  0,
							0,  0,  0,  0,  0,  0,  0,  0]
	print 'reset'
	print 'unset key'
	print 'set xrange [0:32]'
	print 'set yrange [0:*]'
	print 'set border 1'
	print 'unset ytics'
	print 'set xtics out nomirror format "%.0f" 1'
	print 'set boxwidth 0.8'
	print 'set style fill solid 1 noborder'
	print 'set style data histograms'
	print 'set style histogram cluster gap 1'
	print 'plot "-" volatile using 1, "-" volatile using 1'
	for x in lambdas: print x
	print 'e'
	for x in paper_lambdas: print x
	print 'e'

if __name__ == '__main__':
	lambda_hist(*sys.argv[1:])
