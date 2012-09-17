#!/usr/bin/env python
# encoding=utf-8
from __future__ import division
from visualize import *
from math import log

def spectrum(rule, seed):
	rule = easyrule(rule)
	seed = int(seed)

	fit, alpha, beta, data = one_spectrum(rule, seed=seed)

	fb = 100
	sigma = sum([
		(log(float(data[f])) - (alpha + beta * log(f + 1.0)))**2
		for f in range(fb)
	]) / fb

	print r'''
		reset
		set logscale xyx2
		set yrange [ 10**-4 :10**1 ]
		set xrange [1:1500]
		set x2range [1:1500]
		set mxtics 10
		set mytics 10

		set border 3
		unset key
		set style fill transparent solid 0.25
		set style line 2 lw 1 lc rgbcolor "black" # dots
		set style line 3 lw 2 lc rgbcolor "red" # fit

		set lmargin 1
		set rmargin 1
		set bmargin 1
		set tmargin 2
		set xtics nomirror out format ""
		set ytics nomirror out format ""

		set x2tics scale 0 format "" (10, 100)
		set style line 8 lt 1 lc rgbcolor "gray"
		set grid x2 ls 8

		set title '\shortstack{{$\beta=\num{{{1:.2f}}}\quad \sigma^2=\num{{{2:.2g}}}$\\\normalsize $F=\num{{{3:.2f}}}$}}'

		plot \
			'-' w filledcurves ls 3, \
			exp({0}) * x**{1} w l ls 3, \
			'-' using ($0 + 1):1 w l ls 2
	'''.format(alpha, beta, sigma, fit)
	
	for x, y in enumerate(data[:100], 1):
		print x, y, exp(alpha + beta * log(x))
	print 'e'
	print '\n'.join(data)
	print 'e'


if __name__ == '__main__':
	spectrum(*sys.argv[1:])
