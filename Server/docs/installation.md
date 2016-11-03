Installation of Raspberry Pi
============================

Setup display
-------------

In /boot/config.txt insert/edit:

`
disable_overscan=1
hdmi_force_hotplug=1
hdmi_group=2
hdmi_mode=28
hdmi_drive=2
`

Setup WiFi
----------

`
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
        ssid="Daniel & Annie"
        scan_ssid=1
        psk="<password>"
        proto=RSN
        key_mgmt=WPA-PSK
        pairwise=CCMP
        auth_alg=OPEN
}
`

Update system
-------------

    $ sudo apt-get update
    $ sudo apt-get upgrade --fix-missing

Install additional packages for hardware accelerated OpenGL:

    $ sudo apt-get install xcompmgr

Setup system
------------

Run raspi-config:

    $ sudo raspi-config

Choose:

* Expand Filesystem
* Enable Camera
* Internationalisation Options -> Change Locale / keyboard layout
* Experimental:
  * Advanced Options -> GL Driver

Install X11
-----------

    $ sudo apt-get install xserver-xorg xinit x11-xserver-utils matchbox xwit feh --fix-missing

Grant all access to start X11:

    $ sudo dpkg-reconfigure x11-common

Move .xinitrc and rc.local into place:

    ~/.xinitrc
    /etc/rc.local

Install nginx webserver
-----------------------

    $ sudo apt-get install nginx

Move nginx.conf into place:

    /etc/nginx/nginx.conf

Install npm
-----------

    $ sudo apt-get install npm --fix-missing

Server
------

Install git:

    $ sudo apt-get install git

Setup ssh-keys and clone Magic Lamp:

    $ git clone git@github.com:daniel-andersen/Interactive-Tabletop-Projected.git
    $ mv Interactive-Tabletop-Projected magic_lamp

Install dependencies:

    $ sudo apt-get install build-essential cmake pkg-config  # Build essentials
    $ sudo apt-get install libjpeg8-dev libjasper-dev libpng12-dev  # Image handling
    $ sudo apt-get install libatlas-base-dev gfortran   # For optimizations within OpenCV
    $ sudo apt-get install python-pip python-dev python-picamera
    $ ./install_packages.sh

Install OpenCV:

    $ wget -O opencv-2.4.10.zip http://sourceforge.net/projects/opencvlibrary/files/opencv-unix/2.4.10/opencv-2.4.10.zip/download
    $ unzip opencv-2.4.10.zip
    $ cd opencv-2.4.10

    $ mkdir build
    $ cd build
    $ cmake -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D BUILD_NEW_PYTHON_SUPPORT=ON -D INSTALL_C_EXAMPLES=OFF -D INSTALL_PYTHON_EXAMPLES=OFF  -D BUILD_EXAMPLES=OFF ..
    $ sudo make install
    $ sudo ldconfig

Client
------

Install dependencies:

    $ cd magic_lamp/Client
    $ sudo ./install_dependencies.sh

Install browser
---------------

    $ git clone git@github.com:daniel-andersen/kiosk-browser.git
    $ sudo apt-get install libwebkit-dev
    $ cd kiosk-browser
    $ make

