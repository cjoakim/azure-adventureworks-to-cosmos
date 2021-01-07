#!/bin/bash

# Bash script with AZ CLI to automate the creation/deletion of my
# Azure Cosmos/Mongo DB.
# Chris Joakim, Microsoft, 2021/01/07
#
# See https://docs.microsoft.com/en-us/cli/azure/?view=azure-cli-latest
# See https://docs.microsoft.com/en-us/azure/cosmos-db/scripts/cli/mongodb/create

# az login

source ./config.sh

arg_count=$#
processed=0

create() {
    processed=1
    echo 'creating cosmos rg: '$cosmos_mongo_rg
    az group create \
        --location $cosmos_mongo_region \
        --name $cosmos_mongo_rg \
        --subscription $subscription \
        > tmp/cosmos_mongo_rg_create.json

    echo 'creating cosmos acct: '$cosmos_mongo_acct_name
    az cosmosdb create \
        --name $cosmos_mongo_acct_name \
        --resource-group $cosmos_mongo_rg \
        --subscription $subscription \
        --locations regionName=$cosmos_mongo_region failoverPriority=0 isZoneRedundant=False \
        --default-consistency-level $cosmos_mongo_acct_consistency \
        --enable-multiple-write-locations true \
        --kind $cosmos_mongo_acct_kind \
        --capabilities EnableMongo \
        > tmp/cosmos_mongo_acct_create.json

    create_db
    create_collections
    info 
}

create_db() {
    processed=1
    echo 'creating cosmos db: '$cosmos_mongo_dbname
    az cosmosdb mongodb database create \
        --resource-group $cosmos_mongo_rg \
        --account-name $cosmos_mongo_acct_name \
        --name $cosmos_mongo_dbname \
        > tmp/cosmos_mongo_db_create.json
}

create_collections() {
    processed=1
    echo 'creating cosmos collection: Customer'
    az cosmosdb mongodb collection create \
        --resource-group $cosmos_mongo_rg \
        --account-name $cosmos_mongo_acct_name \
        --database-name $cosmos_mongo_dbname \
        --name 'Customer' \
        --shard $cosmos_mongo_pk \
        --throughput $cosmos_mongo_ru

    echo 'creating cosmos collection: CustomerOrder'
    az cosmosdb mongodb collection create \
        --resource-group $cosmos_mongo_rg \
        --account-name $cosmos_mongo_acct_name \
        --database-name $cosmos_mongo_dbname \
        --name 'CustomerOrder' \
        --shard $cosmos_mongo_pk \
        --throughput $cosmos_mongo_ru

    echo 'creating cosmos collection: Product'
    az cosmosdb mongodb collection create \
        --resource-group $cosmos_mongo_rg \
        --account-name $cosmos_mongo_acct_name \
        --database-name $cosmos_mongo_dbname \
        --name 'Product' \
        --shard $cosmos_mongo_pk \
        --throughput $cosmos_mongo_ru

    echo 'creating cosmos collection: ProductCategory'
    az cosmosdb mongodb collection create \
        --resource-group $cosmos_mongo_rg \
        --account-name $cosmos_mongo_acct_name \
        --database-name $cosmos_mongo_dbname \
        --name 'ProductCategory' \
        --shard $cosmos_mongo_pk \
        --throughput $cosmos_mongo_ru

    echo 'creating cosmos collection: Data'
    az cosmosdb mongodb collection create \
        --resource-group $cosmos_mongo_rg \
        --account-name $cosmos_mongo_acct_name \
        --database-name $cosmos_mongo_dbname \
        --name 'Data' \
        --shard $cosmos_mongo_pk \
        --throughput $cosmos_mongo_ru
}

info() {
    processed=1
    echo 'az cosmosdb show ...'
    az cosmosdb show \
        --name $cosmos_mongo_acct_name \
        --resource-group $cosmos_mongo_rg \
        > tmp/cosmos_mongo_db_show.json

    echo 'az cosmosdb keys list - keys ...'
    az cosmosdb keys list \
        --resource-group $cosmos_mongo_rg \
        --name $cosmos_mongo_acct_name \
        --type keys \
        > tmp/cosmos_mongo_db_keys.json

    echo 'az cosmosdb keys list - connection-strings ...'
    az cosmosdb keys list \
        --resource-group $cosmos_mongo_rg \
        --name $cosmos_mongo_acct_name \
        --type connection-strings \
        > tmp/cosmos_mongo_db_connection_strings.json

    # This command has been deprecated and will be removed in a future release. Use 'cosmosdb keys list' instead.
}

display_usage() {
    echo 'Usage:'
    echo './cosmos_mongo.sh create'
    echo './cosmos_mongo.sh create_db'
    echo './cosmos_mongo.sh create_collections'
    echo './cosmos_mongo.sh info'
}

# ========== "main" logic below ==========

if [ $arg_count -gt 0 ]
then
    for arg in $@
    do
        if [ $arg == "create" ]; then create; fi 
        if [ $arg == "create_db" ]; then create_db; fi 
        if [ $arg == "create_collections" ]; then create_collections; fi 
        if [ $arg == "info" ];   then info; fi 
    done
fi

if [ $processed -eq 0 ]; then display_usage; fi

echo 'done'
