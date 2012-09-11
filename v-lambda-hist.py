#!/usr/bin/env python
# encoding=utf-8
from __future__ import division
from visualize import *

def lambda_hist(*names):
	GENS = 200
	DETAIL = 40
	TOP = ALL

	def read(top):
		lambdas = zeros((33, GENS))
		for name in names:
			for i, pop in zip(range(GENS), read_pop(name, top)):
				for k in pop:
					lambdas[k[0].count('1'), i] += 1
		return lambdas

	data = read(TOP)
	data = data / data[:,10:].max()


	def dump(a):
		print '\n'.join([ ' '.join(map(str, l)) for l in a ]), '\ne\ne'

	print r'''
		reset
		unset key
		
		set palette defined (0 "white", 0.25 "#729fcf", 0.5 "#cc0000", 1 "#fce94f")
		unset colorbox
		set cbrange [0:1]

		unset border
		set multiplot layout 1,2

		set yrange [-0.5:24.5]
		set ylabel '$\lambda$' offset 3,0
		set ytics 4 out nomirror format '\sfrac{{%.0f}}{{32}}'
		set mytics 4

		set xrange [-0.5:{0}+0.5]
		set xtics 5 out nomirror format "[c]{{%.f}}"
		set mxtics 5
		set xlabel ' '
		
		set rmargin 0
		
		plot "-" matrix w image
	'''.format(DETAIL - 1)
	dump(data[:,:DETAIL+1])

	print '''
		unset ytics
		unset ylabel
		set lmargin 0
		set rmargin 1
		set xtics 20
		set mxtics 20
		set  xrange [{0}-0.5:{1}+0.5]
		plot "-" matrix using ($1 + {0} - 1):2:3 w image
	'''.format(DETAIL, GENS - 1)
	dump(data[:,DETAIL-1:])

	print 'unset multiplot'

if __name__ == '__main__':
	lambda_hist(*sys.argv[1:])

