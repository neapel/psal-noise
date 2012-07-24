#!/usr/bin/env python
from __future__ import division
from visualize import *

def one_pop(name, index = -1, do_median=True, do_mean=True):
	index = int(index)

	that_pop = read_this_pop(name, index, ALL) if index >= 0 else read_last_pop(name, ALL)
	# better half only, rest is boring
	pop_whole = that_pop[:ALL//2]
	pop = map(lambda x: x[2:], pop_whole)
	s = range(len(pop[0]))

	print '''
		reset
		unset border
		set key right top samplen 1 horizontal
		set yrange [0:*]
		set xrange [-0.49:{0} + 0.49]
		set lmargin 9
		set bmargin 10
		set ylabel "Fitness" font ",10"
		unset xtics
		set ytics scale 0
		set encoding utf8

		set style line 2 lt 1 lw 2 lc rgbcolor "green" # median
		set style line 3 lt 1 lw 2 lc rgbcolor "red" # mean

		set label 1000 "Regeln" right rotate by 90 at first 0, first 0 offset -7,-4 font ",10"
	'''.format(len(pop) - 1)
	
	for x, l in enumerate(pop_whole):
		print 'set label {0} "{1}" right rotate by 90 at first {2}, first 0 offset 0.0,-0.5 font "Monospace,6"'.format(x+1, binstring(l[0]), x)

	print 'plot ',
	print '"-" w impulses lc rgbcolor "gray" notitle, ',
	if do_median:
		print '"-" w histeps ls 2 t "Median", ',
	if do_mean:
		print '"-" w histeps ls 3 t "Mean", ',

	print ','.join([
		'"-" w p pt {0} lc rgbcolor "black" t "Lauf {0}"'.format(i + 1)
		for i in s])

	print '\n'.join([str(max(l)) for l in pop]), '\ne'
	if do_median: print '\n'.join([str(median(l)) for l in pop]), '\ne'
	if do_mean: print '\n'.join([str(mean(l)) for l in pop]), '\ne'

	for i in s:
		for l in pop: print l[i]
		print 'e'


if __name__ == '__main__':
	one_pop(*sys.argv[1:])
