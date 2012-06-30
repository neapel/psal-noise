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
						gen[fields[1]] = (fields[1],)
					elif fields[0] == 'mate' and fields[3] == 'children':
						if fields[4] not in gen:
							gen[fields[4]] = (fields[1], fields[2])
						if fields[5] not in gen:
							gen[fields[5]] = (fields[1], fields[2])
			if len(gen) > 0:
				yield gen


def smooth(points, window=1+2*25):
	if window == 0:
		return list(points)
	w = hanning(window)
	data = [points[0]] * window + points + [points[-1]] * window
	out = convolve(w / sum(w), data, 'same')
	return out[window:-window]

def overview(name):
	pop = array(map(lambda x: map(itemgetter(1), x), read_pop(name, ALL)))
	elite = pop[:,:ELITE]
	elite_mean = list(mean(elite, 1))
	smooth_mean = smooth(elite_mean, 1+2*5)
	print 'reset'
	print 'set title "{0}"'.format(name)
	print 'unset key'
	print 'set style line 1 pt 5 ps 0.2 lw 2 lc rgbcolor "red"'
	print 'set style line 2 lc rgbcolor "#606060"'
	print 'set style line 3 pt 5 ps 0.1 lc rgbcolor "black"'
	print 'set style line 4 pt 5 ps 0.05 lc rgbcolor "gray"'
	print 'set xtics border nomirror out 50 offset 0,0.25 font "Sans, 8"'
	print 'set mxtics 5'
	print 'unset ytics'
	print 'set border 0 ls 2'
	print 'set rmargin 5'
	print 'set xrange [0:*]; set yrange [0:*]'
	print 'set label 1 "{0:.0f}" at {1},{0} '.format(smooth_mean[-1], len(smooth_mean)),
	print '  nopoint offset 0.25,0 textcolor ls 1 font "Sans Bold, 10"'
	print 'plot ',
	print '"-" volatile w p ls 4, ',
	print '"-" volatile w p ls 3, ',
	print '"-" volatile w p ls 1, ',
	print '"-" volatile w l ls 1'
	for i, gen in enumerate(pop[:,ELITE:]): # normal
		for x in gen: print i + jitter(), x
	print 'e'
	for i, gen in enumerate(elite): # elite
		for x in gen: print i + jitter(), x
	print 'e'
	for p in elite_mean: print p
	print 'e'
	for p in smooth_mean: print p
	print 'e'

def overviews(*names):
	print 'set terminal pngcairo notransparent size 1000,400'
	for name in names:
		print 'print "{0}" ; set output "{0}.png"'.format(name)
		overview(name)

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

def binstring(s):
	return s.replace('0','.').replace('1','▮')

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
		print 'set xtics add ("%s" %d)' % (binstring(l[0]), x) 
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

def profile(ptype, name):
	profiles = []
	for g in read_pop(name):
		p = []
		for i in g:
			p.append(array(map(int, i[0])))
		p = vstack(p)
		if ptype == 'mean':
			profiles.append(mean(p, 0))
		else:
			profiles.append(var(p, 0))
	profiles = vstack(profiles)
	print 'reset'
	print 'set palette rgb 31,13,10'

	print 'set rmargin 10'
	if ptype == 'mean':
		print 'set palette rgb 9,13,-9'
		print 'set cbtics scale 0 ("{0}" 0, "{1}" 1)'.format(*map(binstring, '01'))
	else:
		print 'set palette rgb -7,-7,-7'
		print 'set cbtics scale 0 ("0" 0, "0.25" 0.25)'
	h = 0.125
	print 'set colorbox user noborder origin graph 1.01, graph {0} size character 2, graph {1}'.format((1-h)/2, h)
	print 'set yrange [-0.5:31.5]'
	print 'set lmargin 8'
	print 'unset border'
	print 'set ytics scale 0 ({0}) font "Monospace"'.format(','.join([
		'"{0}" {1}'.format(binstring(bin(i)[2:].rjust(5,'0')), i)
		for i in range(32)
	]))
	print 'set xrange [0:200]'
	print 'set xtics out nomirror'
	print 'plot "-" matrix w image'
	print '\n'.join([' '.join(map(str, line)) for line in reversed(transpose(profiles))])
	print 'e'
	print 'e'

def lambda_hist(*names):
	lambdas = [0] * 32
	for name in names:
		for indiv in read_this_pop(name, 200, 10):
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

