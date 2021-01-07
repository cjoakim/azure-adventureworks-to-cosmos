#!/usr/bin/env bash

# Bash script to install the dependencies for pyenv on Ubuntu Linux;
# run this before executing 'pyenv_install_part2.sh'
# Use: $ sudo ./pyenv_install_part1.sh
# Chris Joakim, Microsoft, 2021/01/07
#
# see https://www.liquidweb.com/kb/how-to-install-pyenv-on-ubuntu-18-04/

apt update -y

apt install -y make build-essential libssl-dev zlib1g-dev \
    libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm libncurses5-dev \
    libncursesw5-dev xz-utils tk-dev libffi-dev liblzma-dev python-openssl
