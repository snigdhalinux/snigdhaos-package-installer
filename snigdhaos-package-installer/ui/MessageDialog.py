import os
import gi
import Functions as fn
gi.require_version("Gtk","3.0")
from gi.repository import Gtk
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))

class MessageDialog(Gtk.Dialog):
    def __init__(
            self,
            title,
            subtitle,
            first_msg,
            second_msg,
            message_type,
            extended,
    ):
        Gtk.Dialog.__init__(self)
        headerbar = Gtk.HeaderBar()
        headerbar.set_title(title)
        headerbar.set_show_close_button(True)
        self.set_resizable(True)
        self.set_border_width(10)
        self.set_titlebar(headerbar)
        btn_ok = Gtk.Button(Label = "OK")
        btn_ok.set_size_request(100,30)
        btn_ok.connect("clicked",on_message_dialog_ok_response,self) #spicreate001 -> Functions
        btn_ok.set_halign(Gtk.Align.END)
        self.set_icon_from_file(os.path.join(base_dir, "images/spi.png"))
        infobar = Gtk.InfoBar()
        if message_type == "info":
            infobar.set_name("infobar_info")
        if message_type == "warning":
            infobar.set_name("infobar_warning")
        if message_type == "error":
            infobar.set_name("infobar_error")
        lbl_title_message = Gtk.Label(xlaign=0,yalign=0)
        lbl_title_message.set_markup("%s" % subtitle)
        content = infobar.get_content_area()
        content.add(lbl_title_message)
        infobar.set_revealed(True)
        lbl_padding1 = Gtk.Label(xalign=0,yalign=0)
        lbl_padding1.set_text("")
        lbl_padding2 = Gtk.Label(xalign=0,yalign=0)
        lbl_padding2.set_text("")
        grid_message = Gtk.Grid()
        grid_message.attach(infobar, 0, 0, 1 , 1)
        grid_message.attach(lbl_padding1, 0, 1, 1, 1)
        if extended is True:
            scrolled_window = Gtk.ScrolledWindow()
            textview = Gtk.TextView()
            textview.set_property("editable", False)
            textview.set_property("monospace", True)
            textview.set_border_width(10)
            textview.set_vexpand(True)
            textview.set_hexpand(True)
            msg_buffer = textview.get_buffer()
            msg_buffer.insert(
                msg_buffer.get_end_iter(),
                "Event timestamp = %s\n" % fn.datetime.now().strftime("%Y-%m-%d-%H-%M-%S"),
            )
            

