#!/bin/bash
name="run-$(date +%FT%T)"
./search "$name" | tee "$name.log"
