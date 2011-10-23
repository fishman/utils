#!/usr/bin/env python2

# prfkill - rfkill switch listener
#
# Copyright (C) 2011 Reza Jelveh

import gtk
import gobject

import dbus
import gobject
from dbus.mainloop.glib import DBusGMainLoop

types = dict()
types[1] = "WLAN"
types[2] = "Bluetooth"

appname            = "Purfkill"
bt_icon_enabled    = "/usr/share/icons/ubuntu-mono-light/status/24/bluetooth-active.svg"
bt_icon_disabled   = "/usr/share/icons/ubuntu-mono-light/status/24/bluetooth-disabled.svg"
wlan_icon_enabled  = "/usr/share/icons/ubuntu-mono-light/status/24/nm-device-wireless.svg"
wlan_icon_disabled = "/usr/share/icons/ubuntu-mono-light/status/24/nm-no-connection.svg"

class Display:
    def __init__(self, props, wmname=appname):
        self.window = gtk.Window(gtk.WINDOW_POPUP)
        self.window.set_title(wmname)
        self.window.set_border_width(1)
        self.window.set_default_size(180, -1)
        self.window.set_position(gtk.WIN_POS_CENTER)

        self.window.connect("destroy", lambda x: self.window.destroy())
        timer = gobject.timeout_add(2000, lambda: self.window.destroy())

        wlan_widgetbox = gtk.HBox()
        bt_widgetbox   = gtk.HBox()

        bt_icon  = gtk.Image()
        bt_label = gtk.Label()
        # init bt default settings since it will not be enumerable when disabled, unlike wlan
        bt_icon.set_from_file(bt_icon_disabled)
        bt_label_str = "disabled"

        wlan_icon  = gtk.Image()
        wlan_label = gtk.Label()
        for prop in props:
            if prop['type'] == 1:
                if prop['hard']:
                    wlan_icon.set_from_file(wlan_icon_disabled)
                    wlan_label_str = "disabled"
                else:
                    wlan_icon.set_from_file(wlan_icon_enabled)
                    wlan_label_str = "enabled"

            elif prop['type'] == 2:
                if prop['hard']:
                    bt_icon.set_from_file(bt_icon_disabled)
                    bt_label_str = "disabled"
                else:
                    bt_icon.set_from_file(bt_icon_enabled)
                    bt_label_str = "enabled"


        # set labels
        wlan_label.set_text(wlan_label_str)
        bt_label.set_text(bt_label_str)

        # show widgets
        bt_icon.show()
        bt_label.show()
        wlan_icon.show()
        wlan_label.show()

        wlan_widgetbox.pack_start(wlan_icon)
        wlan_widgetbox.pack_start(wlan_label)
        wlan_widgetbox.pack_start(bt_icon)
        wlan_widgetbox.pack_start(bt_label)
        wlan_widgetbox.show()

        self.window.add(wlan_widgetbox)
        self.window.show_all()

class RfkillAdapter:
    def get_device_props(self, device_name):
        device = bus.get_object("org.freedesktop.URfkill", device_name)
        props = device.GetAll('org.freedesktop.URfkill.Device',
                    dbus_interface="org.freedesktop.DBus.Properties")

        return props

    def device_removed_callback(self, device):
        print 'Device %s was removed' % (device)
        self.print_devices()

    def show_status(self, device):
        devices = self.iface.get_dbus_method('EnumerateDevices')()
        props = []
        for device in devices:
            props.append(self.get_device_props(device))
        Display(props)


    def __init__(self):
        self.proxy = bus.get_object("org.freedesktop.URfkill",
                "/org/freedesktop/URfkill")
        self.iface = dbus.Interface(self.proxy, "org.freedesktop.URfkill")

        #addes two signal listeners
        self.iface.connect_to_signal('DeviceAdded', self.show_status)
        self.iface.connect_to_signal('DeviceChanged', self.show_status)
        # self.iface.connect_to_signal('DeviceRemoved', self.device_removed_callback)



#must be done before connecting to DBus
DBusGMainLoop(set_as_default=True)

bus = dbus.SystemBus()

rf = RfkillAdapter()

#start the main loop
mainloop = gobject.MainLoop()
mainloop.run()
