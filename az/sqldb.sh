#!/bin/bash

# Bash script with AZ CLI to automate the creation/deletion of my
# Azure SQL DB account.
# Chris Joakim, Microsoft, 2021/01/07
#
# https://docs.microsoft.com/en-us/azure/sql-database/scripts/sql-database-create-and-configure-database-cli

# az login

source ./config.sh

arg_count=$#
processed=0

create() {
    processed=1
    echo 'creating Azure SQL DB rg: '$sqldb_rg
    az group create \
        --location $sqldb_region \
        --name $sqldb_rg \
        --subscription $subscription \
        > tmp/sqldb_rg_create.json

    echo 'creating Azure SQL DB server: '$sqldb_server
    az sql server create \
        --name $sqldb_server \
        --resource-group $sqldb_rg \
        --location $sqldb_region \
        --admin-user $sqldb_admin_user \
        --admin-password $sqldb_admin_pass \
        > tmp/sqldb_server_create.json

    echo 'creating Azure SQL DB firewall for server: '$sqldb_server
    az sql server firewall-rule create \
        --name "allow-internet" \
        --resource-group $sqldb_rg \
        --server $sqldb_server \
        --start-ip-address $sqldb_start_ip \
        --end-ip-address $sqldb_end_ip \
        > tmp/sqldb_firewall_rule_create.json

    echo 'creating Azure SQL DB database with AdventureWorksLT: '$sqldb_dbname
    az sql db create \
        --resource-group $sqldb_rg \
        --server $sqldb_server \
        --name $sqldb_dbname \
        --sample-name AdventureWorksLT \
        --edition GeneralPurpose \
        --family Gen4 \
        --capacity 1 \
        --zone-redundant false \
        > tmp/sqldb_db_create.json
}

info() {
    processed=1
    echo 'az sql db show: '$sqldb_name
    az sql db show \
        --name $sqldb_dbname \
        --resource-group $sqldb_rg \
        --server $sqldb_server \
        > tmp/sqldb_info.json
}

display_usage() {
    echo 'Usage:'
    echo './sqldb.sh create'
    echo './sqldb.sh info'
}

# ========== "main" logic below ==========

if [ $arg_count -gt 0 ]
then
    for arg in $@
    do
        if [ $arg == "create" ]; then create; fi 
        if [ $arg == "info" ];   then info; fi 
    done
fi

if [ $processed -eq 0 ]; then display_usage; fi

echo 'done'
