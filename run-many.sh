#!/bin/bash
while true ; do
	for x in $* ; do
		./search $x
	done
done
