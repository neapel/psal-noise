#!/usr/bin/env python
from visualize import *

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

if __name__ == '__main__':
	profile(*sys.argv[1:])
