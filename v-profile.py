#!/usr/bin/env python
# encoding=utf-8
from __future__ import division
from visualize import *

def profile(name):
	GENS = 200
	DETAIL = 40

	profiles = zeros((32, GENS))
	fitness = zeros(GENS)
	for i, g in zip(range(GENS), read_pop(name, ALL)):
		profile = zeros((32, len(g)))
		fit = zeros(len(g))
		for j, r in enumerate(g):
			profile[:,j] = array(map(int, reversed(r[0])))
			fit[j] = r[1]
		profiles[:,i] = mean(profile, 1)
		fitness[i] = mean(fit[:ELITE])

	def dump(m):
		print '\n'.join([' '.join(map(str, line)) for line in m]), '\ne\ne'

	print '''
		reset
		unset key
		set palette defined (0 "white", 0.25 "#cccccc", 0.5 "#cc4444", 0.75 "#444444", 1 "black")
		unset colorbox
		unset border
		set yrange [-0.5:31.5]
		set xtics out nomirror font ",10"
		set multiplot
		set style line 1 lw 1 lc rgbcolor "black"
		H = 0.8
		FITM = {0}
		DETAIL = {1}
	'''.format(5 * ceil(fitness.max() / 5), DETAIL)


	# detail
	print '''
		set size 0.5,H
		set origin 0,0
		set xrange [0-0.5:DETAIL+0.5]
		set lmargin 12
		set rmargin 0
		set ytics scale 0 ({0}) font ",10"
		set label 1 "Generation" font ",10" at graph 0, graph 0 right offset -1,-1.4
		plot "-" matrix w image
	'''.format(','.join([
		'"{0}" {1}'.format(binstring(bin(i)[2:].rjust(5,'0')), i)
		for i in range(32)
	]))
	dump(profiles[:,:DETAIL + 1])

	print '''
		unset label 1
		set size 0.5,(1-H)
		set origin 0,H
		unset xtics
		set ylabel "Fitness →" font ",10"
		unset ytics
		set bmargin 0
		set yrange [0:FITM]
		plot "-" w l ls 1
	'''
	print '\n'.join(map(str, fitness[:DETAIL+2])), '\ne'


	# rest
	print '''
		set size 0.5,H
		set origin 0.5,0
		set lmargin 0
		unset bmargin
		unset rmargin
		unset ylabel
		set xtics out nomirror font ",10"
		set xrange [DETAIL+0.5:200-0.5]
		set yrange [-0.5:31.5]
		plot "-" matrix using ($1 + DETAIL):2:3 w image
	'''
	dump(profiles[:,DETAIL:])

	print '''
		set size 0.5,(1-H)
		set origin 0.5,H
		set bmargin 0
		unset xtics
		set yrange [0:FITM]
		plot "-" using ($0 + DETAIL):1 w l ls 1
	'''
	print '\n'.join(map(str, fitness[DETAIL+1:])), '\ne'

	print 'unset multiplot'

if __name__ == '__main__':
	profile(*sys.argv[1:])
