#!/usr/bin/env python
# encoding=utf-8
from __future__ import division
from visualize import *

def spectrum(rule, line=True, fitness=True, width=1, height=1):
	width=int(width)
	height=int(height)
	line=bool(int(line))
	fitness=bool(int(fitness))
	rule = easyrule(rule)

	print '''
		reset
		set logscale xyx2
		set yrange [10**-5:10**2]
		set xrange [1:1500]
		set x2range [1:1500]
		set xtics out nomirror format "10^{%T}" font ",10"
		set ytics out nomirror format "10^{%T}" font ",10"
		set mxtics 10
		set mytics 10

		set xlabel "f" font ",10"
		set ylabel "S(f)" font ",10"

		#set lmargin 5
		#set rmargin 1
		#set bmargin 2
		set border 3
		unset key
		set style fill solid 0.125
		set style line 2 pt 7 ps 0.4 lc rgbcolor "black"
	'''

	if width * height > 1:
		print '''
			unset xlabel
			unset ylabel
			set xtics format ""
			set ytics format ""
			set style line 2 ps 0.25
		'''

	if line:
		print '''
			set x2tics scale 0 format "" (10, 100)
			set style line 8 lt 1 lc rgbcolor "gray"
			set grid x2 ls 8
		'''

	print 'set multiplot layout {0},{1}'.format(width, height)

	datas = sorted([one_spectrum(rule, 123 + i) for i in range(width * height)], key=itemgetter(0))


	for fit, alpha, beta, data in datas:
		if line:
			lx = 10
			ly = exp(alpha + beta * log(lx))
			if fitness:
				text =r'β={1:.2f}\nF={2:.2f}'
				opts = 'noenhanced offset 1,2'
			else:
				text = r'e^{{{0:.2f}}} f^{{{1:.2f}}}'
				opts = 'offset 1,1'
			print r'set label 1 "{0}" {1} at first {2}, first {3} textcolor rgbcolor "red" front font ",{4}"'.format(
				text.format(alpha, beta, fit).replace('-', '−'), opts, lx, ly, 16 if len(datas) == 1 else 12)

		print 'plot ',
		if line:
			print '"-" volatile w filledcu lc rgbcolor "red", ',
			print r'exp({0} + {1} * log(x)) w l lw 2 lc rgbcolor "red", '.format(alpha, beta),
		print '"-" volatile using ($0 + 1):1 w p ls 2'
		if line:
			for x, y in enumerate(data[:100], 1):
				print x, y, exp(alpha + beta * log(x))
			print 'e'
		print '\n'.join(data)
		print 'e'

	print 'unset multiplot'

if __name__ == '__main__':
	spectrum(*sys.argv[1:])
