#!/bin/bash

# Bash script to install the necessary programs for the python "pyodbc"
# library on macOS with the homebrew package manager.
# Chris Joakim, Microsoft, 2021/01/05
#
# See https://docs.microsoft.com/en-us/azure/azure-sql/database/connect-query-python?tabs=macos

brew install unixodbc
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
HOMEBREW_NO_ENV_FILTERING=1 ACCEPT_EULA=Y brew install msodbcsql17 mssql-tools

echo 'done'

