Display
=======

In '/boot/config.txt' uncomment:
hdmi_force_hotplug=1
hdmi_group=1
hdmi_mode=28


WiFi (hidden SSID)
==================

See: http://www.bytecreation.com/blog/2014/1/1/raspberry-pi-wifi-configuration-hidden-ssid

Content of /etc/wpa_supplicant/wpa_supplicant.conf:

"""
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
"""

Raspi-config
============

See: http://www.forum-raspberrypi.de/Thread-raspbian-minimal

"""
apt-get -y install lua5.1 triggerhappy dmsetup libdevmapper1.02.1 libparted0debian1 parted
wget http://archive.raspberrypi.org/debian/pool/main/r/raspi-config/raspi-config_20130925-1_all.deb -O raspi-config.deb
dpkg -i raspi-config.deb && rm raspi-config.deb
raspi-config
"""

Camera module
=============

See: https://www.raspberrypi.org/documentation/usage/camera/README.md

Enable camera module in raspi-config

Expand filesystem to fill whole SD card
=======================================

See: http://elinux.org/RPi_raspi-config

"""
sudo raspi-config expand_rootfs
"""

OpenCV 3 + Python 2.7/3
=======================

See: http://www.pyimagesearch.com/2015/07/27/installing-opencv-3-0-for-both-python-2-7-and-python-3-on-your-raspberry-pi-2/

If running out of space while using pip install use custom build directory:

"""
mkdir ~/tmp
pip install -b ~/tmp numpy
"""

