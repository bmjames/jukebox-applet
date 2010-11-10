#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pygtk
pygtk.require('2.0')

import gtk
import gnomeapplet
import gobject
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
        applet.add(self.label)
        applet.show_all()
        
        self.set_text()
        gobject.timeout_add(TIMEOUT_MS, self.set_text)

    def set_text(self):
        status = self.get_status()
        self.label.set_text(pretty_trim(status))
        self.label.set_tooltip_text(status)
        return True

    def get_queue(self):
        return self.proxy.get_queue()

    def get_status(self):
        try:
            queue = self.get_queue()
        except Exception, e:
            print repr(e)
            return "Could not connect to jukebox"
        try:
            if queue['status'] == 'playing':
                return format_track_info(queue['info'])
        except KeyError, e:
            print repr(e)
            print repr(queue)
            return "Could not get track info"
        return "Jukebox idle"

def run_in_window():
    main_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    main_window.set_title('Jukebox Applet')
    main_window.connect("destroy", gtk.main_quit)
    app = gnomeapplet.Applet()
    JukeboxApplet(app, None)
    app.reparent(main_window)
    main_window.show_all()
    gtk.main()

def main():
    import sys
    if len(sys.argv) == 2 and sys.argv[1] in ('-w', '--windowed'):
        run_in_window()
    else:
        gnomeapplet.bonobo_factory("OAFIID:JukeboxApplet_Factory",
                                    gnomeapplet.Applet.__gtype__,
                                    "Jukebox Applet", "0.1", JukeboxApplet)

if __name__ == '__main__':
    main()

