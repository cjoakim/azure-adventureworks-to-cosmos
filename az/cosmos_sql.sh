#!/bin/bash

# Bash script with AZ CLI to automate the creation/deletion of my
# Azure Cosmos/SQL DB.
# Chris Joakim, Microsoft, 2021/01/07
#
# See https://docs.microsoft.com/en-us/cli/azure/?view=azure-cli-latest

# az login

source ./config.sh

arg_count=$#
processed=0

create() {
    processed=1
    echo 'creating cosmos rg: '$cosmos_sql_rg
    az group create \
        --location $cosmos_sql_region \
        --name $cosmos_sql_rg \
        --subscription $subscription \
        > tmp/cosmos_sql_rg_create.json

    echo 'creating cosmos acct: '$cosmos_sql_acct_name
    az cosmosdb create \
        --name $cosmos_sql_acct_name \
        --resource-group $cosmos_sql_rg \
        --subscription $subscription \
        --locations regionName=$cosmos_sql_region failoverPriority=0 isZoneRedundant=False \
        --default-consistency-level $cosmos_sql_acct_consistency \
        --enable-multiple-write-locations true \
        --enable-analytical-storage true \
        --kind $cosmos_sql_acct_kind \
        > tmp/cosmos_sql_acct_create.json

    create_db
    info  
}

create_db() {
    processed=1
    echo 'creating cosmos db: '$cosmos_sql_dbname
    az cosmosdb sql database create \
        --resource-group $cosmos_sql_rg \
        --account-name $cosmos_sql_acct_name \
        --name $cosmos_sql_dbname \
        > tmp/cosmos_sql_db_create.json
}

create_collections() {
    processed=1
    echo 'creating cosmos collection: '$cosmos_sql_airports_collname
    az cosmosdb sql container create \
        --resource-group $cosmos_sql_rg \
        --account-name $cosmos_sql_acct_name \
        --database-name $cosmos_sql_dbname \
        --name airports \
        --subscription $subscription \
        --partition-key-path /pk \
        --throughput 400 \
        > tmp/cosmos_sql_db_create_airports.json

    az cosmosdb sql container create \
        --resource-group $cosmos_sql_rg \
        --account-name $cosmos_sql_acct_name \
        --database-name $cosmos_sql_dbname \
        --name amtrak_stations \
        --subscription $subscription \
        --partition-key-path /pk \
        --throughput 400 \
        > tmp/cosmos_sql_db_create_amtrak_stations.json

    az cosmosdb sql container create \
        --resource-group $cosmos_sql_rg \
        --account-name $cosmos_sql_acct_name \
        --database-name $cosmos_sql_dbname \
        --name transportation_nodes \
        --subscription $subscription \
        --partition-key-path /pk \
        --throughput 400 \
        > tmp/cosmos_sql_db_create_transportation_nodes.json
}

info() {
    processed=1
    echo 'az cosmosdb show ...'
    az cosmosdb show \
        --name $cosmos_sql_acct_name \
        --resource-group $cosmos_sql_rg \
        > tmp/cosmos_sql_db_show.json

    # echo 'az cosmosdb list-keys ...'
    # az cosmosdb list-keys \
    #     --name $cosmos_sql_acct_name \
    #     --resource-group $cosmos_sql_rg \
    #     --subscription $subscription \
    #     > tmp/cosmos_sql_db_keys.json

    echo 'az cosmosdb keys list - keys ...'
    az cosmosdb keys list \
        --resource-group $cosmos_sql_rg \
        --name $cosmos_sql_acct_name \
        --type keys \
        > tmp/cosmos_sql_db_keys.json

    echo 'az cosmosdb keys list - connection-strings ...'
    az cosmosdb keys list \
        --resource-group $cosmos_sql_rg \
        --name $cosmos_sql_acct_name \
        --type connection-strings \
        > tmp/cosmos_sql_db_connection_strings.json

    # This command has been deprecated and will be removed in a future release. Use 'cosmosdb keys list' instead.
}

display_usage() {
    echo 'Usage:'
    echo './cosmos_sql.sh create'
    echo './cosmos_sql.sh create_collections'
    echo './cosmos_sql.sh info'
}

# ========== "main" logic below ==========

if [ $arg_count -gt 0 ]
then
    for arg in $@
    do
        if [ $arg == "create" ]; then create; fi 
        if [ $arg == "create_collections" ]; then create_collections; fi 
        if [ $arg == "info" ]; then info; fi 
    done
fi

if [ $processed -eq 0 ]; then display_usage; fi

echo 'done'
