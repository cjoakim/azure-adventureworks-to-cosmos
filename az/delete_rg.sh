#!/bin/bash

# Bash script with AZ CLI to automate the creation/deletion of my
# Azure SQL DB account.
# Chris Joakim, Microsoft, 2021/01/07
#
# https://docs.microsoft.com/en-us/azure/sql-database/scripts/sql-database-create-and-configure-database-cli

# az login

source ./config.sh

echo 'deleting resource group: '$resource_group
az group delete \
    --name $resource_group \
    --subscription $subscription \
    --yes \
    > tmp/delete_rg.json

echo 'done'
