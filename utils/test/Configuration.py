# coding: utf-8
'''
------------------------------------------------------------------------------
Copyright 2015 - 2017 Esri
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

 ----------------------------------------------------------------------------
==================================================
Configuration.py
--------------------------------------------------
requirements:
* ArcGIS Desktop 10.X+ or ArcGIS Pro 1.X+
* Python 2.7 or Python 3.4
author: ArcGIS Solutions
company: Esri
==================================================
description:
Configuration flags/paths for unit tests

data URL pattern: r"http://www.arcgis.com/sharing/content/items/XXX/data", where XXX is the item GUID

==================================================
history:
10/2015 - JH - Original coding
07/2017 - CM - Reorg/refactor

==================================================
'''

import os
import sys

DEBUG = True # this guy is a flag for extra messaging while debugging tests

#NOTE: Logger and Platform are initialized in TestRunner's main()
Logger = None

Platform = None

PLATFORM_PRO = "PRO"
PLATFORM_DESKTOP = "DESKTOP"

''' Testing paths '''
currentPath = os.path.dirname(__file__) # should go to .\solutions-geoprocessing-toolbox\utils\test
repoPath = os.path.dirname(os.path.dirname(currentPath))

''' Download path '''
testDataPath = os.path.normpath(os.path.join(currentPath, r"test_data")) # should go to .\solutions-geoprocessing-toolbox\utils\test\test_data

''' Log Path: the folder where the log files go wild and multiply '''
logPath = os.path.normpath(os.path.join(currentPath, r"log")) # should go to .\solutions-geoprocessing-toolbox\utils\test\log

'''Distance To Assets paths'''
distancetoAssetsToolboxPath = os.path.normpath(os.path.join(currentPath, r"../../distance_to_assets/Distance To Assets"))
distanceToAssetsDataPath = os.path.normpath(os.path.join(testDataPath, r"DistanceToAssets"))
distanceToAssetsInputGDB = os.path.join(distanceToAssetsDataPath, "DistancetoAssetsTestData/DistanceToAssets.gdb")
distanceToAssetsOutputGDB = os.path.join(currentPath, r"../../distance_to_assets/DistanceToAssets.gdb")
distanceToAssetsInputNDGDB=os.path.join(distanceToAssetsDataPath, "DistancetoAssetsTestData/SanFrancisco.gdb")
distanceToAssetsURL = r"http://www.arcgis.com/sharing/content/items/700e44eb3e114c098818ea71f7ad72b6/data"

''' Clearing Operations - Test Data/Paths '''
clearingOperationsToolboxPath = os.path.normpath(os.path.join(currentPath, r"../../clearing_operations/ClearingOperationsTools"))
clearingOperationsPath = os.path.normpath(os.path.join(testDataPath, r"clearing_operations"))
clearingOperationsURL = r"http://www.arcgis.com/sharing/content/items/198f01e263474c209198c9c3c3586287/data"
clearingOperationsInputGDB = os.path.join(clearingOperationsPath, "test_clearing_operations.gdb")

''' Geonames - Test Data/Paths '''
geonamesToolboxPath = os.path.normpath(os.path.join(currentPath, r"../../geonames/Geonames Tools"))
geonamesDataPath = os.path.normpath(os.path.join(testDataPath, r"geonames"))
geonamesInputGDB = os.path.join(geonamesDataPath, "Geonames.gdb")
geonamesURL = r"http://www.arcgis.com/sharing/content/items/afc766d5276648ab80aa85b819af1ffc/data"

''' Incident Analysis - Test Data/Paths '''
incidentToolboxPath = os.path.normpath(os.path.join(currentPath, r"../../incident_analysis/Incident Analysis Tools"))
incidentAnalysisDataPath = os.path.normpath(os.path.join(testDataPath, r"incident_analysis"))
incidentURL = "http://www.arcgis.com/sharing/content/items/528faf6b23154b04a8268b33196fa9ad/data"
incidentInputGDB = os.path.join(incidentAnalysisDataPath, "test_incident_analysis_tools.gdb")
incidentResultGDB = os.path.join(incidentAnalysisDataPath, "test_incident_analysis_results.gdb")

''' Sun Position Analysis - Test Data/Paths '''
sunPositionAnalysisToolboxPath = os.path.normpath(os.path.join(currentPath, r"../../sun_position_analysis/Sun Position Analysis Tools"))
sunPositionAnalysisDataPath = os.path.normpath(os.path.join(testDataPath, r"sun_position_analysis"))
sunPositionAnalysisURL = r"http://www.arcgis.com/sharing/content/items/bf6a04b4c9a3447b91e9c0b4074ca1e4/data"
sunPositionInputGDB = os.path.join(sunPositionAnalysisDataPath, "test_sun_position.gdb")

''' MAoT - Test Data/Paths '''
maotToolboxPath = os.path.normpath(os.path.join(currentPath, r"../../military_aspects_of_terrain/Military Aspects of Terrain Tools"))
maotPath = os.path.normpath(os.path.join(testDataPath, r"maot"))
maotURL = r"http://www.arcgis.com/sharing/content/items/127bff2341694342a6df884aaa51237e/data"

''' MAoW - Test Data/Paths '''
maowToolboxPath = os.path.normpath(os.path.join(currentPath, r"../../military_aspects_of_weather/Military Aspects of Weather Tools"))
maowPath = os.path.normpath(os.path.join(testDataPath, r"maow"))
maowURL = "http://www.arcgis.com/sharing/content/items/74eeb356c7dd4422bf52f36f38bb8a9b/data"

def checkTokenizeWorkaround() :
    #################################################
    # WORKAROUND: for Python 3 choking on reading some binary files (with nulls)
    # For example in ArcPy when loading a toolbox when run from command line
    # Get error like: detect_encoding...tokenize.py...find_cookie...raise SyntaxError(msg)  
    # ...SyntaxError: invalid or missing encoding declaration for '...XXXX.tbx'
    # Workaround borrowed/used from:
    # https://github.com/habnabit/passacre/commit/2ea05ba94eab2d26951ae7b4b51abf53132b20f0

    # Code should work with Python 2, but only do workaround for Python 3
    # Workaround needed in Versions 3.0 - 3.5.2
    if sys.version_info >= (3, 0) and sys.version_info < (3, 5, 3):
        import tokenize

        try:
            _detect_encoding = tokenize.detect_encoding
        except AttributeError:
            pass
        else:
            def detect_encoding(readline):
                try:
                    return _detect_encoding(readline)
                except SyntaxError:
                    return 'latin-1', []

            tokenize.detect_encoding = detect_encoding
    ## END WORKAROUND
    #################################################

def GetLogger() :

    global Logger

    if Logger is None:

        import UnitTestUtilities

        logName = UnitTestUtilities.getLoggerName()
        Logger = UnitTestUtilities.initializeLogger(logName)

    return Logger

def GetPlatform() :

    global Platform

    if Platform is None :

        import arcpy

        Platform = PLATFORM_DESKTOP
        installInfo = arcpy.GetInstallInfo()
        if installInfo['ProductName'] == 'ArcGISPro':
            Platform = PLATFORM_PRO
            checkTokenizeWorkaround()

    return Platform

def GetToolboxSuffix() :

    platform = GetPlatform()

    # default to ArcMap
    suffix = "_arcmap.tbx"

    if Platform == PLATFORM_PRO :
        suffix = "_pro.tbx"

    return suffix
