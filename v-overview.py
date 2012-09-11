#!/usr/bin/env python
# encoding=utf-8
from __future__ import division
from visualize import *

def overview(name):
	elite = array(map(lambda x: map(itemgetter(1), x), read_pop(name, ELITE))) + 1
	elite_mean = list(mean(elite, 1))
	smooth_mean = smooth(elite_mean, 1+2*4)

	upper = max(smooth_mean) * 1.75

	print '''
		reset
		set key top left vertical reverse Left samplen 0.5

		set ytics border nomirror out
		set ylabel '$\overline F$'
		set xtics 10 border nomirror out
		set mxtics 10
		set xlabel "Generation"

		set border 0
		set yrange [0:{0}]
		set xrange [-0.5:{1} + 0.5]

		set style line 1 lw 2 lc rgbcolor "red"
		set style line 2 pt 7 ps 0.05 lc rgbcolor "black"

		plot "-" w p ls 2 t "Elite", "-" w l ls 1 t "Mittelwert (geglättet)"
	'''.format(upper, len(elite) - 1)

	for i, gen in enumerate(elite):
		for j, x in enumerate(gen): print i, x
	print 'e'

	print '\n'.join(map(str, smooth_mean)), '\ne'



if __name__ == '__main__':
	overview(*sys.argv[1:])
