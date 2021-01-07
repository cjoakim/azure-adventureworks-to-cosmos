#!/usr/bin/env bash

# Chris Joakim, Microsoft, 2021/01/07

curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -

#Download appropriate package for the OS version
#Choose only ONE of the following, corresponding to your OS version

#Ubuntu 16.04
# curl https://packages.microsoft.com/config/ubuntu/16.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

#Ubuntu 18.04
#curl https://packages.microsoft.com/config/ubuntu/18.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

curl https://packages.microsoft.com/config/ubuntu/18.04/prod.list > mssql-release.list
cat mssql-release.list
# cat output looks like this:
# deb [arch=amd64] https://packages.microsoft.com/ubuntu/18.04/prod bionic main(py)

sudo cp mssql-release.list 

#Ubuntu 20.04
# curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list

sudo apt-get update
sudo ACCEPT_EULA=Y apt-get install msodbcsql17

cat /etc/odbcinst.ini
# cat output looks like this:
# [ODBC Driver 17 for SQL Server]
# Description=Microsoft ODBC Driver 17 for SQL Server
# Driver=/opt/microsoft/msodbcsql17/lib64/libmsodbcsql-17.6.so.1.1
# UsageCount=1

# optional: for bcp and sqlcmd
# sudo ACCEPT_EULA=Y apt-get install mssql-tools
# echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bash_profile
# echo 'export PATH="$PATH:/opt/mssql-tools/bin"' >> ~/.bashrc
# source ~/.bashrc

# optional: for unixODBC development headers
# sudo apt-get install unixodbc-dev
