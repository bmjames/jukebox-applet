#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pygtk
pygtk.require('2.0')

import logging
import logging.handlers

import gtk
import gnomeapplet
import gobject
import jsonrpc

RPC_ADDR = "http://jukebox:8888/rpc/jukebox"
TIMEOUT_MS = 5000
LOG_FILENAME = "/tmp/jukeboxapplet.log"

LOGGER = logging.getLogger('jukeboxapplet')
LOGGER.addHandler(logging.handlers.RotatingFileHandler(LOG_FILENAME))
 
def format_track_info(info):
    return "♫ %(trackName)s - %(artistName)s" % info

def pretty_trim(text, max_len=50):
    if len(text) > max_len:
        return text[:max_len-1] + "…"
    return text

class JukeboxApplet(object):
    def __init__(self, applet):
        self.proxy = jsonrpc.ServiceProxy(RPC_ADDR)

        self.label = gtk.Label()
        applet.add(self.label)
        applet.show_all()
        
        self.update_status_text()
        gobject.timeout_add(TIMEOUT_MS, self.update_status_text)

    def update_status_text(self):
        status = self.get_status()
        self.label.set_text(pretty_trim(status))
        self.label.set_tooltip_text(status)
        LOGGER.info("Updated status text: %s", status)
        return True

    def get_queue(self):
        return self.proxy.get_queue()

    def get_status(self):
        try:
            queue = self.get_queue()
            LOGGER.debug("Got queue info: %s", queue)
        except Exception, e:
            LOGGER.error(" error: %", e)
            return "Could not connect to jukebox"
        try:
            if queue['status'] == 'playing':
                return format_track_info(queue['info'])
        except KeyError, e:
            LOGGER.error("Unexpected structure: %s", e)
            return "Could not get track info"
        return "Jukebox idle"

def jukebox_applet_factory(applet, iid=None):
    JukeboxApplet(applet)

def run_in_window():
    main_window = gtk.Window(gtk.WINDOW_TOPLEVEL)
    main_window.set_title('Jukebox Applet')
    main_window.connect("destroy", gtk.main_quit)
    app = gnomeapplet.Applet()
    jukebox_applet_factory(app)
    app.reparent(main_window)
    main_window.show_all()
    gtk.main()

def main():
    import getopt
    import sys

    # default options
    loglevel, windowed = logging.INFO, False

    try:
        optlist, _args = getopt.getopt(sys.argv[1:], 'w', ['windowed', 'loglevel='])
        for opt, arg in optlist:
            if opt == '--loglevel':
                loglevel = {'debug': logging.DEBUG,
                    'info': logging.INFO,
                    'warning': logging.WARNING,
                    'error': logging.ERROR,
                    'critical': logging.CRITICAL}.get(arg.lower(), logging.NOTSET)
            if opt in ('-w', '--windowed'):
                windowed = True
    except getopt.GetoptError as getopt_error:
        # probably caused by GNOME passing an option we didn't expect
        LOGGER.debug(getopt_error)

    LOGGER.setLevel(loglevel)

    if windowed:
        LOGGER.info("Starting jukebox applet windowed")
        run_in_window()
    else:
        LOGGER.info("Starting jukebox applet via Bonobo")
        gnomeapplet.bonobo_factory("OAFIID:JukeboxApplet_Factory",
            gnomeapplet.Applet.__gtype__, "Jukebox Applet", "0.1",
            jukebox_applet_factory)

if __name__ == '__main__':
    main()

