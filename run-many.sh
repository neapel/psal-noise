#!/bin/bash
while true ; do
	for x in $* ; do
		./search --name "$x" --generations 50
	done
done
