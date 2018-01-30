#!/usr/bin/env python

"""
Corrected, the thread stops now.
"""
import argparse
import sys
import os
from pythonosc import osc_message_builder
from pythonosc import udp_client


from time import sleep

import gi
gi.require_version('Gtk', '3.0')

from gi.repository import Gtk, GObject

#Gtk.gdk.threads_init()

import threading

# uses the package python-xlib
# from http://snipplr.com/view/19188/mouseposition-on-linux-via-xlib/
# or: sudo apt-get install python-xlib
from Xlib import display
screen_root = display.Display().screen().root

old_stdout = sys.stdout
sys.stdout = open(os.devnull, 'w')

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument("--ip", default="192.168.0.104",
      help="The ip of the OSC server")
  parser.add_argument("--port", type=int, default=5001,
      help="The port the OSC server is listening on")
  args = parser.parse_args()

  client = udp_client.SimpleUDPClient(args.ip, args.port)



def mousepos():
    """mousepos() --> (x, y) get the mouse coordinates on the screen (linux, Xlib)."""
    data = screen_root.query_pointer()._data
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
                client.send_message("/MousePos", mousepos() )
                sleep(0.04)
        except (KeyboardInterrupt, SystemExit):
            sys.exit()

    def kill(self):
        self.killed = True

    def stopped(self):
        return self.killed



class PyApp(Gtk.Window):

    def __init__(self):
        super(PyApp, self).__init__()


        self.set_title("Mouse coordinates 0.1")
        self.set_size_request(250, 50)
        #self.set_position(Gtk.WIN_POS_CENTER)
        self.connect("destroy", self.quit)

        label = Gtk.Label()

        self.mouseThread = MouseThread(self, label)
        self.mouseThread.start()

        fixed = Gtk.Fixed()
        fixed.put(label, 10, 10)

        self.add(fixed)
        self.show_all()

    def quit(self, widget):
        self.mouseThread.kill()
        Gtk.main_quit()


if __name__ == '__main__':
    app = PyApp()
    Gtk.main()
