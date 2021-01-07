#!/bin/bash

# Bash script with AZ CLI to automate login and set the current subscription.
# Chris Joakim, Microsoft, 2021/01/07

source ./config.sh

az login 

az account list --output table

az account set --subscription $AZURE_SUBSCRIPTION_ID

az account show

echo 'done'
