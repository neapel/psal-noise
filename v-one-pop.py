#!/usr/bin/env python
from __future__ import division
from visualize import *

def one_pop(name):
	pop = map(lambda x: x[2:], read_last_pop(name, ALL))
	s = range(len(pop[0]))

	print r'''
		reset
		unset border
		set key right top reverse Left samplen 0.5 vertical spacing 1.2
		set yrange [0:*]
		set xrange [-0.49:{0} + 0.49]
		set ylabel '$F$' offset 1,0
		unset xtics
		set ytics scale 0

		set style line 3 lt 1 lw 4 lc rgbcolor "red" # mean

		plot \
			'-' w impulses lc rgbcolor "gray" notitle, \
			'-' w l lw 4 lc rgbcolor "red" t '$\overline F$', \
			{1}
	'''.format(len(pop) - 1, ','.join([
		'"-" w p pt {0} ps 0.35 lc rgbcolor "black" t "$x^0:{0}$"'.format(i + 1)
		for i in s]))
	
	print '\n'.join([str(max(l)) for l in pop]), '\ne'
	print '\n'.join([str(mean(l)) for l in pop]), '\ne'

	for i in s:
		for l in pop: print l[i]
		print 'e'


if __name__ == '__main__':
	one_pop(*sys.argv[1:])
