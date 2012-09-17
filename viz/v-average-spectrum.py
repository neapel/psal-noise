#!/usr/bin/env python
# encoding=utf-8
from __future__ import division
from visualize import *

def spectrum(rule, samples = 5):
	rule = easyrule(rule)
	samples = int(samples)

	data = zeros((samples, 1500))
	for i in range(samples):
		data[i] = array(map(float, one_spectrum(rule, seed=123 + i)[3][:1500]))
	
	datas = '\n'.join([
		' '.join(map(str,x))
		for x in zip(mean(data, axis=0), std(data, axis=0))
	]) + '\ne\n'

	
	print r'''
		reset
		set logscale xy
		set xtics out nomirror format "$10^{%T}$" offset 0,0.125
		set ytics out nomirror format "$10^{%T}$" offset 0.75,0
		set mxtics 10
		set mytics 10

		set lmargin 5
		set rmargin 0.5
		set tmargin 0.5
		set bmargin 2

		set yrange [10**-3:10**1]
		set xrange [1:1500]

		set xlabel "$f$" offset 0,1.25

		set border 3
		set key center top reverse Left samplen 0.5 spacing 1.5

		set style line 2 lw 0.5 pt 5 ps 0.04 lc rgbcolor "black" # dots
		set style line 3 lw 1 lc rgbcolor "red" # fit
		set style line 4 lw 1 lc rgbcolor "gray" # ref

		plot \
			"-" u ($0 + 1):($1 - $2):($1 + $2) \
				w filledcurves lc rgbcolor "#cce5ff" \
				t '$\sigma\bigl(\overline S(f)\bigr)$', \
			"-" u ($0 + 1):1 w l lw 2 lc rgbcolor "black" t '$\overline S(f)$'
	'''
	print datas, datas


if __name__ == '__main__':
	spectrum(*sys.argv[1:])

