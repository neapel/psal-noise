#!/usr/bin/env python
# encoding=utf-8
from __future__ import division
from visualize import *

def lambda_hist(*names):
	paper = [ 0,  0,  0,  0,  0,  0,  0,  0,
	          0,  0,  2, 16, 21, 37, 39, 31,
	         31, 15,  6,  2,  0,  0,  0,  0,
	          0,  0,  0,  0,  0,  0,  0,  0, 0]
	data = []
	for pat in names:
		lambdas = [0] * 33
		for name in glob(pat + '*/'):
			for i in read_this_pop(name, 200, 10):
				lambdas[i[0].count('1')] += 1
		data.append(lambdas)

	print '''
		reset
		set termoptions enhanced
		unset colorbox
		set palette rgb 33,13,10
		set key top right samplen 1
		set xrange [0:32]
		set yrange [0:*]
		unset border
		set xtics 1 scale 0 font ",10"
		set xlabel "λ_{10}" font ",10"
		unset ytics
		set style fill solid 1 noborder
	'''

	print 'plot "-" w boxes lc rgbcolor "black" t "Paper", ', ','.join([
		'"-"w boxes lc rgbcolor "{0}" t "Lauf {1}"'.format(c, i)
		for i, (_, c) in enumerate(zip(data, ['#80b2e8', '#c791c1', '#e9b96e']), 1)
	])

	def histogram(datas, widths):
		dl = len(datas)
		bins = max(map(len, datas))
		xss = zeros((dl + 1, bins))
		for i, (data, width) in enumerate(zip(datas, widths)):
			for j, v in enumerate(data):
				if v > 0:
					xss[i][j] += width/2
					xss[i + 1][j] += width/2
		xss = cumsum(xss, 0)
		xss -= xss[-1] / 2
		xss += range(bins)
		for xs, data, width in zip(xss, datas, widths):
			for x, v in zip(xs, data):
				print x, v, width
			print 'e'

	fullw = 0.8
	bigw = fullw / 2
	smallw = (fullw - bigw) / len(data)

	histogram([paper] + data, [bigw] + [smallw] * len(data))

if __name__ == '__main__':
	lambda_hist(*sys.argv[1:])
