#!/usr/bin/env python
# encoding=utf-8
from __future__ import division
from visualize import *

def weighted_avg_and_std(values, weights):
    """
	 <http://stackoverflow.com/a/2415343/535522>
    Returns the weighted average and standard deviation.

    values, weights -- Numpy ndarrays with the same shape.
    """
    av = average(values, weights=weights)
    variance = dot(weights, (values - av)**2) / weights.sum()
    return (av, sqrt(variance))

def lambda_hist(*names):
	print r'''
		reset
		unset key
		set palette defined (0 "white", 0.25 "#729fcf", 0.5 "#cc0000", 1 "#fce94f")
		unset colorbox
		set cbrange [0:1]
		set border 3

		set yrange [-0.5:31.5]
		set xrange [-0.5:199+0.5]
		set xlabel 'Generation'
		set ylabel '$\overline\lambda$' offset 3,0
		set xtics 10 out nomirror format '[c]{{%.0f}}'
		set mxtics 10
		set ytics 4 out nomirror format '\sfrac{{%.0f}}{{32}}'
		set mytics 4

		set style fill transparent solid 0.2
		set style line 1 lw 2 lc rgbcolor "#000000"
	'''.format(len(names))

	print 'plot', ','.join([
		'"-" w l ls 1'
		for n in names
	])

	GENS = 200

	numbers = range(33)
	for name in names:
		avgl = zeros(GENS)
		std = zeros(GENS)
		for i, pop in zip(range(GENS), read_pop(name, ALL)):
			lambdas = zeros(33)
			for k in pop:
				lambdas[k[0].count('1')] += 1
			avgl[i], std[i] = weighted_avg_and_std(numbers, lambdas)

		for x, e in zip(avgl, std):
			print x
		print 'e'


if __name__ == '__main__':
	lambda_hist(*sys.argv[1:])

