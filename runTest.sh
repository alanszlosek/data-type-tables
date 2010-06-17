#!/bin/sh
cd oldTests
rm dtt.db
sqlite3 dtt.db < ../schema.sqlite3
PYTHONPATH=../:$PYTHONPATH python3 $1.*.py
cd ..
