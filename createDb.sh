#!/bin/sh
rm tests/dtt.db
sqlite3 tests/dtt.db < schema.sqlite3
