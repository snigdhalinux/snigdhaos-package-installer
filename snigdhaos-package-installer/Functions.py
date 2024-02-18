
# Author : Eshan Roy <eshan@snigdhaos.org>
# Author URL : https://eshan.snigdhaos.org

# Import Mosules -->

import os
from os import makedirs
import sys
import subprocess
import threading
import psutil
import logging
import shutil
import time
from datetime import datetime, timedelta
from Settings import Settings
from logging.handlers import TimedRotatingFileHandler

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

# config base directory
base_dir = os.path.dirname(os.path.realpath(__file__))

# Global Variables - We may use local in needed
sudo_username = os.getlogin()
home = "/home/" + str(sudo_username)
path_dir_cache = base_dir + "/cache/"
package = []
distr = id()
spi_lckfile = "/tmp/spi.lock" # SPI = SnigdhaOS Package Installer
spi_pid_file = "/tmp/spi.pid"
process_timeout = 600

# Pointing to our repository & mirrorlist
snigdhaos_core_repo = [
    "#[snigdhaos-core]",
    "#Server = https://snigdhalinux.github.io/snigdhaos-core/x86_64",
    #Server = https://snigdhalinux.github.io/$repo/$arch
]

snigdhaos_spectrum_repo = [
    "#[spectrum]",
    "#Server = https://build.snigdhaos.org/spectrum/x86_64",
    #Server = https://build.snigdhaos.org/$repo/$arch
]

log_dir = "/var/log/spi/"
config_dir = "%s/.config/spi" % home
config_file = "%s/spi.yaml" % config_dir
event_logfile = "%s/event.log" % log_dir
export_dir = "%s/spi-exports" % home

# Global Functions

def permissions(dst): #dst = destination
    try:
        groups = subprocess.run(
            ["sh", "-c", "id " + sudo_username],
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        for i in groups.stdout.decode().split(" "):
            if "gid" in i:
                g = i.split("(")[1]
                group = g.replace(")", "").strip()
        subprocess.call(
            ["chown", "-R", sudo_username + ":" + group, dst],
            shell=False,
        )
    except Exception as e:
        print(e) # sipex00001
        # logger.error(e)

try:
    if not os.path.exists(log_dir):
        makedirs(log_dir)
    if not os.path.exists(export_dir):
        makedirs(export_dir)
    if not os.path.exists(config_dir):
        makedirs(config_dir)
    permissions(export_dir)
    permissions(config_dir)
    # Print log
    print("[INFO] Log File %s" % log_dir)
    print("[INFO] Export Directory %s" % export_dir)
    print("[INFO] Config Directory %s" % config_dir)
except os.error as oserror:
    print("[ERROR] Found Exception in Setup log/export : %s !" %oserror)
    sys.exit(1)

# Just need to make a settings file!
try:
    settings = Settings(False, False)
    settings_config = settings.read_config_file()
    logger = logging.getLogger("logger")
    ch = logging.StreamHandler()
    tfh = TimedRotatingFileHandler(event_logfile, encoding="UTF-8", delay=False, when="W4")
    if settings_config:
        debug_logging_enabled = None
        debug_logging_enabled = settings_config["Debug Logging"]
        if debug_logging_enabled is not None and debug_logging_enabled is True:
            logger.setLevel(logging.DEBUG)
            ch.setLevel(logging.DEBUG)
            tfh.setLevel(level=logging.DEBUG)
        else:
            logger.setLevel(logging.INFO)
            ch.setLevel(logging.INFO)
            tfh.setLevel(level=logging.INFO)
    else:
        logger.setLevel(logging.INFO)
        ch.setLevel(logging.INFO)
        tfh.setLevel(level=logging.INFO)
    formatter = logging.Formatter(
        "%(asctime)s:%(levelname)s > %(message)s", "%Y-%m-%d %H:%M:%S"
    )
    ch.setFormatter(formatter)
    tfh.setFormatter(formatter)
    logger.addHandler(ch)
    logger.addHandler(tfh)
except Exception as e:
    print("[ERROR] Found Exception: %s" % e)


def _on_close_create_packages_file():
    try:
        logger.info(
            "App Closing With Saving Currently Installed Packages -> File!"
        )
        packages_file = "%s-package.txt" % datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        logger.info("Saving: %s%s" % (log_dir, packages_file))
        cmd = ["pacman", "-Q"]
        with subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True,
        ) as process:
            with open("%s/%s" % (log_dir, packages_file), "w") as f:
                for line in process.stdout:
                    f.write("%s" % line)
    except Exception as e:
        print("[ERROR] Found Exception in _on_close_create_packages_file(): %s" % e)

