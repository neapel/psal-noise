#!/usr/bin/env python
# encoding=utf-8
from __future__ import division
from visualize import *
from collections import *
from itertools import *

def new(*names):
	
	seen = defaultdict(int)
	everything = 0
	for name in names:
		for g in read_pop(name, ALL):
			for r in g:
				seen[r[0]] += 1
				everything += 1

	grouped = list([len(list(s)) for c, s in groupby(sorted(seen.items(), key=itemgetter(1)), key=itemgetter(1))])

	unique = sum(grouped)
	multi = sum(grouped[1:])

	print 'p multi', multi / unique
	print 'expected', everything, 'p seen', 1 - unique/everything


if __name__ == '__main__':
	new(*sys.argv[1:])
