'''
------------------------------------------------------------------------------
Copyright 2015 Esri
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-----------------------------------------------------------------------------
Configuration.py
Description: Common objects/methods used by test scripts
Requirements: ArcGIS Desktop Standard

data URL pattern: r"http://www.arcgis.com/sharing/content/items/XXX/data", where XXX is the item GUID
 ----------------------------------------------------------------------------
'''

import os

DEBUG = True # this guy is a flag for extra messaging while debugging tests

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

pooURL = r"http://www.arcgis.com/sharing/content/items/9d8a534a70d54a74911d9ddb60b5a1d9/data"

''' Data Management Paths '''
dataManagementPaths = os.path.normpath(os.path.join(currentPath, r"data_management_tests"))
geonamesURL = r"http://www.arcgis.com/sharing/content/items/afc766d5276648ab80aa85b819af1ffc/data"
networkPrepURL = r"http://www.arcgis.com/sharing/content/items/cf09da3684214d2b9b18c22149130fc4/data"
patrolDataCaptureURL = r"http://www.arcgis.com/sharing/content/items/853736d171e44a40a55e4c312bf43b66/data"
importAndConversionURL = r"http://www.arcgis.com/sharing/content/items/130f52ac95a040cb80717d99db100409/data"
publishableTasksURL = r"http://www.arcgis.com/sharing/content/items/921fc6d5f5e2444dab14831edc01ef9d/data"

''' Operational Graphics Paths '''
operationalGraphicsPaths = os.path.normpath(os.path.join(currentPath, r"operational_graphics_tests"))
clearingOperationsURL = r"http://www.arcgis.com/sharing/content/items/198f01e263474c209198c9c3c3586287/data"
sunPositionAnalysisURL = r"http://www.arcgis.com/sharing/content/items/bf6a04b4c9a3447b91e9c0b4074ca1e4/data"
rangeCardURL = r"http://www.arcgis.com/sharing/content/items/f5414250daf14dd389cc50199efeef8d/data"


''' Patterns Paths '''
patternsPaths = os.path.normpath(os.path.join(currentPath, r"patterns_tests"))
incidentDataPath = None
incidentInputGDB = None
incidentResultGDB = None
incidentScratchGDB = None
patterns_ToolboxesPath = os.path.normpath(os.path.join(currentPath, r"../../patterns/toolboxes/"))
patterns_ProToolboxPath = os.path.normpath(os.path.join(patterns_ToolboxesPath, "Incident Analysis Tools.tbx"))
patterns_DesktopToolboxPath = os.path.normpath(os.path.join(patterns_ToolboxesPath, "Incident Analysis Tools_10.4.tbx"))
incidentURL = "http://www.arcgis.com/sharing/content/items/528faf6b23154b04a8268b33196fa9ad/data"
incidentGDBName = "test_incident_analysis_tools.gdb"
incidentResultGDBName = "test_incident_analysis_results.gdb"

''' Suitability Paths '''
suitabilityPaths = os.path.normpath(os.path.join(currentPath, r"suitability_tests"))
suitabilityDataPath = None
suitability_ToolboxesPath = os.path.normpath(os.path.join(currentPath, r"../../suitability/toolboxes/"))
maritimeDataPath = None
maritimeScratchGDB = None
maow_ToolboxPath = os.path.join(suitability_ToolboxesPath, "Military Aspects of Weather Tools_10.4.tbx")
maotURL = r"http://www.arcgis.com/sharing/content/items/127bff2341694342a6df884aaa51237e/data"
maowURL = "http://www.arcgis.com/sharing/content/items/74eeb356c7dd4422bf52f36f38bb8a9b/data"
maritime_DesktopToolboxPath = os.path.join(suitability_ToolboxesPath, "Maritime Decision Aid Tools_10.4.tbx")
maritime_ProToolboxPath = os.path.join(suitability_ToolboxesPath, "Maritime Decision Aid Tools.tbx")
maritimeURL = "http://www.arcgis.com/sharing/content/items/43fbe3e823614783a391676d47dd3c5f/data"
maritimeGDBName = "MaritimeDecisionAidToolsTestData"
pathSlopeURL = r"http://www.arcgis.com/sharing/content/items/cbb812326b6f4fb2b77cac4a85e734a9/data"

''' Visibility Paths '''
visibilityPaths = os.path.normpath(os.path.join(currentPath, r"visibility_tests"))
vis_ToolboxesPath = os.path.normpath(os.path.join(currentPath, r"../../visibility/toolboxes/"))



