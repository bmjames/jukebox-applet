Jukebox Applet for GNOME Panel
==============================

At LShift_ we have a jukebox in the office running the erlang-jukebox_ software, and I wanted to be able to see at-a-glance which track it was playing, without needing to open the web interface. This no-frills applet does just that, nothing more.

Installation
------------

Install python-jsonrpc_.

Put ``jukeboxapplet.py`` somewhere on your path, like ``/usr/bin/``

Put JukeboxApplet.server in ``/usr/lib/bonobo/servers/``

.. _LShift: http://www.lshift.net/
.. _erlang-jukebox: http://hg.opensource.lshift.net/erlang-jukebox
.. _python-jsonrpc: http://json-rpc.org/wiki/python-json-rpc

