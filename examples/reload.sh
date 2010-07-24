#!/bin/sh
rm dtt.db
sqlite3 dtt.db < ../schema.sqlite3
