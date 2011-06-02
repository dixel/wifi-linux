#!/usr/bin/env python
#-*- encoding: utf-8 -*-
import dbus
bus = dbus.SystemBus()
NM = 'org.freedesktop.NetworkManager'
nm = bus.get_object(NM, '/org/freedesktop/NetworkManager')
devlist = nm.GetDevices(dbus_interface = NM)
wifiadl = []
for i in devlist:
    if bus.get_object(NM, i).Get(NM+'.Device', 'DeviceType', dbus_interface = 'org.freedesktop.DBus.Properties') == 2:
        wifiadl.append(bus.get_object(NM, i))

apl = [i.GetAccessPoints(dbus_interface = NM+'.Device.Wireless') for i in wifiadl]

rssid = {}
for ads in apl:
    for i in ads:
        ssid = bus.get_object(NM, i).Get(NM+'.AccessPoint', 'Ssid', dbus_interface = 'org.freedesktop.DBus.Properties')
        strength = bus.get_object(NM, i).Get(NM+'.AccessPoint', 'Strength', dbus_interface = 'org.freedesktop.DBus.Properties')
        rssid["".join(["%s" % k for k in ssid])] =  int(strength)

print "\n".join(["%20s: %5d" % (k, j) for k, j in rssid.items()])
