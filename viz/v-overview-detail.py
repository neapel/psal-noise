#!/usr/bin/env python
# encoding=utf-8
from __future__ import division
from visualize import *

def overview(name):
	pop = array(map(lambda x: map(itemgetter(1), x), read_pop(name, ALL, 51)))
	elite = pop[:,:ELITE]
	elite_mean = list(mean(elite, 1))
	smooth_mean = elite_mean

	upper = max(smooth_mean) * 1.75

	print '''
		reset
		unset key

		set ytics border nomirror out
		set ylabel '$\overline F$'
		set xtics 10 border nomirror out
		set mxtics 10
		set xlabel "Generation"

		set logscale y
		set border 3

		set yrange [0.1:100]
		set xrange [-0.5:{1} + 0.5]
		set x2range [-0.5:{1} + 0.5]

		set x2tics -0.5, 1 out nomirror scale 0 format ""
		set style line 3 lc rgbcolor "#dddddd"
		set grid x2 ls 3

		set style line 1 lw 2 lc rgbcolor "red"
		set style line 2 pt 7 ps 0.05 lc rgbcolor "black"

		plot "-" w p ls 2, "-" w l ls 1
	'''.format(upper, len(pop)-1)

	for l in range(0, 160, 20):
		h = l + 20
		for i, gen in enumerate(pop[:,l:h]):
			for j, x in enumerate(gen): print jitter(i,j), x
	print 'e'

	print '\n'.join(map(str, smooth_mean)), '\ne'



if __name__ == '__main__':
	overview(*sys.argv[1:])
