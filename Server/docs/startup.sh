#!/bin/bash

export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python3
export WORKON_HOME=$HOME/.virtualenvs
source /usr/local/bin/virtualenvwrapper.sh

# Hide the cursor (move it to the bottom-right, comment out if you want mouse interaction)
#xwit -root -warp $( cat /sys/module/*fb*/parameters/fbwidth ) $( cat /sys/module/*fb*/parameters/fbheight )

# Show splash
feh -F ~/magic_lamp/Server/assets/splash.png & feh_pid=$!

# Virtualenv
workon cv

# Update source code to newest
cd ~/magic_lamp/
git fetch --all
git reset --hard origin/master

# Start server
cd ~/magic_lamp/Server/src
python -u main.py > ~/log/server.log 2>&1 &
#python -m trace -c -t -C ~/coverage main.py > ~/log/server.log 2>&1 &

# Start client
cd ~/magic_lamp/Client
grunt run > ~/log/client.log 2>&1 &

# Wait for client
up=0
while [ $up -eq 0 ]
do
  echo "Waiting for client..."
  sleep 1
  wget http://localhost:9002/content/Menu/index.html -O - 2>/dev/null | grep "body" > /dev/null && up=1
done

# Start the browser
~/kiosk-browser/browser http://localhost:9002/content/Menu/index.html & browser_pid=$!

sleep 2
kill -9 $feh_pid

wait $browser_pid

