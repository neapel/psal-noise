#!/usr/bin/env python
from visualize import *

def averages(*names):
	print 'reset'
	print 'unset key'
	print 'unset colorbox'
	print 'set palette rgb 33,13,10'
	print 'unset border'
	print 'set grid xtics noytics back lt 1 lc rgbcolor "grey"'
	print 'set xtics scale 0 textcolor rgbcolor "grey"'
	print 'set yrange [0:*]'
	print 'set ytics scale 0'
	print 'plot ', ','.join([
		('"-" volatile w p pt 5 ps 0.01 lw 1.25 lc palette frac {0} notitle, '
		+ '"-" volatile w l lw 2 lc palette frac {0} t "{1}"').format(
			i/len(names), os.path.basename(name))
		for i, name in enumerate(names)
	])
	def mean(points, at=1):
		return sum([p[at] for p in points]) / len(points)
	for name in names:
		m = map(mean, read_pop(name))
		for x in m: print x
		print 'e'
		for x in smooth(m): print x
		print 'e'

if __name__ == '__main__':
	averages(*sys.argv[1:])