def parenthood(name): # run112
	n = 7
	pop = list({} for _ in range(n + 1))
	for i, g in zip(range(n + 1), read_pop(name, ALL)):
		for j, r in enumerate(g):
			pop[i][r[0]] = (i + jitter(8), r[1], j)

	super_elite_lines = []
	super_mate_lines = []
	elite_lines = []
	mate_lines = []
	for i, g in zip(range(n), read_gen(name)):
		for k, v in g.items():
			child = pop[i + 1].get(k, None)
			if child:
				parents = map(lambda x: pop[i][x], v)
				appto = None
				if child[2] == 0:
					appto = super_elite_lines if len(parents) == 1 else super_mate_lines
				else:
					appto = elite_lines if len(parents) == 1 else mate_lines
				for p in parents:
					appto.append( child + p )

	print 'reset'
	print 'set key left top samplen 1'
	print 'unset border'
	print 'unset ytics'
	print 'set xtics scale 0 font ",8"'
	print 'set xrange [-0.5:{0}]'.format(n + 0.5)
	print 'set style line 1 lw 0.1 lc rgbcolor "blue"'
	print 'set style line 2 lw 0.5 lc rgbcolor "red"'
	print 'plot ',
	print '"-" w l ls 1 notitle,',
	print '"-" w l ls 2 notitle,',
	print '"-" w l ls 1 lw 1.25 t "Crossover",',
	print '"-" w l ls 2 lw 1.5 t "Kopiert",',
	print '"-" w p pt 5 ps 0.3 lc rgbcolor "black" t "Regeln" '
	def lines(l):
		for x1, y1, _, x2, y2, _ in l:
			print x1, y1, '\n', x2, y2, '\n'
		print 'e'
	lines(mate_lines)
	lines(elite_lines)
	lines(super_mate_lines)
	lines(super_elite_lines)
	for gen in pop:
		for x, y, _ in gen.values(): print x, y
	print 'e'


def genealogy(name):
	n = 150
	pop = list({} for _ in range(n + 1))
	elite_threshold = []
	poor_threshold = []
	for i, g in zip(range(n + 1), read_pop(name, ALL)):
		for j, r in enumerate(g):
			pop[i][r[0]] = (i + jitter(), r[1], j)
		elite_threshold.append(g[ELITE - 1][1])
		poor_threshold.append(g[ALL//2][1])

	old_elite = []
	new_elite = []
	rest = []
	for i, g in zip(range(n), read_gen(name)):
		for k, v in g.items():
			child = pop[i + 1].get(k, None)
			if child:
				if len(v) == 1:
					old_elite.append(child)
				elif child[2] < ELITE:
					new_elite.append(child)
				else:
					rest.append(child)
					#for p in v:
					#	parent = pop.get((i, p), None)
					#	if parent:
					#		lines.append( parent + child )

	rest = rest + new_elite
	new_elite = []

	print 'reset'
	print 'set key left top samplen 1'
	print 'unset border'
	print 'unset ytics'
	print 'set xtics scale 0 font ",8"'
	print 'set xrange [0.51:{0}]'.format(n + 0.49)
	print 'plot ',
	print '"-" w p pt 5 ps 0.05 lc rgbcolor "#808080" t "Normale", ',
	print '"-" w histeps lc rgbcolor "black" t "Elitegrenze", ',
	print '"-" w histeps lc rgbcolor "black" t "Median", ',
	print '"-" w p pt 5 ps 0.3 lc rgbcolor "red" t "Alte Elite", ',
	print '"-" w p pt 5 ps 0.2 lc rgbcolor "blue" t "Neu in Elite" '
	for x, y, _ in rest: print x, y
	print 'e'
	for y in elite_threshold: print y
	print 'e'
	for y in poor_threshold: print y
	print 'e'
	for x, y, _ in old_elite: print x, y
	print 'e'
	for x, y, _ in new_elite: print x, y
	print 'e'


def one_spectrum(rule):
	out = check_output(['./search', '--info', rule])
	out = out.split('\n')
	fit, alpha, beta = map(float, out[0].split())
	data = out[3:]
	return fit, alpha, beta, data


def spectrum(rule, width=1, height=1):
	width=int(width)
	height=int(height)

	print 'reset'
	print 'set termoption enhanced'
	print 'set logscale xyx2'
	print 'set yrange [0.0001:100]'
	print 'set xrange [1:1500]'
	print 'set x2range [1:1500]'
	print 'set xtics out nomirror format "10^{%T}"'
	print 'set ytics out nomirror format "10^{%T}"'

	print 'set x2tics scale 0 format "" (10, 100)'
	print 'set style line 8 lt 1 lc rgbcolor "gray"'
	print 'set grid x2 ls 8'

	print 'set border 3'
	print 'unset key'
	print 'set style fill solid 0.125'

	print 'set multiplot layout {0},{1}'.format(width, height)

	for i in range(width * height):
		fit, alpha, beta, data = one_spectrum(rule)
		print 'set title "{{/Symbol a}}={0:.4f} {{/Symbol b}}={1:.4f} f={2:.2f}" enhanced'.format(alpha, beta, fit)

		print 'plot ',
		print '"-" volatile w filledcu lc rgbcolor "red", ',
		print 'exp({0} + {1} * log(x)) w l lw 2 lc rgbcolor "red", '.format(alpha, beta),
		print '"-" volatile using ($0 + 1):1 w p pt 5 ps 0.2 lc rgbcolor "black"'
		for x, y in enumerate(data[:100], 1):
			print x, y, exp(alpha + beta * log(x)) 
		print 'e'
		print '\n'.join(data)
		print 'e'

	print 'unset multiplot'




if __name__ == '__main__':
	names = list([os.path.splitext(n)[0] for n in sys.argv[2:]])
	locals()[sys.argv[1]](*names)
