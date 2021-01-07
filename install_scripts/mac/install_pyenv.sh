#!/bin/bash

# Bash script to install pyenv, with the homebrew package manager, on macOS.
# Chris Joakim, Microsoft, 2021/01/05
#
# See https://binx.io/blog/2019/04/12/installing-pyenv-on-macos/

# list the currently installed libraries
brew list

# uninstall any versions of python that are already installed with homebrew
# for example:
# brew uninstall --ignore-dependencies python@3.8
# brew uninstall --ignore-dependencies python@3.7

# Install dependencies
brew install --force openssl readline sqlite3 xz zlib

# Install pyenv
brew install pyenv pyenv-virtualenv

# Next, add these two lines to the end of your ~/.bash_profile, then restart the shell:
# eval "$(pyenv init -)"
# eval "$(pyenv virtualenv-init -)"

echo 'done'
