#------------------------------------------------------------------------------
# Copyright 2015 Esri
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
#-----------------------------------------------------------------------------
# TestUtilities.py
# Description: Common objects/methods used by test scripts
# Requirements: ArcGIS Desktop Standard
# ----------------------------------------------------------------------------

import arcpy
import os
import sys

currentPath = os.path.dirname(__file__)
logPath = os.path.normpath(os.path.join(currentPath, r"../log/"))

#### Visibility ####
vis_GeodatabasePath = os.path.normpath(os.path.join(currentPath, r"../../visibility/data/geodatabases/"))
vis_ScratchPath = os.path.normpath(os.path.join(currentPath, r"../../visibility/data/geodatabases"))
vis_ToolboxesPath = os.path.normpath(os.path.join(currentPath, r"../../visibility/toolboxes/"))
vis_ScriptsPath = os.path.join(vis_ToolboxesPath, "scripts")
sunPosToolbox = os.path.join(vis_ToolboxesPath, "Sun Position Analysis Tools_10.3.tbx")
visandRangeToolbox = os.path.join(vis_ToolboxesPath, "Visibility and Range Tools_10.3.tbx")