# Global ->
def _get_position(lists, value):
    data = [string for string in lists if value in string]
    position = lists.index(data[0])
    return position

def is_file_stale(filepath, stale_days, stale_hours, stale_minutes):
    now = datetime.now()
    stale_datetime = now - timedelta(
        days=stale_days, hours=stale_hours, minutes=stale_minutes
    )
    if os.path.exists(filepath):
        file_created = datetime.fromtimestamp(os.path.getctime(filepath))
        if file_created < stale_datetime:
            return True
    return False

def sync_package_db():
    try:
        sync_str = ["pacman", "-Sy"]
        logger.info(
            "Synchronizing Database..."
        )
        process_sync = subprocess.run(
            sync_str,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=process_timeout,
        )
        if process_sync.returncode == 0:
            return None
        else:
            if process_sync.stdout:
                out = str(process_sync.stdout.decode("utf-8"))
                logger.error(out)
                return out
    except Exception as e:
        print("[ERROR] Found Exception in sync_package_db(): %s" % e)

def sync_file_db():
    try:
        sync_str = ["pacman", "-Fy"]
        logger.info(
            "Synchronizing Database..."
        )
        process_sync = subprocess.run(
            sync_str,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=process_timeout,
        )
        if process_sync.returncode == 0:
            return None
        else:
            if process_sync.stdout:
                out = str(process_sync.stdout.decode("utf-8"))
                logger.error(out)
                return out
    except Exception as e:
        print("[ERROR] Found Exception in sync_file_db(): %s" % e)

# Pacman install & remove process
        
def start_subprocess(self, cmd, progress_dialog, action, pkg, widget):
    try:
        self.switch_package_version.set_sensitive(False)
        self.switch_snigdhaos_keyring.set_sensitive(False)
        # self.switch_package_version.set_sensitive(False)
        widget.set_sensitive(False)
        process_stdout_lst = []
        process_stdout_lst.append("Command = %s\n\n" % " ".join(cmd))
        with subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            universal_newlines=True,
        ) as process:
            if progress_dialog is not None:
                progress_dialog.pkg_dialog_closed = False
            self.in_progress = True
            if(progress_dialog is not None and progress_dialog.pkg_dialog_closed is False):
                line = ("Pacman is Currently Processing %s of Package %s \n\n Command Running -> %s\n\n" % (action,pkg.name, " ".join(cmd)))
                GLib.idle_add(
                    update_progress_txt_view,
                    self,
                    line,
                    progress_dialog,
                    priority=GLib.PRIORITY_DEFAULT,
                )
            logger.debug("Pacman is busy!")
            while True:
                if process.poll() is not None:
                    break
                if progress_dialog is not None and progress_dialog.pkg_dialog_closed is False:
                    for line in process.stdout:
                        GLib.idle_add(
                            update_progress_txt_view,
                            self,
                            line,
                            progress_dialog,
                            priority=GLib.PRIORITY_DEFAULT,
                        )
                    time.sleep(0.3)
                else:
                    for line in process.stdout:
                        process_stdout_lst.append(line)
                    time.sleep(1)
            returncode = None
            returncode = process.poll()
            # Print log
            logger.debug("Pacman return code -> %s" % returncode)
            if returncode is not None:
                logger.info("Completed -> %s" % " ".join(cmd))
                GLib.idle_add(
                    refresh_ui,
                    self,
                    action,
                    widget,
                    pkg,
                    progress_dialog,
                    process_stdout_lst,
                    priotiry=GLib.PRIORITY_DEFAULT,
                )
    except SystemError as se:
        logger.error("Pacman Failed -> %s" % (action,se))
        process.terminate()
        if progress_dialog is not None:
            print("O")
            # progress_dialog. #spiinc0002
        self.switch_package_version.set_sensitive(True)
        self.switch_snigdhaos_keyring.set_sensitive(True)

