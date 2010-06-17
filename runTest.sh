#!/bin/sh
cd tests
PYTHONPATH=../:$PYTHONPATH python3 $1.*.py
cd ..
