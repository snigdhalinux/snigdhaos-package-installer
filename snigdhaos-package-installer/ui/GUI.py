# Author : Abhiraj Roy <icon@snigdhaos.org>
# Author URL : https://icon.snigdhaos.org

import Functions as fn
from ui.AppFrameGUI import AppFrameGUI
from multiprocessing import cpu_count
from queue import Queue
from threading import Thread

base_dir = fn.os.path.abspath(fn.os.path.join(fn.os.path.dirname(__file__), ".."))
base_dir = fn.os.path.dirname(fn.os.path.realpath(__file__))


class GUI_Worker(Thread):
    def __init__(self, queue):
        Thread.__init__(self)
        self.queue = queue

    def run(self):
        while True:
            items = self.queue.get()

            try:
                if items is not None:
                    self, Gtk, vbox_stack, category, packages = items
                    AppFrameGUI.build_ui_frame(
                        self,
                        Gtk,
                        vbox_stack,
                        category,
                        packages,
                    )
            except Exception as e:
                fn.logger.error("Exception in GUI_Worker(): %s" % e)
            finally:
                if items is None:
                    fn.logger.debug("Stopping GUI Worker thread")
                    self.queue.task_done()
                    return False
                self.queue.task_done()

class GUI:
    def setup_gui_search(
        self,
        Gtk,
        Gdk,
        GdkPixbuf,
        base_dir,
        os,
        Pango,
        search_results,
        search_term,
        settings,
    ):
        try:
            if self.search_activated == False:
                self.remove(self.vbox)
            else:
                self.remove(self.vbox_search)
            fn.get_current_installed()
            setup_headerbar(self, Gtk, settings)

            hbox0 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            self.notification_revealer = Gtk.Revealer()
            self.notification_revealer.set_reveal_child(False)
            self.notification_label = Gtk.Label()

            pb_panel = GdkPixbuf.Pixbuf().new_from_file(base_dir + "/images/panel.png")
            panel = Gtk.Image().new_from_pixbuf(pb_panel)

            overlay_frame = Gtk.Overlay()
            overlay_frame.add(panel)
            overlay_frame.add_overlay(self.notification_label)
            self.notification_revealer.add(overlay_frame)
            hbox0.pack_start(self.notification_revealer, True, False, 0)

            self.vbox_search = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            vbox1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

            self.vbox_search.pack_start(hbox, True, True, 0)
            self.add(self.vbox_search)

            stack = Gtk.Stack()
            stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)
            stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
            stack.set_transition_duration(350)

            vbox_stack = []
            stack_item = 0

            # Max Threads
            """
                Fatal Python error: Segmentation fault
                This error happens randomly, due to the for loop iteration on the cpu_count
                old code: for x in range(cpu_count()):
            """
            search_worker = GUI_Worker(self.queue)
            search_worker.name = "thread_GUI_search_worker"
            # Set the worker to be True to allow processing, and avoid Blocking
            # search_worker.daemon = True
            search_worker.start()


            for category in search_results:
                # @eshanized update yaml along with GUI.py

                # subcategory = search_results[category][0].subcategory
                vbox_stack.append(
                    Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
                )
                stack.add_titled(
                    vbox_stack[stack_item],
                    str("stack" + str(len(vbox_stack))),
                    category,
                )

                # subcategory_desc = search_results[category][0].subcategory_description
                search_res_lst = search_results[category]

                # Multithreading!

                self.queue.put(
                    (
                        self,
                        Gtk,
                        vbox_stack[stack_item],
                        category,
                        search_res_lst,
                    )
                )

                stack_item += 1

            # send a signal that no further items are to be put on the queue
            self.queue.put(None)
            # safety to ensure that we finish threading before we continue on.
            self.queue.join()
            fn.logger.debug("GUI Worker thread completed")

            stack_switcher = Gtk.StackSidebar()
            stack_switcher.set_name("sidebar")
            stack_switcher.set_stack(stack)

            ivbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            pixbuf = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(base_dir, "images/spi.png"), 45, 45
            )
            image = Gtk.Image().new_from_pixbuf(pixbuf)

            # remove the focus on startup from search entry
            ivbox.set_property("can-focus", True)
            Gtk.Window.grab_focus(ivbox)

            btn_recache = Gtk.Button(label="Recache Applications")
            btn_recache.connect("clicked", self.recache_clicked)
            btnReCache.set_property("has-tooltip", True)
            btnReCache.connect("query-tooltip", self.tooltip_callback,
                      "Refresh the application cache")

            if not (
                fn.check_package_installed("snigdhaos-keyring")
                or fn.check_package_installed("snigdhaos-mirrorlist")
            ):
                self.btnRepos = Gtk.Button(label="Add Snigdha OS Repo")
                self.btnRepos._value = 1
            else:
                self.btnRepos = Gtk.Button(label="Remove Snigdha OS Repo")
                self.btnRepos._value = 2
            
            self.btnRepos.set_size_request(100, 30)
            self.btnRepos.connect("clicked", self.on_repos_clicked)

            btn_quit_app = Gtk.Button(label="Exit")
            btn_quit_app.set_size_request(100, 30)
            btn_quit_app.connect("clicked", self.on_close, "delete-event")
            btn_context = btn_quit_app.get_style_context()
            btn_context.add_class("destructive-action")

            self.searchentry = Gtk.SearchEntry()
            self.searchentry.set_text(search_term)
            self.searchentry.connect("activate", self.on_search_activated)
            self.searchentry.connect("icon-release", self.on_search_cleared)

            iv_searchbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

            hbox1 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
            hbox2 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)
            hbox3 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=2)

            hbox3.pack_start(btnReCache, False, False, 0)

            iv_searchbox.pack_start(self.searchentry, False, False, 0)

            ivbox.pack_start(image, False, False, 0)
            ivbox.pack_start(iv_searchbox, False, False, 0)
            ivbox.pack_start(stack_switcher, True, True, 0)

            ivbox.pack_start(btn_quit_app, False, False, 0)

            vbox1.pack_start(hbox0, False, False, 0)
            vbox1.pack_start(stack, True, True, 0)

            hbox.pack_start(ivbox, False, True, 0)
            hbox.pack_start(vbox1, True, True, 0)

            stack.set_hhomogeneous(False)
            stack.set_vhomogeneous(False)

            self.show_all()

        except Exception as e:
            fn.logger.error("Found Exception in GUISearch(): %s" % e)

    def setup_gui(self, Gtk, Gdk, GdkPixbuf, base_dir, os, Pango, settings):
        try:
            if self.search_activated:
                self.remove(self.vbox_search)
                self.show_all()
            fn.get_current_installed()

            setup_headerbar(self, Gtk, settings)

            hbox0 = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)

            self.notification_revealer = Gtk.Revealer()
            self.notification_revealer.set_reveal_child(False)

            self.notification_label = Gtk.Label()

            pb_panel = GdkPixbuf.Pixbuf().new_from_file(base_dir + "/images/panel.png")
            panel = Gtk.Image().new_from_pixbuf(pb_panel)

            overlay_frame = Gtk.Overlay()
            overlay_frame.add(panel)
            overlay_frame.add_overlay(self.notification_label)

            self.notification_revealer.add(overlay_frame)

            hbox0.pack_start(self.notification_revealer, True, False, 0)

            self.vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            vbox1 = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
            hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)

            self.vbox.pack_start(hbox, True, True, 0)
            self.add(self.vbox)

            # This section sets up the tabs, and the array for dealing with the tab content
            
            yaml_files_unsorted = []
            path = base_dir + "/yaml/"
            for file in os.listdir(path):
                if file.endswith(".yaml"):
                    yaml_files_unsorted.append(file)
                else:
                    print(
                        "Unsupported configuration file type. Please contact Snigdha OS Support."
                    )
            # Need to sort the list (Or do we? I choose to)
            yaml_files = sorted(yaml_files_unsorted)
        
            # Check github for updated files
            fn.check_github(yaml_files)

            stack = Gtk.Stack()
            stack.set_transition_type(Gtk.StackTransitionType.SLIDE_UP_DOWN)
            stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
            stack.set_transition_duration(350)

            vbox_stack = []
            stack_item = 0

            # Max Threads
            """
                Fatal Python error: Segmentation fault
                This error happens randomly, due to the for loop iteration on the cpu_count
                old code: for x in range(cpu_count()):
            """

            # spawn only 1 GUI_Worker threads, as any number greater causes a Segmentation fault

            worker = GUI_Worker(self.queue)
            worker.name = "thread_GUI_Worker"
            # Set the worker to be True to allow processing, and avoid Blocking
            worker.daemon = True
            worker.start()

            for category in self.packages:
                # NOTE: IF the yaml file name standard changes, be sure to update this, or weirdness will follow.

                # this is the side stack listing all categories
                vbox_stack.append(
                    Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
                )
                stack.add_titled(
                    vbox_stack[stack_item],
                    str("stack" + str(len(vbox_stack))),
                    category,
                )

                packages_lst = self.packages[category]

                # Multithreading!
                self.queue.put(
                    (
                        self,
                        Gtk,
                        vbox_stack[stack_item],
                        category,
                        packages_lst,
                    )
                )
                stack_item += 1

            # send a signal that no further items are to be put on the queue
            self.queue.put(None)
            # safety to ensure that we finish threading before we continue on.

            self.queue.join()
            fn.logger.debug("GUI Worker thread completed")

            stack_switcher = Gtk.StackSidebar()
            stack_switcher.set_name("sidebar")
            stack_switcher.set_stack(stack)

            ivbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
            pixbuf = GdkPixbuf.Pixbuf().new_from_file_at_size(
                os.path.join(base_dir, "images/spi.png"), 45, 45
            )
            image = Gtk.Image().new_from_pixbuf(pixbuf)

            # remove the focus on startup from search entry
            ivbox.set_property("can-focus", True)
            Gtk.Window.grab_focus(ivbox)

            btnReCache = Gtk.Button(label="Recache Applications")
            btnReCache.connect("clicked", self.recache_clicked)
            btnReCache.set_property("has-tooltip", True)
            btnReCache.connect("query-tooltip", self.tooltip_callback,
                      "Refresh the application cache")

            btn_quit_app = Gtk.Button(label="Exit")
            btn_quit_app.set_size_request(100, 30)
            btn_quit_app.connect("clicked", self.on_close, "delete-event")
            btn_context = btn_quit_app.get_style_context()
            btn_context.add_class("destructive-action")

            self.searchentry = Gtk.SearchEntry()
            self.searchentry.set_placeholder_text("Search...")
            self.searchentry.connect("activate", self.on_search_activated)
            self.searchentry.connect("icon-release", self.on_search_cleared)

            ivsearchbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

            ivsearchbox.pack_start(self.searchentry, False, False, 0)

            ivbox.pack_start(image, False, False, 0)
            ivbox.pack_start(ivsearchbox, False, False, 0)
            ivbox.pack_start(stack_switcher, True, True, 0)
            ivbox.pack_start(btn_quit_app, False, False, 0)

            vbox1.pack_start(hbox0, False, False, 0)
            vbox1.pack_start(stack, True, True, 0)

            hbox.pack_start(ivbox, False, True, 0)
            hbox.pack_start(vbox1, True, True, 0)

            stack.set_hhomogeneous(False)
            stack.set_vhomogeneous(False)

            if self.search_activated:
                self.show_all()

        except Exception as e:
            fn.logger.error("Exception in GUI(): %s" % e)


