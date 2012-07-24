#!/usr/bin/env python
# encoding=utf-8
from __future__ import division
from visualize import *

def new(name):
	GENS = 200
	seen = set()
	new = list([[] for _ in range(GENS)])
	old = list([[] for _ in range(GENS)])
	for i, pop in zip(range(GENS),read_pop(name, ALL)):
		for j, r in enumerate(pop):
			if r[0] in seen:
				old[i].append((j,r[1]))
			else:
				new[i].append((j,r[1]))
				seen.add(r[0])

	is_elite = lambda x: x[0] < ELITE

	new_f = zeros(GENS)
	elite_new_f = zeros(GENS)
	for i, (n, o) in enumerate(zip(new, old)):
		new_f[i] = len(n) / (len(n) + len(o))
		
		ne = filter(is_elite, n)
		no = filter(is_elite, o)
		elite_new_f[i] = len(ne) / (len(ne) + len(no))

	def dump(r):
		for x, g in enumerate(r):
			for rank, y in g:
				if rank < ELITE:
					print x + jitter(), y
		print 'e'

	print r'''
		reset
		set multiplot layout 2,1
		plot \
			"-" w p pt 7 ps 0.2 lc rgb "black" t "Alt", \
			"-" w p pt 7 ps 0.2 lc rgb "red" t "Neu"
	'''
	dump(old)
	dump(new)

	print 'plot "-" w l, "-" w l'
	print '\n'.join(map(str, new_f)), '\ne'
	print '\n'.join(map(str, elite_new_f)), '\ne'

	print 'unset multiplot'

if __name__ == '__main__':
	new(*sys.argv[1:])
