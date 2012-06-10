#!/usr/bin/env zsh
name="run-$(date +%FT%T)"
./search "$name.gen" | tee "$name.log"
