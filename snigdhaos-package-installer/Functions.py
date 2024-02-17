
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
]

snigdhaos_spectrum_repo = [
    "#[spectrum]",
    "#Server = https://build.snigdhaos.org/spectrum/x86_64",
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
    settings

