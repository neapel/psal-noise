#!/usr/bin/env python

def read_pop(file, limit=20):
	gen = []
	for line in file:
		line = line.strip()
		if len(line) == 0:
			if len(gen) > 0:
				yield gen
			gen = []
		elif len(gen) < limit:
			fields = line.split()
			rule = fields[0]
			fits = map(float, fields[1:])
			gen.append(tuple([rule] + fits))
	if len(gen) > 0:
		yield gen

def read_gen(file):
	gen = {}
	for line in file:
		if len(line) == 0:
			if len(gen) > 0:
				yield gen
			gen = {}
		else:
			fields = line.split()
			if fields[0] == 'elite':
				gen[fields[1]] = (fields[1],)
			elif fields[0] == 'mate' and fields[3] == 'children':
				gen[fields[4]] = (fields[1], fields[2])
				gen[fields[5]] = (fields[1], fields[2])
	if len(gen) > 0:
		yield gen

def each_elite(*names):
	print 'set multiplot layout', len(names), ',1'
	for name in names:
		pop = read_pop(open(name + '.pop', 'r'))
		print 'unset key'
		print 'unset xtics; unset ytics'
		print 'set tmargin 0; set rmargin 0; set bmargin 0; set lmargin 0'
		print 'plot "-" volatile using (column(-1)):1',
		print 'w p pt 5 ps 0.1 ',
		print 't "' + name + '"'
		for p in pop:
			for i in p:
				v = i[1]
				print v
			print
		print 'e'
	print 'unset multiplot'

def avg_elite(*names):
	print 'unset key'
	print 'plot ', ', '.join(['"-" smooth bezier w l' for k in names])
	for name in names:
		with open(name + '.pop') as f:
			for gen in read_pop(f):
				print sum([i[1] for i in gen]) / len(gen)
		print 'e'

if __name__ == '__main__':
	import sys
	import os.path
	names = list([os.path.splitext(n)[0] for n in sys.argv[1:]])
	avg_elite(*names)
