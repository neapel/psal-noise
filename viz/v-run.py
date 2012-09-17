#!/usr/bin/env python
# encoding=utf-8
from __future__ import division
from visualize import *

def run(rule, width=201, height=201, more=''):
	print '''
		reset
		unset border
		unset colorbox
		unset key

		set palette defined (0 "white", 1 "black")

		set lmargin 0
		set rmargin 0
		set tmargin 0
		set bmargin 0

		unset xtics
		unset ytics
		set xrange [*:*] reverse
		set yrange [*:*] reverse
		set size ratio {2}.0/{1}.0
		plot "< ./search --width {1} --height {2} --run {0} --seed 21 {3}" matrix w image
	'''.format(easyrule(rule), width, height, more)

if __name__ == '__main__':
	run(*sys.argv[1:])
