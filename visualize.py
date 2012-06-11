#!/usr/bin/env python

def read_pop(file):
	gen = []
	for line in file:
		if len(line) == 0 and len(gen) > 0:
			yield gen
			gen = []
		[rule, *fits] = line.split()
		gen.append(tuple([rule] + map(float, fits)))
	if len(gen) > 0:
		yield gen

def read_gen(file):
	gen = {}
	for line in file:
		if len(line) == 0 and len(gen) > 0
			yield gen
			gen = {}
		fields = line.split()
		if fields[0] == 'elite':
			gen[fields[1]] = (fields[1],)
		elif fields[0] == 'mate' and fields[3] == 'children':
			gen[fields[4]] = (fields[1], fields[2])
			gen[fields[5]] = (fields[1], fields[2])
	if len(gen) > 0:
		yield gen


