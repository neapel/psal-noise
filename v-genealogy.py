#!/usr/bin/env python
from visualize import *

def genealogy(name):
	n = 150
	pop = list({} for _ in range(n + 1))
	elite_threshold = []
	poor_threshold = []
	for i, g in zip(range(n + 1), read_pop(name, ALL)):
		for j, r in enumerate(g):
			pop[i][r[0]] = (i + jitter(), r[1], j)
		elite_threshold.append(g[ELITE - 1][1])
		poor_threshold.append(g[ALL//2][1])

	old_elite = []
	new_elite = []
	rest = []
	for i, g in zip(range(n), read_gen(name)):
		for k, v in g.items():
			child = pop[i + 1].get(k, None)
			if child:
				if len(v) == 1:
					old_elite.append(child)
				elif child[2] < ELITE:
					new_elite.append(child)
				else:
					rest.append(child)
					#for p in v:
					#	parent = pop.get((i, p), None)
					#	if parent:
					#		lines.append( parent + child )

	rest = rest + new_elite
	new_elite = []

	print 'reset'
	print 'set key left top samplen 1'
	print 'unset border'
	print 'unset ytics'
	print 'set xtics scale 0 font ",8"'
	print 'set xrange [0.51:{0}]'.format(n + 0.49)
	print 'plot ',
	print '"-" w p pt 5 ps 0.05 lc rgbcolor "#808080" t "Normale", ',
	print '"-" w histeps lc rgbcolor "black" t "Elitegrenze", ',
	print '"-" w histeps lc rgbcolor "black" t "Median", ',
	print '"-" w p pt 5 ps 0.3 lc rgbcolor "red" t "Alte Elite", ',
	print '"-" w p pt 5 ps 0.2 lc rgbcolor "blue" t "Neu in Elite" '
	for x, y, _ in rest: print x, y
	print 'e'
	for y in elite_threshold: print y
	print 'e'
	for y in poor_threshold: print y
	print 'e'
	for x, y, _ in old_elite: print x, y
	print 'e'
	for x, y, _ in new_elite: print x, y
	print 'e'

if __name__ == '__main__':
	genealogy(*sys.argv[1:])
