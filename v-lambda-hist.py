#!/usr/bin/env python
# encoding=utf-8
from __future__ import division
from visualize import *

def lambda_hist(*names):
	GENS = 200
	DETAIL = 40

	def read(top):
		lambdas = zeros((33, GENS))
		for name in names:
			for i, pop in zip(range(GENS), read_pop(name, top)):
				for k in pop:
					lambdas[k[0].count('1'), i] += 1
		return lambdas

	def dump(a):
		print '\n'.join([ ' '.join(map(str, l)) for l in a ]), '\ne\ne'

	print '''
		reset
		set termoptions enhanced
		unset key
		unset colorbox
		unset border
		set multiplot layout 2,2 rowsfirst
		set yrange [-0.5:32.5]
		set cbrange [0:1]
	'''

	datas = map(read, [10, ALL])
	datas = map(lambda x: x / x[:,10:].max(), datas)

	for i, data in enumerate(datas):
		margin = 1.35
		if i == 0:
			print '''
				unset x2tics
				set xtics out nomirror font ",10"
				set label 1 "Generation" at graph 0, graph 0 center rotate by 90 font ",10" offset -7, -{0}
				set ylabel "λ_{{10}}" font ",10"
				set tmargin 1
				set bmargin {0}
			'''.format(margin)
		else:
			print '''
				unset xtics
				set x2tics out nomirror format ""
				set ylabel "λ_{{160}}" font ",10"
				set tmargin {0}
				set bmargin 1
			'''.format(margin)

		print '''
			set ytics 4 out nomirror font ",10"
			unset lmargin
			set rmargin 0
			set  xrange [-0.5:{0}+0.5]
			set x2range [-0.5:{0}+0.5]
			plot "-" matrix w image
		'''.format(DETAIL - 1)
		dump(data[:,:DETAIL+1])

		print '''
			unset ytics
			unset ylabel
			set lmargin 0
			unset rmargin
			unset label 1
			set  xrange [{0}-0.5:{1}+0.5]
			set x2range [{0}-0.5:{1}+0.5]
			plot "-" matrix using ($1 + {0} - 1):2:3 w image
		'''.format(DETAIL, GENS - 1)
		dump(data[:,DETAIL-1:])

	print 'unset multiplot'

if __name__ == '__main__':
	lambda_hist(*sys.argv[1:])

