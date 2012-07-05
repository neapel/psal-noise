#!/usr/bin/env python
from visualize import *

def overview(name):
	pop = array(map(lambda x: map(itemgetter(1), x), read_pop(name, ALL)))
	elite = pop[:,:ELITE]
	elite_mean = list(mean(elite, 1))
	smooth_mean = smooth(elite_mean, 1+2*5)
	print 'reset'
	print 'set title "{0}"'.format(name)
	print 'unset key'
	print 'set style line 1 pt 5 ps 0.2 lw 2 lc rgbcolor "red"'
	print 'set style line 2 lc rgbcolor "#606060"'
	print 'set style line 3 pt 5 ps 0.1 lc rgbcolor "black"'
	print 'set style line 4 pt 5 ps 0.05 lc rgbcolor "gray"'
	print 'set xtics border nomirror out 50 offset 0,0.25 font "Sans, 8"'
	print 'set mxtics 5'
	print 'unset ytics'
	print 'set border 0 ls 2'
	print 'set rmargin 5'
	print 'set xrange [0:*]; set yrange [0:*]'
	print 'set label 1 "{0:.0f}" at {1},{0} '.format(smooth_mean[-1], len(smooth_mean)),
	print '  nopoint offset 0.25,0 textcolor ls 1 font "Sans Bold, 10"'
	print 'plot ',
	print '"-" volatile w p ls 4, ',
	print '"-" volatile w p ls 3, ',
	print '"-" volatile w p ls 1, ',
	print '"-" volatile w l ls 1'
	for i, gen in enumerate(pop[:,ELITE:]): # normal
		for x in gen: print i + jitter(), x
	print 'e'
	for i, gen in enumerate(elite): # elite
		for x in gen: print i + jitter(), x
	print 'e'
	for p in elite_mean: print p
	print 'e'
	for p in smooth_mean: print p
	print 'e'

if __name__ == '__main__':
	overview(*sys.argv[1:])
