#!/usr/bin/env python

from glob import glob
import sys
import os.path

def read_pop(name, limit=20):
	for fname in sorted(glob(name + '/*.pop')):
		with open(fname) as f:
			gen = []
			for line, _ in zip(f, range(limit)):
				fields = line.split()
				if len(fields) < 2:
					return
				rule = fields[0]
				fits = map(float, fields[1:])
				gen.append(tuple([rule] + fits))
			if len(gen) > 0:
				yield tuple(gen)

def read_gen(name):
	for fname in sorted(glob(name + '/*.gen')):
		with open(fname) as f:
			gen = {}
			for line in f:
				fields = line.split()
				if fields[0] == 'elite':
					gen[fields[1]] = (fields[1],)
				elif fields[0] == 'mate' and fields[3] == 'children':
					gen[fields[4]] = (fields[1], fields[2])
					gen[fields[5]] = (fields[1], fields[2])
			if len(gen) > 0:
				yield gen

def mean(points, at=1):
	return sum([p[at] for p in points]) / len(points)

def smooth(points, d=2):
	out = list(points)
	for i in range(len(points)):
		context = points[max(0,i - d):min(len(points),i + 1 + d)]
		out[i] = sum(context) / len(context)
	return out

def overview(name):
	d = list(read_pop(name))
	md = map(mean, d)
	smd = smooth(md, d=10)
	print 'reset'
	print 'set title "%s"' % (name,)
	print 'unset key'
	print 'set style line 1 pt 5 ps 0.01 lw 2 lc rgbcolor "red"'
	print 'set style line 2 lc rgbcolor "#606060"'
	print 'set style line 3 pt 5 ps 0.05 lc rgbcolor "black"'
	print 'set xtics border nomirror out 50 offset 0,0.25 font "Sans, 8"'
	print 'set mxtics 5'
	print 'unset ytics'
	print 'set border 1 ls 2'
	print 'set rmargin 5'
	print 'set xrange [0:*]; set yrange [0:*]'
	print 'set label 1 "%d" at %f,%f nopoint offset 0.25,0 textcolor ls 1 font "Sans Bold, 10"' % (smd[-1], len(smd), smd[-1])
	print 'plot "-" volatile using ( column(-1) + 0.5 * (rand(0) - 0.5)):1 w p ls 3, ',
	print '"-" volatile w p ls 1, ',
	print '"-" volatile w l ls 1'
	for p in d:
		for i in p:
			v = i[1]
			print v
		print
	print 'e'
	for p in md:
		print p
	print 'e'
	for p in smd:
		print p
	print 'e'

def overviews(*names):
	print 'set terminal pngcairo notransparent size 1000,400'
	for name in names:
		print 'set output "%s.png"' % name
		overview(name)

def averages(*names):
	print 'reset'
	print 'set key outside center horizontal top samplen 1'
	print 'plot ', ','.join([
		('"-" volatile w l lc palette frac %f lt %d t "%s"' % (i/20.0,i,os.path.basename(name),))
		for i, name in enumerate(names)
	])
	for name in names:
		for x in smooth(map(mean, read_pop(name)), d=10):
			print x
		print 'e'

def avg_elite(*names):
	print 'unset key'
	print 'plot ', ', '.join(['"-" smooth bezier w l' for k in names])
	for name in names:
		for gen in read_pop(name):
			print sum([i[1] for i in gen]) / len(gen)
		print 'e'

if __name__ == '__main__':
	names = list([os.path.splitext(n)[0] for n in sys.argv[2:]])
	locals()[sys.argv[1]](*names)
