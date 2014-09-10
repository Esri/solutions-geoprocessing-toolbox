#------------------------------------------------------------------------------
# Copyright 2013 Esri
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#------------------------------------------------------------------------------
# TestUtilities.py
# Description: Common objects/methods used by test scripts
# Requirements: ArcGIS Desktop Standard
# ----------------------------------------------------------------------------

import arcpy
import os
import sys

currentPath = os.path.dirname(__file__)
toolboxesPath = os.path.normpath(os.path.join(currentPath, r"../../../capability/toolboxes/"))

toolDataPath = os.path.join(toolboxesPath, "tooldata")
layerPath  = os.path.join(toolboxesPath, "layers")
layerDataPath = os.path.join(layerPath, "layerdata")
templateGDB = os.path.join(toolDataPath, "Templates.gdb")

toolbox = os.path.join(toolboxesPath, "ERG Tools.pyt")