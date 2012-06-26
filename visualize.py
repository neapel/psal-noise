#!/usr/bin/env python
# encoding=utf-8

from glob import glob
import sys
import os.path

ALL = 160
ELITE = 20

def read_one_pop(f, limit):
	gen = []
	for line, _ in zip(f, range(limit)):
		fields = line.split()
		if len(fields) < 2:
			return
		rule = fields[0]
		fits = map(float, fields[1:])
		gen.append(tuple([rule] + fits))
	if len(gen) > 0:
		return tuple(gen)

def read_pop(name, limit=ELITE):
	for fname in sorted(glob(name + '/*.pop')):
		with open(fname) as f:
			x = read_one_pop(f, limit)
			if x:
				yield x

def read_last_pop(name, limit=ELITE):
	for fname in sorted(glob(name + '/*.pop'), reverse=True):
		with open(fname) as f:
			x = read_one_pop(f, limit)
			if x:
				return x

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
		for i in p: print i[1]
		print
	print 'e'
	for p in md: print p
	print 'e'
	for p in smd: print p
	print 'e'

def overviews(*names):
	print 'set terminal pngcairo notransparent size 1000,400'
	for name in names:
		print 'print "%s"' % name
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
		for gen in read_pop(name): print mean(gen, 1)
		print 'e'

def one_pop(name):
	pop_whole = filter(lambda x: x[1] > 1, read_last_pop(name, ALL))
	pop = map(lambda x: x[2:], pop_whole)
	pop_a = map(lambda x: x[1], pop_whole)
	s = range(len(pop[0]))
	print 'reset'
	print 'unset border'
	print 'unset key'
	print 'set yrange [0:*]'
	print 'set xrange [-1:*]'
	print 'set bmargin 10'
	print 'unset xtics'
	print 'set ytics scale 0'
	print 'set encoding utf8'
	print 'set xtics scale 0 rotate by -90 offset -0.5,-0.5 font "Monospace,5" ("" 0)'
	for x, l in enumerate(pop_whole):
		print 'set xtics add ("%s" %d)' % (l[0].replace('0','.').replace('1','▮'), x) 
	print 'plot ',
	print '"-" volatile w impulses lc rgbcolor "gray", ',
	for i in s:
		print '"-" volatile w p pt %d lc rgbcolor "black", ' % (i + 1,),
	print '"-" volatile w p pt 1 lw 2 lc rgbcolor "red" '
	for x in map(max, pop): print x
	print 'e'
	for i in s:
		for l in pop: print l[i]
		print 'e'
	for x in pop_a: print x
	print 'e'

def lambda_hist(*names):
	lambdas = [0] * 32
	for name in names:
		for indiv in read_last_pop(name, 10):
			lambdas[indiv[0].count('1')] += 1
	paper_lambdas = [ 0,  0,  0,  0,  0,  0,  0,  0,
	                  0,  0,  2, 16, 21, 37, 39, 31,
						  31, 15,  6,  2,  0,  0,  0,  0,
							0,  0,  0,  0,  0,  0,  0,  0]
	print 'reset'
	print 'unset key'
	print 'set xrange [0:32]'
	print 'set yrange [0:*]'
	print 'set border 1'
	print 'unset ytics'
	print 'set xtics out nomirror format "%.0f" 1'
	print 'set boxwidth 0.8'
	print 'set style fill solid 1 noborder'
	print 'set style data histograms'
	print 'set style histogram cluster gap 1'
	print 'plot "-" volatile using 1, "-" volatile using 1'
	for x in lambdas: print x
	print 'e'
	for x in paper_lambdas: print x
	print 'e'

if __name__ == '__main__':
	names = list([os.path.splitext(n)[0] for n in sys.argv[2:]])
	locals()[sys.argv[1]](*names)
