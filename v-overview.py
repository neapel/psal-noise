#!/usr/bin/env python
from __future__ import division
from visualize import *

def overview(name):

	pop = array(map(lambda x: map(itemgetter(1), x), read_pop(name, ALL)))
	elite = pop[:,:ELITE]
	elite_mean = list(mean(elite, 1))
	smooth_mean = smooth(elite_mean, 1+2*10)

	upper = max(smooth_mean) * 2

	print '''
		reset
		unset key
		set style line 1 pt 7 ps 0.3 lw 2 lc rgbcolor "red" # mean
		set style line 2 lc rgbcolor "#606060"
		set style line 3 pt 7 ps 0.15 lc rgbcolor "black"
		set style line 4 pt 7 ps 0.05 lc rgbcolor "gray"
		set style line 5 pt 7 ps 0.1 lc rgbcolor "blue"
		set style line 6 lw 1 lc rgbcolor "green" # median

		set ytics border nomirror out font ",10"
		set ylabel "Fitness" font ",10"

		set xtics border nomirror out font ",10"
		set mxtics 5
		set xlabel "Generation" font ",10"

		set border 0 ls 2

		set yrange [0:{0}]
		set xrange [-0.5:{1} + 0.5]

		plot \
			"-" w p ls 4 t "Population", \
			"-" w p ls 5 t "Outlier", \
			"-" w p ls 3 t "Elite", \
			"-" w p ls 1 notitle, \
			"-" w l ls 1 t "Elite-Mittelwert"
	'''.format(upper, len(pop) - 2)

	for i, gen in enumerate(pop[:,ELITE:]): # normal
		for x in gen: print i + jitter(), x
	print 'e'

	for i, gen in enumerate(pop): # outlier
		for x in gen:
			if x > upper:
				print i + jitter(), upper
	print 'e'

	for i, gen in enumerate(elite): # elite
		for x in gen: print i + jitter(), x
	print 'e'

	print '\n'.join(map(str, elite_mean)), '\ne'
	print '\n'.join(map(str, smooth_mean)), '\ne'



if __name__ == '__main__':
	overview(*sys.argv[1:])
