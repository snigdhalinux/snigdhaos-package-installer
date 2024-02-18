import gi
from Functions import os
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk,Gdk,GdkPixbuf

base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))

class SplashScreen(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, Gtk.WindowType.POPUP, title="")
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_size_request(1280, 720)
        self.set_position(Gtk.WindowPosition.CENTER)
        main_vbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing = 1)
        self.add(main_vbox)
        self.image = Gtk.Image()
        spimage = GdkPixbuf.Pixbuf().new_from_file_at_size(
            base_dir + "/image/snigdhaos-splash.png"
        )
        self.image.set_from_pixbuf(spimage)
        main_vbox.pack_start(self.image, True, True, 0)
        self.show_all()

