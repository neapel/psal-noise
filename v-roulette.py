#!/usr/bin/env python
from __future__ import division
from visualize import *

def roulette(name):
	def prepare_pie(data):
		return ','.join([
			'"-" w {0} lc rgbcolor "{1}"'.format(
				'filledcurve',
				('#ff0000' if i % 2 else '#440000') if i < ELITE \
					else ('#0000ff' if i%2 else '#000044')
			)
			for i in range(len(data))
		])

	def make_pie(pop, inner=0.8, outer=1.0):
		data = map(itemgetter(1), pop)
		cum = cumsum([0] + data)
		angles = cum * (2 * pi / cum[-1])
		for start, end in zip(angles, angles[1:]):
			delta = end - start
			steps = int(delta / pi * 180 / 2)
			angles = start + delta / (steps + 1) * array(range(0, steps + 2))
			# outer rim
			for x in angles: print outer * sin(x), outer * cos(x)
			# inner rim
			for x in reversed(angles): print inner * sin(x), inner * cos(x)
			print 'e'

	print '''
		reset
		set size square
		unset border
		unset xtics
		unset ytics
		unset colorbox
		unset key
		set palette rgb 33,13,10
	'''

	last = read_last_pop(name, ALL)

	print 'plot', prepare_pie(last),
	print ', "-" w l lw 2 lc rgb "black"'
	make_pie(last, 0.8, 1.0)

	r1 = 0.7
	r2 = 0.78
	for i in range(ALL):
		x = nr.random() * (2 * pi)
		print r1 * sin(x), r1 * cos(x)
		print r2 * sin(x), r2 * cos(x)
		print
	print 'e'

if __name__ == '__main__':
	roulette(*sys.argv[1:])
