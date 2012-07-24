#!/usr/bin/env python
# encoding=utf-8
from __future__ import division
from visualize import *

def parenthood(name):
	n = 7
	pop = list({} for _ in range(n + 1))
	for i, g in zip(range(n + 1), read_pop(name, ALL)):
		for j, r in enumerate(g):
			pop[i][r[0]] = (i + jitter(8), r[1], j)

	super_elite_lines = []
	super_mate_lines = []
	super_mutate_lines = []
	elite_lines = []
	mate_lines = []
	mutate_lines = []
	for i, g in zip(range(n), read_gen(name)):
		for k, v in g.items():
			child = pop[i + 1].get(k, None)
			if child:
				parents = map(lambda x: pop[i][x], v[1:])
				appto = {'e': super_elite_lines, 'c': super_mate_lines, 'm': super_mutate_lines} if child[2] == 0 \
						else {'e': elite_lines, 'c': mate_lines, 'm': mutate_lines}
				for p in parents:
					appto[v[0]].append( child + p )

	print r'''
		reset
		set key left top samplen 1
		unset border
		unset ytics
		set xtics scale 0 font ",10"
		set xrange [-0.25:{0}+0.25]
		set yrange [0:*]
		set xlabel "Generation" font ",10"
		set ylabel "Fitness →" font ",10"
		set style line 1 lw 0.25 lc rgbcolor "#0000ee"
		set style line 3 lw 0.25 lc rgbcolor "#00ee00"
		set style line 2 lw 0.75 lc rgbcolor "#ee0000"

		plot \
			"-" w l ls 3 notitle, \
			"-" w l ls 1 notitle, \
			"-" w l ls 2 notitle, \
			"-" w l ls 3 lw 2 t "Mutiert", \
			"-" w l ls 1 lw 2 t "Crossover", \
			"-" w l ls 2 lw 2 t "Kopiert", \
			"-" w p pt 6 ps 0.4 lc rgbcolor "black" notitle
	'''.format(n)

	def lines(l):
		for x1, y1, _, x2, y2, _ in l:
			print x1, y1, '\n', x2, y2, '\n'
		print 'e'
	lines(mutate_lines)
	lines(mate_lines)
	lines(elite_lines)
	lines(super_mutate_lines)
	lines(super_mate_lines)
	lines(super_elite_lines)
	for gen in pop:
		for x, y, _ in gen.values(): print x, y
	print 'e'

if __name__ == '__main__':
	parenthood(*sys.argv[1:])
