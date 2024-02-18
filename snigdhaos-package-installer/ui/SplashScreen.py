import gi
from Functions import os
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk,Gdk

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))

class SplashScreen(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, Gtk.WindowType.POPUP, title="")
        self.set_decorated(False)