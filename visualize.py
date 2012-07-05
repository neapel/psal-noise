#!/usr/bin/env python
# encoding=utf-8

from __future__ import division
from glob import glob
import sys
import os.path
from numpy import *
from random import random
from operator import itemgetter
from subprocess import check_output

ALL = 160
ELITE = 20

def jitter(d = 2):
	return (random() - 0.5) / d

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

def read_this_pop(name, number, limit=ELITE):
	with open('{0}/{1:05d}.pop'.format(name, number)) as f:
		x = read_one_pop(f, limit)
		if x:
			return x

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
	data = [points[0]] * window + points + [points[-1]] * window
	out = convolve(w / sum(w), data, 'same')
	return out[window:-window]


def binstring(s):
	return s.replace('0','.').replace('1','▮')


def one_spectrum(rule):
	out = check_output(['./search', '--info', rule])
	out = out.split('\n')
	fit, alpha, beta = map(float, out[0].split())
	data = out[3:]
	return fit, alpha, beta, data

