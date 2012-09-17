#!/usr/bin/env python
# encoding=utf-8
from __future__ import division
from visualize import *
from math import log

def spectrum(*rules):
	print '''
		reset
		set logscale xyx2
		#set yrange [ 10**-4 :10**1 ]
		set xrange [1:1500]
		set xtics out nomirror format "$10^{%T}$"
		set ytics out nomirror format "$10^{%T}$"
		set mxtics 10
		set mytics 10

		set xlabel "$f$"
		set ylabel "$S(f)$"

		set border 3
		set key samplen 0.5 reverse Left at graph 0.8,graph 1 spacing 1.2
		set style fill transparent solid 0.125
		set style line 2 pt 5 ps 0.04 lc rgbcolor "black" # dots
		set style line 3 lw 2 lc rgbcolor "red" # fit
		set style line 4 lw 1 lc rgbcolor "gray" # ref
	'''

	print 'set multiplot layout {0},1'.format(len(rules))

	dens = [0.001, 0.01, 0.1, 0.5]

	for rule in rules:

		print 'plot', ','.join([
			r''' "-" using ($0 + 1):1 w l lc rgbcolor "{1}" t '$p(\1)={0}$' '''.format(i, C_MD[c])
			for i, c in zip(dens, C_IN)
		])

		for i in dens:
			data = zeros(1500)
			avg = 6
			for k in range(avg):
				_, _, _, d = one_spectrum(easyrule(rule), seed=123 + k, density=i)
				data += array(map(float, d[:1500]))
			data /= avg
			print '\n'.join(map(str, data))
			print 'e'
	
	print 'unset multiplot'

if __name__ == '__main__':
	spectrum(*sys.argv[1:])
