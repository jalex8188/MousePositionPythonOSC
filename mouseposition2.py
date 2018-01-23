#!/usr/bin/env python

"""
Corrected, the thread stops now.
"""
import argparse
import sys
import os
import time
import random

from OSC import OSCClient, OSCMessage
from pythonosc import osc_message_builder
from pythonosc import udp_client

from time import sleep

import gtk
gtk.gdk.threads_init()

import threading

# uses the package python-xlib
# from http://snipplr.com/view/19188/mouseposition-on-linux-via-xlib/
# or: sudo apt-get install python-xlib
from Xlib import display


old_stdout = sys.stdout
sys.stdout = open(os.devnull, 'w')

client = OSCClient()
client.connect( ("192.168.1.125", 7110) )


def mousepos():
    """mousepos() --> (x, y) get the mouse coordinates on the screen (linux, Xlib)."""
    data = display.Display().screen().root.query_pointer()._data
    return data["root_x"], data["root_y"]


class MouseThread(threading.Thread):
    def __init__(self, parent, label):
        threading.Thread.__init__(self)
        self.label = label
        self.killed = False

    def run(self):
        try:
            while True:
                if self.stopped():
                    break
                text = "{0}".format(mousepos())
                self.label.set_text(text)
                sleep(0.2)
                client.send( OSCMessage("/MousePos", ["{0}".format(mousepos())] ) )
        except (KeyboardInterrupt, SystemExit):
            sys.exit()




    def kill(self):
        self.killed = True

    def stopped(self):
        return self.killed



class PyApp(gtk.Window):

    def __init__(self):
        super(PyApp, self).__init__()

        self.set_title("Mouse coordinates 0.1")
        self.set_size_request(250, 50)
        self.set_position(gtk.WIN_POS_CENTER)
        self.connect("destroy", self.quit)

        label = gtk.Label()

        self.mouseThread = MouseThread(self, label)
        self.mouseThread.start()


        fixed = gtk.Fixed()
        fixed.put(label, 10, 10)

        self.add(fixed)
        self.show_all()

    def quit(self, widget):
        self.mouseThread.kill()
        gtk.main_quit()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--ip", default="192.168.1.125",
      help="The ip of the OSC server")
    parser.add_argument("--port", type=int, default=5005,
      help="The port the OSC server is listening on")
    args = parser.parse_args()

    client = udp_client.SimpleUDPClient(args.ip, args.port)

    client.send_message("/MousePosition", random.random())
    app = PyApp()
    gtk.main()
