#!/usr/bin/env python
# encoding=utf-8
from __future__ import division
from visualize import *

def lambda_hist(*names):
	GENS = 50

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
		unset key
		unset colorbox
		unset border
		#set hidden3d
		set pm3d corners2color max hidden3d 1 interpolate 1,2
		splot "-" matrix w pm3d
	'''
	dump(read(10))

if __name__ == '__main__':
	lambda_hist(*sys.argv[1:])


