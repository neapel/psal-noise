#!/bin/bash
name="run-$(date +%FT%T)"
./search "$name" | tee "$name.log"
git add "$name.gen" "$name.pop" "$name.log" && git commit -m 'output' && git push
