#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import dbus
import gobject
import sys
import glib
from dbus.mainloop.glib import DBusGMainLoop
import argparse
try:
    import matplotlib.pyplot as plt
except ImportError:
    pass


class WiFiList():
    def __init__(self, watched):
        self.bus = dbus.SystemBus()
        self.NM = 'org.freedesktop.NetworkManager'
        self.bus.add_signal_receiver(
            self.handle_rssi_change, None, self.NM + '.AccessPoint', None, None)
        nm = self.bus.get_object(self.NM, '/org/freedesktop/NetworkManager')
        self.devlist = nm.GetDevices(dbus_interface=self.NM)
        self.rssid = {}
        self.data = {}
        self.watched = watched

    def __repr__(self):
        return "\n".join(["%35s: %5d" % (k, j) for k, j in self.rssid.items()])

    def dbus_get_property(self, prop, member, proxy):
        return proxy.Get(
            self.NM + '.' + member,
            prop,
            dbus_interface='org.freedesktop.DBus.Properties')

    def repopulate_ap_list(self):
        apl = []
        res = []
        for i in self.devlist:
            tmp = self.bus.get_object(self.NM, i)
            if self.dbus_get_property('DeviceType', 'Device', tmp) == 2:
                apl.append(
                    self.bus.get_object(self.NM, i) .GetAccessPoints(
                        dbus_interface=self.NM + '.Device.Wireless'))
        for i in apl:
            for j in i:
                res.append(self.bus.get_object(self.NM, j))
        return res

    def form_rssi_dic(self):
        for i in self.repopulate_ap_list():
            ssid = self.dbus_get_property('Ssid', 'AccessPoint', i)
            strength = self.dbus_get_property('Strength', 'AccessPoint', i)
            self.rssid["".join(["%s" % k for k in ssid])] = int(strength)

    def plotter(self):
        try:
            plt
        except NameError:
            log.error(
                "was unable to use plotting library, try setting up one of: ")
            log.error(
                ("matplotlib (pip install matplotlib)\n"
                 "python-tk (sudo apt-get install python-tk)\n"))
        else:
            graphs = []
            for i in self.data:
                graphs.append(plt.plot(self.data[i], label=i))
            plt.legend(handles=[g[0] for g in graphs])
            plt.show()

    def handle_rssi_change(self, *_):
        self.form_rssi_dic()
        for i in [x for x in self.watched if x in self.rssid]:
            if i in self.data.keys():
                self.data[i].append(self.rssid[i])
            else:
                self.data[i] = []
                self.data[i].append(self.rssid[i])
        return True

    def iowch(self, _arg, _key, loop):
        cmd = sys.stdin.readline()
        if cmd.startswith("stop"):
            print 'stopping the program'
            loop.quit()
            return False
        elif cmd.startswith("print"):
            print self
        elif cmd.startswith("plot"):
            print 'plotting your rssi data'
            self.plotter()
        return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-i",
                        "--interactive",
                        help="start polling RSSI from the networks",
                        action="store_true")
    parser.add_argument("-n",
                        "--networks",
                        nargs="*",
                        help="networks to collect data from",
                        default=[])
    args = parser.parse_args()
    loop = gobject.MainLoop()
    DBusGMainLoop(set_as_default=True)
    wfl = WiFiList(args.networks)
    wfl.form_rssi_dic()
    gobject.io_add_watch(sys.stdin, glib.IO_IN, wfl.iowch, loop)
    print wfl
    if args.interactive:
        loop.run()
