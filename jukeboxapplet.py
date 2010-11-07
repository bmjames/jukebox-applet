#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pygtk
pygtk.require('2.0')

import gtk
import gnomeapplet
import jsonrpc

RPC_ADDR = "http://jukebox:8888/rpc/jukebox"
TIMEOUT_MS = 5000

def format_track_info(info):
    return "♫ %(trackName)s - %(artistName)s" % info

def pretty_trim(text, max_len=50):
    if len(text) > max_len:
        return text[:max_len-1] + "…"
    return text

class JukeboxApplet(object):
    def __init__(self, applet, iid):
        self.proxy = jsonrpc.ServiceProxy(RPC_ADDR)

        self.label = gtk.Label()
        self.tooltips = gtk.Tooltips()
        applet.add(self.label)
        applet.show_all()
        
        self.set_text()
        gtk.timeout_add(TIMEOUT_MS, self.set_text)

    def set_text(self):
        status = self.get_status()
        self.label.set_text(pretty_trim(status))
        self.tooltips.set_tip(self.label, status)
        return True

    def get_queue(self):
        return self.proxy.get_queue()

    def get_status(self):
        try:
            queue = self.get_queue()
        except:
            return "Could not connect to jukebox"
        if queue['status'] == 'playing':
            return format_track_info(queue['info'])
        return "Jukebox idle"
        
gnomeapplet.bonobo_factory("OAFIID:JukeboxApplet_Factory",
                            gnomeapplet.Applet.__gtype__,
                            "Jukebox Applet", "0.1", JukeboxApplet)

