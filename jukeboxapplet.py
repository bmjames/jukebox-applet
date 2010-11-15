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
            LOGGER.error("JSON-RPC error: %s", e)
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
    from optparse import OptionParser

    parser = OptionParser()
    parser.add_option("-w", "--windowed", dest="windowed", default=False,
                      action="store_true", help="run windowed")
    parser.add_option("--loglevel", dest="loglevel", default="ERROR",
                      help="set logging level to LOGLEVEL",
                      metavar="LOGLEVEL")
    opts, _args = parser.parse_args()

    levels = {'DEBUG': logging.DEBUG,
              'INFO': logging.INFO,
              'WARNING': logging.WARNING,
              'ERROR': logging.ERROR,
              'CRITICAL': logging.CRITICAL}
    LOGGER.setLevel(levels.get(opts.loglevel, logging.NOTSET))

    if opts.windowed:
        LOGGER.info("Starting jukebox applet windowed")
        run_in_window()
    else:
        LOGGER.info("Starting jukebox applet via Bonobo")
        gnomeapplet.bonobo_factory("OAFIID:JukeboxApplet_Factory",
            gnomeapplet.Applet.__gtype__, "Jukebox Applet", "0.1",
            jukebox_applet_factory)

if __name__ == '__main__':
    main()

