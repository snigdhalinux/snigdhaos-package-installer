# Author : Eshan Roy <eshan@snigdhaos.org>
# Author URL : https://eshan.snigdhaos.org

import os
import Functions as fn
from string import Template
import shutil

# Global Varibale:
base_dir = os.path.dirname(os.path.realpath(__file__))
default_file = "%s/defaults/spi.yaml" % base_dir

# oop concept
class Settings(object):
    def __init__(self, display_versions, display_package_progress):
        self.display_versions = display_versions
        self.display_package_progress = display_package_progress
    
    def write_config_file(self):
        try:
            content = []
            with open(fn.config_file, "r", encoding="UTF-8") as f:
                contents = f.readlines()
            if len(contents) > 0:
                self.read(contents)
                conf_settings = {}
                conf_settings["Display Package Versions"] = self.display_versions
                conf_settings["Display Package Progress"] = self.display_package_progress
                index = 0
                for line in contents:
                    if line.startswith("- name:"):
                        # we need to go 2 log n as Aux Space
                        if (
                            line.strip("- name: ").strip().strip('"').strip("\n").strip() == "Display Package Versions"
                        ):
                            index = contents.index(line)
                            index += 2
                            if contents[index].startswith("  enabled: "):
                                del contents[index]
                                contents.insert(
                                    index, "  enabled: %s\n" % conf_settings["Display Package Versions"],
                                    )
                            if (
                                line.strip("- name: ").strip().strip('"').strip("\n").strip() == "Display Package Progress"
                            ):
                                index += 4
                                if contents[index].startswith("  enabled: "):
                                    del contents[index]
                                contents.insert(
                                    index, "  enabled: %s\n" % conf_settings["Display Package Progress"],
                                    )
            if len(contents) > 0:
                with open(fn.config_file, "w", encoding="UTF-8") as f:
                    f.writelines(contents)
                fn.permissions(fn.config_dir)
        except Exception as e:
            print(e) # sipex00001
    
    def read_config_file(self):
        try:
            if os.path.exists(fn.config_file):
                contents = []
                with open(fn.config_file, "r", encoding="UTF-8") as f:
                    contents = f.readlines()
                if len(contents) == 0:
                    fn.shutil.copy(default_file, fn.config_file)
                    fn.permissions(fn.config_dir)
                else:
                    return self.read(contents)
            else:
                fn.shutil.copy(default_file, fn.config_file)
                fn.permissions(fn.config_dir)
        except Exception as e:
            # print(e) # sipex00001
            print("Found Exception in read_config_file(): %s" % e)
    
    def read(self, contents):
        setting_name = None
        setting_value_enabled = None
        conf_settings = {}
        for line in contents:
            if line.startswith("- name:"):
                setting_name = (
                    line.strip("- name: ").strip().strip('"').strip("\n").strip()
                )
            elif line.startswith("  enabled: "):
                setting_value_enabled = (
                    line.strip("  enabled: ").strip().strip('"').strip("\n").strip()
                )
                if setting_value_enabled == "False":
                    conf_settings[setting_name] = False
                else:
                    conf_settings[setting_name] = True
        if len(conf_settings) > 0:
            return conf_settings
        else:
            print("[ERROR] Failed To Read Settings!")
                

