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
import os


currentPath = os.path.dirname(__file__)
print currentPath
geodatabasePath = os.path.normpath(os.path.join(currentPath, r"../../../data_management/data/ScannedMaps/Sample/"))
sampleInputPath = os.path.normpath(os.path.join(currentPath, r"../../../data_management/data/ScannedMaps/Sample/SourceData/RPF"))

toolboxesPath = os.path.normpath(os.path.join(currentPath, r"../../../data_management/toolboxes/")) 
print toolboxesPath               

inputGDB  = os.path.join(geodatabasePath, "ScannedMaps.gdb")

toolbox = os.path.join(toolboxesPath, "Scanned Map Basemap Tools_10.3.tbx")
