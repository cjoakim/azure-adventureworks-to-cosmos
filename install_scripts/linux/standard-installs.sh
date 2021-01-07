#!/bin/bash

# Bash script to install my standard set of software on an Ubuntu VM.
# Chris Joakim, Microsoft, 2021/01/07

echo '=== apt install python3-pip'
sudo apt update
sudo apt install python3-pip --assume-yes
pip3 --version
pip3 --help

echo '=== apt install python3-venv'
sudo apt update
sudo apt-get install python3-dev python3-venv --assume-yes
sudo apt-get install libpq-dev 
sudo apt-get install unixodbc-dev --assume-yes

echo '=== apt install docker support'
# see https://docs.docker.com/engine/install/ubuntu/
sudo apt-get install apt-transport-https ca-certificates curl gnupg-agent software-properties-common --assume-yes
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get install docker-ce docker-ce-cli containerd.io --assume-yes

echo '=== apt install openjdk-8-jdk'
sudo apt update
sudo apt install openjdk-8-jdk --assume-yes

sudo update-alternatives --config java
# There is only one alternative in link group java (providing /usr/bin/java): /usr/lib/jvm/java-8-openjdk-amd64/jre/bin/java
# Nothing to configure.

which java
which javac 
which jar

java -version

echo '=== apt install maven'
sudo apt update
sudo apt install maven --assume-yes
which mvn 

echo '=== apt install ant'
sudo apt update
sudo apt install ant --assume-yes
which ant 

# see https://docs.microsoft.com/en-us/dotnet/core/install/linux-package-manager-ubuntu-1804
echo '=== dotnet core prerequisites ...'
wget https://packages.microsoft.com/config/ubuntu/18.04/packages-microsoft-prod.deb -O packages-microsoft-prod.deb
sudo dpkg -i packages-microsoft-prod.deb
sudo add-apt-repository universe
sudo apt-get update
sudo apt-get install apt-transport-https --assume-yes
sudo apt-get update

echo '=== apt install dotnet-sdk-3.1'
sudo apt update
sudo apt-get install dotnet-sdk-3.1 --assume-yes

# https://linuxize.com/post/how-to-install-node-js-on-ubuntu-18.04/
echo '=== apt install nodejs'
curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -
sudo apt install nodejs --assume-yes
node --version

# https://linuxize.com/post/how-to-install-postgresql-on-ubuntu-18-04/
echo '=== apt install postgresql'
sudo apt update
sudo apt install postgresql postgresql-contrib --assume-yes

sudo -u postgres psql -c "SELECT version();"

echo '=== apt install redis-server'
sudo apt update
sudo apt install redis-server --assume-yes
redis-server --version

echo '=== apt install jq'
sudo apt update
sudo apt install jq --assume-yes
jq --version

echo '=== mongodb ==='
sudo apt update
sudo apt install -y mongodb

echo ''
echo 'todo - run sudo ./pyenv_install_part1.sh'
echo 'todo - run ./pyenv_install_part2.sh'
echo 'todo - restart shell and run: pyenv install 3.8.6'
echo 'done'
