#!/usr/bin/env python
# encoding=utf-8
from __future__ import division
from visualize import *

def run(rule):
	print '''
		reset
		unset border
		unset colorbox
		unset key

		set palette defined (0 "white", 1 "black")

		set lmargin 4
		set rmargin 4
		set tmargin 1
		set bmargin 2

		unset xtics
		unset ytics
		set xrange [*:*] reverse
		set yrange [*:*] reverse
		set label "← Zeit" at graph 0, graph 1 right rotate by 90 font ",10" offset -2,0
		set label "W" at graph 0, graph 0 center font ",10" offset 0,-1
		set label "1" at graph 1, graph 0 center font ",10" offset 0,-1

		plot "< ./search --run {0} --seed 21" matrix w image
	'''.format(easyrule(rule))

if __name__ == '__main__':
	run(*sys.argv[1:])
