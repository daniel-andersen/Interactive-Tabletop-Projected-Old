#!/bin/bash

echo "Installing nodejs..."
sudo apt-get install nodejs npm
sudo ln -s /usr/bin/nodejs /usr/bin/node

echo "Installing dependencies..."
sudo npm install -g grunt-cli
npm install
