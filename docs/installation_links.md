Boot in fullscreen Chromium kiosk mode
======================================

http://blogs.wcode.org/2013/09/howto-boot-your-raspberry-pi-into-a-fullscreen-browser-kiosk/


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

Upgrade to Jessie (from Wheezy)
===============================

"""
sudo vi /etc/apt/sources.list
sudo apt-get update
sudo apt-get install python3 python3-dev
sudo apt-get upgrade
sudo apt-get remove --purge python3.2 python3.2-dev # If already installed python 3.2
"""

Python 3
========

See: http://www.pyimagesearch.com/2015/07/27/installing-opencv-3-0-for-both-python-2-7-and-python-3-on-your-raspberry-pi-2/

If running out of space while using pip install use custom build directory:

"""
mkdir ~/tmp
pip install -b ~/tmp numpy
"""

OpenCV 3
========

Use above link: http://www.pyimagesearch.com/2015/07/27/installing-opencv-3-0-for-both-python-2-7-and-python-3-on-your-raspberry-pi-2/

If anything goes wrong, use: http://raspberrypi.stackexchange.com/questions/27232/installing-opencv-3-0-on-raspberry-pi-b

Turn perf_test off.

If seeing:

"""
[ 21%] Building CXX object modules/videoio/CMakeFiles/opencv_videoio.dir/src/cap_ffmpeg.cpp.o
In file included from /home/sysop/opencv/modules/videoio/src/cap_ffmpeg.cpp:45:0:
/home/sysop/opencv/modules/videoio/src/cap_ffmpeg_impl.hpp:1546:71: error: use of enum ‘AVCodecID’ without previous declaration
/home/sysop/opencv/modules/videoio/src/cap_ffmpeg_impl.hpp:1556:83: error: use of enum ‘AVCodecID’ without previous declaration
make[2]: *** [modules/videoio/CMakeFiles/opencv_videoio.dir/src/cap_ffmpeg.cpp.o] Error 1
make[1]: *** [modules/videoio/CMakeFiles/opencv_videoio.dir/all] Error 2
make: *** [all] Error 2
"""

See: http://stackoverflow.com/questions/31663498/opencv-3-0-0-make-error-with-ffmpeg/31818445#31818445

If seeing:

"""
c++: internal compiler error: Segmentation fault (program cc1plus)
"""

See last answer in: https://bitcointalk.org/index.php?topic=304389.0

