#!/bin/bash

# Bash script to execute the process to wrangle the exported data into a format
# that can be loaded into NoSQL/CosmosDB.
# Chris Joakim, 2021/01/07

python wrangle.py gather_table_metadata

python wrangle.py csv_to_json

python wrangle.py create_documents

echo 'done'
