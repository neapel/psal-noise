#!/usr/bin/env python
from __future__ import division
from visualize import *
import re

def averages(*names):
	items = []
	for i, name in enumerate(names, 1):
		pop = array(map(lambda x: map(itemgetter(1), x), read_pop(name)))
		pop_mean = list(mean(pop, 1))
		smooth_mean = smooth(pop_mean, 1+2*10)
		name = re.search('\d+', name).group(0)
		items.append((i, name, pop_mean, smooth_mean))

	top = max([
		max(s[:200])
		for _, _, _, s in items
	])

	print '''
		reset
		unset key
		unset colorbox
		set palette rgb 33,13,10
		unset border
		set yrange [0:* < {0}]
		set xrange [0:200]
		set xtics 50 nomirror out font ",10"
		set mxtics 5
		set ytics nomirror out font ",10"
		set xlabel "Generation" font ",10"
		set ylabel "Fitness" font ",10"
		set lmargin 10

		set style line 1 pt 7 ps 0.4
		set style line 2 lw 2
	'''.format(top * 1.1)

	if False:
		for i, name, _, s in items:
			print 'set label {0} "{1}" at first {2}, first {3}'.format(i, name, len(s), s[-1])

	print 'plot ', ','.join([
		('"-" w p ls 1 lc palette frac {0} notitle, '
		+ '"-" w l ls 2 lc palette frac {0} notitle').format(i/len(names))
		for i, name, _, _ in items
	])

	for _, _, m, s in items:
		print '\n'.join(map(str, m)), '\ne'
		print '\n'.join(map(str, s)), '\ne'

if __name__ == '__main__':
	averages(*sys.argv[1:])
