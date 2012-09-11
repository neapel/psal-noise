#!/usr/bin/env python
# encoding=utf-8

from __future__ import division
from glob import glob
import sys
import os.path
from numpy import *
import numpy.random as nr
from operator import itemgetter
from subprocess import check_output

nr.seed(123)

ALL = 160
ELITE = 20

def jitter(i,j, count=10):
	
	return i + (j % count - count/2)*(0.5 / count)
	#return (nr.random() - 0.5) / d

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

def read_pop(name, limit=ELITE, gens=1000):
	for fname, _ in zip(sorted(glob(name + '/*.pop')), range(gens)):
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

def read_this_pop(name, number, limit=ELITE):
	with open('{0}/{1:05d}.pop'.format(name, number)) as f:
		x = read_one_pop(f, limit)
		if x:
			return x
	raise Exception, "can't read {0} number={1} limit={2}".format(name,number,limit)

def read_gen(name):
	for fname in sorted(glob(name + '/*.gen')):
		with open(fname) as f:
			gen = {}
			for line in f:
				fields = line.split()
				if len(fields) > 1:
					if fields[0] == 'elite':
						gen[fields[1]] = ('e', fields[1])
					elif fields[0] == 'mate' and fields[3] == 'children':
						if fields[4] not in gen:
							gen[fields[4]] = ('c', fields[1], fields[2])
						if fields[5] not in gen:
							gen[fields[5]] = ('c', fields[1], fields[2])
					elif fields[0] == 'mutate':
						if fields[2] not in gen:
							gen[fields[2]] = ('m', fields[1])
			if len(gen) > 0:
				yield gen

def smooth(points, window=1+2*25):
	if window == 0:
		return list(points)
	w = hanning(window)
	#data = [points[0]] * window + points + [points[-1]] * window
	data = [0.0] * window + points + list(reversed(points[-window:]))
	out = convolve(w / sum(w), data, 'same')
	#return out[window:-window]
	return out[window:-window]

def binstring(s,z='□',o='■'):
	#return s.replace('0','.').replace('1','▮')
	return s.replace('0',z).replace('1',o)

def easyrule(s):
	if s[0] == 'r':
		return bin(int(s[1:]))[2:].rjust(8, '0')
	else:
		return s

def one_spectrum(rule, **kwargs):
	args = ['./search', '--info', rule]
	for k, v in kwargs.items():
		args.append('--' + k)
		args.append(str(v))
	out = check_output(args)
	out = out.split('\n')
	fit, alpha, beta = map(float, out[0].split())
	data = out[3:]
	return fit, alpha, beta, data

#        0Buttr     1Orange    2Choclt    3Chamln    4SkyBlu    5Plum      6SctRed
C_BR = ['#fce94f', '#fcaf3e', '#e9b96e', '#8ae234', '#729fcf', '#ad7fa8', '#ef2929']
C_MD = ['#edd400', '#f57900', '#c17d11', '#73d216', '#3465a4', '#75507b', '#cc0000']
C_DR = ['#c4a000', '#ce5c00', '#8f5902', '#4e9a06', '#204a87', '#5c3566', '#a40000']
C = C_BR
C_IN = [4,1,6,3,5,2]
#Aluminium	eeeeec	d3d7cf	babdb6 888a85	555753	2e3436
COLORS = list([C_BR[i] for i in C_IN])
