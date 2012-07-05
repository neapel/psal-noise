#!/usr/bin/env python
from visualize import *

def one_pop(name):
	pop_whole = filter(lambda x: x[1] > 1, read_last_pop(name, ALL))
	pop = map(lambda x: x[2:], pop_whole)
	pop_a = map(lambda x: x[1], pop_whole)
	s = range(len(pop[0]))
	print 'reset'
	print 'unset border'
	print 'unset key'
	print 'set yrange [0:*]'
	print 'set xrange [-1:*]'
	print 'set bmargin 10'
	print 'unset xtics'
	print 'set ytics scale 0'
	print 'set encoding utf8'
	print 'set xtics scale 0 rotate by -90 offset -0.5,-0.5 font "Monospace,5" ("" 0)'
	for x, l in enumerate(pop_whole):
		print 'set xtics add ("%s" %d)' % (binstring(l[0]), x) 
	print 'plot ',
	print '"-" volatile w impulses lc rgbcolor "gray", ',
	for i in s:
		print '"-" volatile w p pt %d lc rgbcolor "black", ' % (i + 1,),
	print '"-" volatile w p pt 1 lw 2 lc rgbcolor "red" '
	for x in map(max, pop): print x
	print 'e'
	for i in s:
		for l in pop: print l[i]
		print 'e'
	for x in pop_a: print x
	print 'e'

if __name__ == '__main__':
	one_pop(*sys.argv[1:])
