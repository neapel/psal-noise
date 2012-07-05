#!/usr/bin/env python
from visualize import *

def spectrum(rule, line=True, width=1, height=1):
	width=int(width)
	height=int(height)
	line=bool(int(line))

	print 'reset'
	print 'set termoption enhanced'
	print 'set logscale xyx2'
	print 'set yrange [0.0001:100]'
	print 'set xrange [1:1500]'
	print 'set x2range [1:1500]'
	print 'set xtics out nomirror format "$10^{%T}$"'
	print 'set ytics out nomirror format "$10^{%T}$"'
	print 'set mxtics 10'
	print 'set mytics 10'

	print 'set lmargin 6'
	print 'set rmargin 1'
	print 'set bmargin 2'

	if line:
		print 'set x2tics scale 0 format "" (10, 100)'
		print 'set style line 8 lt 1 lc rgbcolor "gray"'
		print 'set grid x2 ls 8'

	print 'set border 3'
	print 'unset key'
	print 'set style fill solid 0.125'

	print 'set multiplot layout {0},{1}'.format(width, height)

	for i in range(width * height):
		fit, alpha, beta, data = one_spectrum(rule)
		if line:
			lx = 10
			ly = exp(alpha + beta * log(lx))
			print r'set label 1 "$\\mathrm{{e}}^{{{0:.2f}}} \\, f^{{{1:.2f}}}$" at first {2}, first {3} textcolor rgbcolor "red" front offset 1,1'.format(alpha, beta, lx, ly)

		print 'plot ',
		if line:
			print '"-" volatile w filledcu lc rgbcolor "red", ',
			print r'exp({0} + {1} * log(x)) w l lw 3 lc rgbcolor "red", '.format(alpha, beta),
		print '"-" volatile using ($0 + 1):1 w p pt 5 ps 0.4 lc rgbcolor "black"'
		if line:
			for x, y in enumerate(data[:100], 1):
				print x, y, exp(alpha + beta * log(x)) 
			print 'e'
		print '\n'.join(data)
		print 'e'

	print 'unset multiplot'

if __name__ == '__main__':
	spectrum(*sys.argv[1:])
