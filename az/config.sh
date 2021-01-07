#!/bin/bash

# Bash shell that defines parameters and environment variables used 
# in this app, and is "sourced" by the other scripts in this repo.
# Chris Joakim, Microsoft, 2021/01/07

export subscription=$AZURE_SUBSCRIPTION_ID
export user=$USER
export resource_group="cjoakimawdb2cosmos"
export primary_region="eastus"
export secondary_region="westus"
#
export cosmos_mongo_region=$primary_region
export cosmos_mongo_locations=""
export cosmos_mongo_rg=$resource_group
export cosmos_mongo_acct_name="cjoakimcosmosmongo2"
export cosmos_mongo_acct_consistency="Session"    # {BoundedStaleness, ConsistentPrefix, Eventual, Session, Strong}
export cosmos_mongo_acct_kind="MongoDB"  # {GlobalDocumentDB, MongoDB, Parse}
export cosmos_mongo_dbname="dev"
export cosmos_mongo_pk="pk"
export cosmos_mongo_ru="400"
#
export cosmos_sql_region=$primary_region
export cosmos_sql_rg=$resource_group
export cosmos_sql_acct_name="cjoakimcosmossql2"
export cosmos_sql_acct_consistency="Session"    # {BoundedStaleness, ConsistentPrefix, Eventual, Session, Strong}
export cosmos_sql_acct_kind="GlobalDocumentDB"  # {GlobalDocumentDB, MongoDB, Parse}
export cosmos_sql_dbname="dev"
#
export sqldb_region=$primary_region
export sqldb_rg=$resource_group
export sqldb_server="cjoakimazsqlsrv2"
export sqldb_dbname="cjoakimazsqldb2"
export sqldb_admin_user=$AZURE_SQL_USER
export sqldb_admin_pass=$AZURE_SQL_PASS
export sqldb_start_ip="0.0.0.0"
export sqldb_end_ip="255.255.255.255"
