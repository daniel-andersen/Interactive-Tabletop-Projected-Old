#!/bin/bash

echo "Installing nodejs..."
sudo apt-get install nodejs npm

echo "Installing grunt..."
sudo npm install -g grunt-cli
npm install grunt
npm install grunt-contrib-copy --save-dev
npm install grunt-contrib-connect --save-dev
npm install grunt-coffee-server
npm install

sudo ln -s /usr/bin/nodejs /usr/bin/node