def check_package_installed(package_name):
    query_str = ["pacman", "-Qq"]
    try:
        process_pkg_installed = subprocess.run(
            query_str,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=process_timeout,
            universal_newlines=True,
        )
        if package_name in process_pkg_installed.stdout.splitlines():
            return True
        else:
            if check_pacman_localdb(package_name):
                return True
            else:
                return False
    except subprocess.CalledProcessError:
        return False

def check_pacman_localdb(package_name):
    query_str = ["pacman", "-Qq"]
    try:
        process_pkg_installed = subprocess.run(
            query_str,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=process_timeout,
            universal_newlines=True,
        )
        if process_pkg_installed.returncode == 0:
            for line in process_pkg_installed.stdout.decode("utf-8").splitlines():
                if line.startswith("Name            :"):
                    if line.replace(" ","").split("Name:")[1].strip() == package_name:
                        return True
                if line.startswith("Replaces            :"):
                    replaces = line.split("Replaces            :")[1].strip()
                    if len(replaces) > 0:
                        if package_name in replaces:
                            return True
        else:
            return False
    except subprocess.CalledProcessError:
        return False


def refresh_ui(self,pkg,progress_dialog,action,switch,process_stdout_lst):
    self.switch_package_version.set_sensitive(True)
    self.switch_snigdhaos_keyring.set_sensitive(True)
    logger.debug("Checking Whether %s is installed or not..." % pkg.name)
    installed = check_package_installed()
    if progress_dialog is not None:
        if progress_dialog.btn_package_progress_closed is False:
            progress_dialog.set_title("[INFO] %s Insalled Successfully!" % pkg.name)
            progress_dialog.infobar.set_name("infobar_info")
            content = progress_dialog.infobar.get_content_area()
            if content is not None:
                for widget in content.get_children():
                    content.remove(widget)
                lbl_install = Gtk.Label(xalign=0,yalign=0)
                lbl_install.set_markup("Installed %s" % pkg.name)
                content.add(lbl_install)
                if self.timeout_id is not None:
                    GLib.source_remove(self.timeout_id)
                    self.timeout_id = None
                self.timeout_id = GLib.timeout_add(100, reveal_infobar, self, progress_dialog)
    if installed is False and action == "install":
        logger.debug("Switch State = False")
        if progress_dialog is not None:
            switch.set_sensitive(True)
            switch.set_state(False)
            switch.set_active(False)
            if progress_dialog.pkg_dialog_closed is False:
                progress_dialog.set_title("Failed: %s" % pkg.name)
                progress_dialog.infobar.set_name("infobar_error")
                content = progress_dialog.infobar.get_content_area()
                if content is not None:
                    for widget in content.get_children():
                        content.remove(widget)
                    lbl_install = Gtk.Label(xalign=0,yalign=0)
                    lbl_install.set_markup("Failed: %s" % pkg.name)
                    content.add(lbl_install)
                    if self.timeout_id is not None:
                        GLib.source_remove(self.timeout_id)
                        self.timeout_id = None
                    self.timeout_id = GLib.timeout_add(100, reveal_infobar, self, progress_dialog)
            else:
                logger.debug(" ".join(process_stdout_lst))
                message_dialog = 










# #eshanined : To Create Functions:
# get_current_installed()
# check_package_installed()
# check_github()
# verify_snigdhaos_pacman_conf()
