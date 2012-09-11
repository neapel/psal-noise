#!/usr/bin/env python
# encoding=utf-8
from __future__ import division
from visualize import *

def profile(name):
	GENS = 200

	profiles = zeros((32, GENS))
	fitness = zeros(GENS)
	for i, g in zip(range(GENS), read_pop(name, ALL)):
		profile = zeros((32, len(g)))
		fit = zeros(len(g))
		for j, r in enumerate(g):
			profile[:,j] = array(map(int, reversed(r[0])))
			fit[j] = r[1]
		profiles[:,i] = mean(profile, 1)

	print r'''
		reset
		unset key
		set palette defined (0 "#a40000", 0.5 "#ffffff", 1 "#0062a3")
		set colorbox user horizontal origin graph 0, character 0.5 size character 10, character 0.5 noborder
		set cbrange [0:1]
		set cbtics scale 0 offset 0,0.75 ("0" 0, "1" 1)
		unset border
		set yrange [0.5:31.5]
		set ytics 1,2 scale 1,1 out nomirror format '$\overline R_{%.0f}$'
		set lmargin 5
		set rmargin 5
		set mytics 2
		set xrange [0-0.5 : 200-0.5]
		set xtics 10 out nomirror
		set mxtics 10
		set xlabel 'Generation'
		plot "-" matrix w image
	'''
	print '\n'.join([' '.join(map(str, line)) for line in profiles]), '\ne\ne'

if __name__ == '__main__':
	profile(*sys.argv[1:])
