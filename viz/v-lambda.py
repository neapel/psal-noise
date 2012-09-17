#!/usr/bin/env python
# encoding=utf-8
from __future__ import division
from visualize import *

def lambda_hist(*params):
	paper = array([ 0,  0,  0,  0,  0,  0,  0,  0,
	          0,  0,  2, 16, 21, 37, 39, 31,
	         31, 15,  6,  2,  0,  0,  0,  0,
	          0,  0,  0,  0,  0,  0,  0,  0, 0])

	titles = ['Paper'] + list(params[1::2])
	names = params[::2]
	count = [sum(paper)]
	data = [paper / max(paper)]
	for pat in names:
		lambdas = zeros((33))
		rules = list([
			i[0]
			for name in glob(pat + '*/')
			for i in read_this_pop(name, 199, 10)
		])
		#rules = list(set(rules))
		count.append(len(rules))
		for r in rules:
			lambdas[r.count('1')] += 1
		lambdas /= max(lambdas)
		data.append(lambdas)

	print r'''
		reset
		set termoptions enhanced
		unset colorbox
		set palette rgb 33,13,10
		set key at graph 0.8,graph 1 reverse Left samplen 0.5 spacing 1.5
		set xrange [0:32]
		set yrange [0:*]
		unset border
		set xtics 1 scale 0 format '[c]{$\frac{%.0f}{32}$}'
		set xlabel '$\lambda$'
		unset ytics
		set style fill solid 1 noborder
	'''

	print 'plot ', ','.join([
		'"-" w boxes lc rgbcolor "{0}" t "{1}"'.format(color, title, c)
		for title, color, c in zip(titles, ['black'] + COLORS, count)
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
	smallw = fullw / len(data)

	histogram(data, [smallw] * len(data))

if __name__ == '__main__':
	lambda_hist(*sys.argv[1:])
