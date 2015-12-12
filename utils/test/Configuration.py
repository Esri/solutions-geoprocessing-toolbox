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
# Configuration.py
# Description: Common objects/methods used by test scripts
# Requirements: ArcGIS Desktop Standard
# ----------------------------------------------------------------------------

import os

DEBUG = False # this guy is a flag for extra messaging while debugging tests

#NOTE: Logger and Platform are initialized in TestRunner's main()
Logger = None
Platform = None

''' Testing paths '''
currentPath = os.path.dirname(__file__) # should go to .\solutions-geoprocessing-toolbox\utils\test
repoPath = os.path.dirname(os.path.dirname(currentPath))

''' Log Path: the folder where the log files go wild and multiply '''
logPath = os.path.normpath(os.path.join(currentPath, r"log")) # should go to .\solutions-geoprocessing-toolbox\utils\test\log

''' Capability Paths'''
capabilityPath = os.path.normpath(os.path.join(currentPath, r"capability_tests"))

''' Data Management Paths '''
dataManagementPaths = os.path.normpath(os.path.join(currentPath, r"data_management_tests"))

''' Operational Graphics Paths '''
operationalGraphicsPaths = os.path.normpath(os.path.join(currentPath, r"operational_graphics_tests"))

''' Patterns Paths '''
patternsPaths = os.path.normpath(os.path.join(currentPath, r"patterns_tests"))

''' Suitability Paths '''
suitabilityPaths = os.path.normpath(os.path.join(currentPath, r"suitability_tests"))

''' Visibility Paths'''
visibilityPaths = os.path.normpath(os.path.join(currentPath, r"visibility_tests"))

#### Visibility ####
vis_GeodatabasePath = os.path.normpath(os.path.join(currentPath, r"../../visibility/data/geodatabases/"))
vis_ScratchPath = os.path.normpath(os.path.join(currentPath, r"../../visibility/data/geodatabases"))
vis_ToolboxesPath = os.path.normpath(os.path.join(currentPath, r"../../visibility/toolboxes/"))
vis_ScriptsPath = os.path.join(vis_ToolboxesPath, "scripts")
sunPosToolbox = os.path.join(vis_ToolboxesPath, "Sun Position Analysis Tools_10.3.tbx")
visandRangeToolbox = os.path.join(vis_ToolboxesPath, "Visibility and Range Tools_10.3.tbx")



