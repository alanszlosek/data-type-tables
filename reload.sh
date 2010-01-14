#!/bin/sh
rm test.db
sqlite3 test.db < schema.sqlite