# setup headerbar including popover settings
def setup_headerbar(self, Gtk, settings):
    try:
        header_bar_title = "Snigdha OS Package Installer"
        headerbar = Gtk.HeaderBar()
        headerbar.set_title(header_bar_title)
        headerbar.set_show_close_button(True)

        self.set_titlebar(headerbar)

        toolbutton = Gtk.ToolButton()
        # icon-name open-menu-symbolic / open-menu-symbolic.symbolic
        toolbutton.set_icon_name("open-menu-symbolic")

        toolbutton.connect("clicked", self.on_settings_clicked)

        headerbar.pack_end(toolbutton)

        self.popover = Gtk.Popover()
        self.popover.set_relative_to(toolbutton)

        vbox = Gtk.Box(spacing=0, orientation=Gtk.Orientation.VERTICAL)
        vbox.set_border_width(15)

        # switches

        # switch to display package versions
        self.switch_package_version = Gtk.Switch()

        if settings != None:
            if settings["Display Package Versions"]:
                self.display_versions = settings["Display Package Versions"]

        if self.display_versions == True:
            self.switch_package_version.set_active(True)
        else:
            self.switch_package_version.set_active(False)

        self.switch_package_version.connect("notify::active", self.version_toggle)

        self.switch_snigdhaos_keyring = Gtk.Switch()

        if (
            fn.check_package_installed("snigdhaos-keyring") is False
            or fn.verify_snigdhaos_pacman_conf() is False
        ):
            self.switch_snigdhaos_keyring.set_state(False)

        else:
            self.switch_snigdhaos_keyring.set_state(True)

        self.switch_snigdhaos_keyring.connect("state-set", self.snigdhaos_keyring_toggle)

        self.switch_snigdhaos_mirrorlist = Gtk.Switch()

        if (
            fn.check_package_installed("snigdhaos-mirrorlist") is False
            or fn.verify_snigdhaos_pacman_conf() is False
        ):
            self.switch_snigdhaos_mirrorlist.set_state(False)

        else:
            self.switch_snigdhaos_mirrorlist.set_state(True)

        self.switch_snigdhaos_mirrorlist.connect("state-set", self.snigdhaos_mirrorlist_toggle)

        # switch to display package progress window
        self.switch_package_progress = Gtk.Switch()

        if settings != None:
            if settings["Display Package Progress"]:
                self.display_package_progress = settings["Display Package Progress"]

        if self.display_package_progress == True:
            self.switch_package_progress.set_active(True)
        else:
            self.switch_package_progress.set_active(False)
        self.switch_package_progress.connect(
            "notify::active", self.package_progress_toggle
        )

        # modalbuttons

        # button to open the pacman log monitoring dialog
        self.modelbtn_pacmanlog = Gtk.ModelButton()
        self.modelbtn_pacmanlog.connect("clicked", self.on_pacman_log_clicked)
        self.modelbtn_pacmanlog.set_name("modelbtn_popover")
        self.modelbtn_pacmanlog.props.centered = False
        self.modelbtn_pacmanlog.props.text = "Open Pacman Log File"

        # button to display installed packages window
        modelbtn_packages_export = Gtk.ModelButton()
        modelbtn_packages_export.connect("clicked", self.on_packages_export_clicked)
        modelbtn_packages_export.set_name("modelbtn_popover")
        modelbtn_packages_export.props.centered = False
        modelbtn_packages_export.props.text = "Show Installed Packages"

        # button to display import packages window
        modelbtn_packages_import = Gtk.ModelButton()
        modelbtn_packages_import.connect("clicked", self.on_packages_import_clicked)
        modelbtn_packages_import.set_name("modelbtn_popover")
        modelbtn_packages_import.props.centered = False
        modelbtn_packages_import.props.text = "Import Packages"

        # button to show about dialog
        modelbtn_about_app = Gtk.ModelButton()
        modelbtn_about_app.connect("clicked", self.on_about_app_clicked)
        modelbtn_about_app.set_name("modelbtn_popover")
        modelbtn_about_app.props.centered = False
        modelbtn_about_app.props.text = "About Sofirem"

        # button to show iso package lists window
        modelbtn_iso_packages_list = Gtk.ModelButton()
        modelbtn_iso_packages_list.connect(
            "clicked", self.on_snigdhaos_iso_packages_clicked
        )
        modelbtn_iso_packages_list.set_name("modelbtn_popover")
        modelbtn_iso_packages_list.props.centered = False
        modelbtn_iso_packages_list.props.text = "Explore Snigdha OS ISO Packages"

        # button to show package search window
        modelbtn_package_search = Gtk.ModelButton()
        modelbtn_package_search.connect("clicked", self.on_package_search_clicked)
        modelbtn_package_search.set_name("modelbtn_popover")
        modelbtn_package_search.props.centered = False
        modelbtn_package_search.props.text = "Open Package Search"

        # grid for the switch options
        grid_switches = Gtk.Grid()
        grid_switches.set_row_homogeneous(True)

        lbl_package_version = Gtk.Label(xalign=0)
        lbl_package_version.set_text("Display Package Versions")

        lbl_package_version_padding = Gtk.Label(xalign=0)
        lbl_package_version_padding.set_text("  ")

        lbl_package_progress = Gtk.Label(xalign=0)
        lbl_package_progress.set_text("Display Package Progress")

        lbl_package_progress_padding = Gtk.Label(xalign=0)
        lbl_package_progress_padding.set_text("  ")

        lbl_snigdhaos_keyring = Gtk.Label(xalign=0)
        lbl_snigdhaos_keyring.set_text("Import Snigdha OS Keyring")

        lbl_snigdhaos_keyring_padding = Gtk.Label(xalign=0)
        lbl_snigdhaos_keyring_padding.set_text("  ")

        lbl_snigdhaos_mirrorlist = Gtk.Label(xalign=0)
        lbl_snigdhaos_mirrorlist.set_text("Import Snigdha OS Mirrorlist")

        lbl_snigdhaos_mirrorlist_padding = Gtk.Label(xalign=0)
        lbl_snigdhaos_mirrorlist_padding.set_text("  ")

        grid_switches.attach(lbl_package_version, 0, 1, 1, 1)
        grid_switches.attach_next_to(
            lbl_package_version_padding,
            lbl_package_version,
            Gtk.PositionType.RIGHT,
            1,
            1,
        )

        grid_switches.attach_next_to(
            self.switch_package_version,
            lbl_package_version_padding,
            Gtk.PositionType.RIGHT,
            1,
            1,
        )

        grid_switches.attach(lbl_package_progress, 0, 2, 1, 1)
        grid_switches.attach_next_to(
            lbl_package_progress_padding,
            lbl_package_progress,
            Gtk.PositionType.RIGHT,
            1,
            1,
        )

        grid_switches.attach_next_to(
            self.switch_package_progress,
            lbl_package_progress_padding,
            Gtk.PositionType.RIGHT,
            1,
            1,
        )

        grid_switches.attach(lbl_snigdhaos_keyring, 0, 3, 1, 1)
        grid_switches.attach_next_to(
            lbl_snigdhaos_keyring_padding,
            lbl_snigdhaos_keyring,
            Gtk.PositionType.RIGHT,
            1,
            1,
        )

        grid_switches.attach_next_to(
            self.switch_snigdhaos_keyring,
            lbl_snigdhaos_keyring_padding,
            Gtk.PositionType.RIGHT,
            1,
            1,
        )

        grid_switches.attach(lbl_snigdhaos_mirrorlist, 0, 4, 1, 1)
        grid_switches.attach_next_to(
            lbl_snigdhaos_mirrorlist_padding,
            lbl_snigdhaos_mirrorlist,
            Gtk.PositionType.RIGHT,
            1,
            1,
        )

        grid_switches.attach_next_to(
            self.switch_snigdhaos_mirrorlist,
            lbl_snigdhaos_mirrorlist_padding,
            Gtk.PositionType.RIGHT,
            1,
            1,
        )

        vbox_buttons = Gtk.Box(spacing=1, orientation=Gtk.Orientation.VERTICAL)
        vbox_buttons.pack_start(self.modelbtn_pacmanlog, False, True, 0)
        vbox_buttons.pack_start(modelbtn_packages_export, False, True, 0)
        vbox_buttons.pack_start(modelbtn_packages_import, False, True, 0)
        vbox_buttons.pack_start(modelbtn_iso_packages_list, False, True, 0)
        vbox_buttons.pack_start(modelbtn_package_search, False, True, 0)
        vbox_buttons.pack_start(modelbtn_about_app, False, True, 0)

        vbox.pack_start(grid_switches, False, False, 0)
        vbox.pack_start(vbox_buttons, False, False, 0)

        self.popover.add(vbox)
        self.popover.set_position(Gtk.PositionType.BOTTOM)
    except Exception as e:
        fn.logger.error("Exception in setup_headerbar(): %s" % e)
