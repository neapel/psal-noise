#!/usr/bin/env python
# encoding=utf-8
from __future__ import division
from visualize import *

def parenthood(name):
	ELITE = 0
	n = 7
	START = 0
	END = START + n
	pop = list({} for _ in range(END + 2))
	for i, g in zip(range(END + 2), read_pop(name, ALL)):
		for j, r in enumerate(g):
			pop[i][r[0]] = (i + (j % 10 - 5)*0.01, r[1], j)
			#jitter(8)

	elite_lines = []
	mate_lines = []
	mutate_lines = []
	for i, g in zip(range(END + 1), read_gen(name)):
		for k, v in g.items():
			child = pop[i + 1].get(k, None)
			if child:
				parents = map(lambda x: pop[i][x], v[1:])
				if v[0] == 'e':
					elite_lines.append(child + parents[0])
				elif v[0] == 'c':
					if child[2] < ELITE:
						for p in parents:
							mate_lines.append(child + p)
				elif v[0] == 'm':
					if child[2] < ELITE:
						mutate_lines.append(child + parents[0])

	print r'''
		reset
		set key left top samplen 0.5
		unset border
		unset ytics
		set xtics scale 0
		set xrange [{0}-0.25:{1}+0.25]
		set yrange [0:*]
		set xlabel "Generation"
		set ylabel "Fitness →"
		set style line 1 lw 1 lc rgbcolor "#0000ee"
		set style line 3 lw 1 lc rgbcolor "#00ee00"
		set style line 2 lw 1 lc rgbcolor "#ee0000"

		plot \
			"-" w l ls 3 t "Mutiert", \
			"-" w l ls 1 t "Crossover", \
			"-" w l ls 2 t "Kopiert", \
			"-" w p pt 6 ps 0.4 lc rgbcolor "black" notitle
	'''.format(START, END)

	def lines(l):
		for x1, y1, _, x2, y2, _ in l:
			print x1, y1, '\n', x2, y2, '\n'
		print 'e'
	lines(mutate_lines)
	lines(mate_lines)
	lines(elite_lines)
	for gen in pop:
		for x, y, _ in gen.values(): print x, y
	print 'e'

if __name__ == '__main__':
	parenthood(*sys.argv[1:])
