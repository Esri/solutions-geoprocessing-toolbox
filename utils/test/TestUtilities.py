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
geodatabasePath = os.path.normpath(os.path.join(currentPath, r"../../visibility/data/geodatabases/"))

logPath = os.path.normpath(os.path.join(currentPath, r"../log/"))


scratchPath = os.path.normpath(os.path.join(currentPath, r"../../visibility/data/geodatabases/"))

toolboxesPath = os.path.normpath(os.path.join(currentPath, r"../../visibility/toolboxes/"))

inputGDB  = os.path.join(geodatabasePath, "test_sun_position.gdb")
inputArea = os.path.join(inputGDB,"inputArea")
inputSurface = os.path.join(inputGDB,"Jbad_SRTM_USGS_EROS")
compareResults = os.path.join(inputGDB,"compareResults")
scratchGDB = os.path.join(scratchPath, "scratch.gdb")
outputGDB = scratchGDB
defaultGDB = scratchGDB

toolbox = os.path.join(toolboxesPath, "Sun Position Analysis Tools_10.3.tbx")
