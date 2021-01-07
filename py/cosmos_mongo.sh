#!/bin/bash

# Bash script to execute the process to load the wrangled JSON data into CosmosDB.
# Chris Joakim, 2021/01/07

# Usage:
# ./cosmos_mongo.sh load_db design_a
# ./cosmos_mongo.sh load_db design_b
# ./cosmos_mongo.sh load_db design_c
# ./cosmos_mongo.sh delete_all_docs

python cosmos_mongo.py $1 $2

echo 'done'
