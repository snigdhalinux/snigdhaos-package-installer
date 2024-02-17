# Author : Eshan Roy <eshan@snigdhaos.org>
# Author URL : https://eshan.snigdhaos.org

import os
import Functions as fn
from string import Template

# oop concept
class Settings(object):
    def __init__(self, display_versions, display_package_progress):
        self.display_versions = display_versions
        self.display_package_progress = display_package_progress