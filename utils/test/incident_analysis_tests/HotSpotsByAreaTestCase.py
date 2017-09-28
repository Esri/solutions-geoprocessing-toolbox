# coding: utf-8
'''
-----------------------------------------------------------------------------
Copyright 2016 Esri
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

==================================================
HotSpotsByAreaTestCase.py
--------------------------------------------------
requirements: ArcGIS X.X, Python 2.7 or Python 3.4
author: ArcGIS Solutions
company: Esri
==================================================
history:
12/16/2015 - JH - initial creation
09/20/2016 - MF - Update to two method test pattern 
07/28/2017 - CM - Refactor
==================================================
'''

import unittest
import arcpy
import os

# Add parent folder to python path if running test case standalone
import sys
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

import UnitTestUtilities
import Configuration
import DataDownload

class HotSpotsByAreaTestCase(unittest.TestCase):
    ''' Test all tools and methods related to the Hot Spots by Area tool
    in the Incident Analysis toolbox'''
 
    toolboxUnderTest = None # Set to Pro or ArcMap toolbox at runtime
    toolboxUnderTestAlias = 'iaTools'

    incidentScratchGDB = None

    inputAOIFeatures = None
    inputIncidents = None
    
    def setUp(self):
        if Configuration.DEBUG == True: print(".....HotSpotsByAreaTestCase.setUp")

        ''' Initialization needed if running Test Case standalone '''
        Configuration.GetLogger()
        Configuration.GetPlatform()
        ''' End standalone initialization '''

        self.toolboxUnderTest = Configuration.incidentToolboxPath + Configuration.GetToolboxSuffix()

        UnitTestUtilities.checkArcPy()
        
        DataDownload.runDataDownload(Configuration.incidentAnalysisDataPath, Configuration.incidentInputGDB, Configuration.incidentURL)
        if (self.incidentScratchGDB == None) or (not arcpy.Exists(self.incidentScratchGDB)):
            self.incidentScratchGDB = UnitTestUtilities.createScratch(Configuration.incidentAnalysisDataPath)
        
        self.inputAOIFeatures = os.path.join(Configuration.incidentInputGDB, "Districts")
        self.inputIncidents = os.path.join(Configuration.incidentInputGDB, "Incidents")

        UnitTestUtilities.checkFilePaths([Configuration.incidentAnalysisDataPath])

        UnitTestUtilities.checkGeoObjects([Configuration.incidentInputGDB, \
                                           self.incidentScratchGDB, \
                                           self.toolboxUnderTest, \
                                           self.inputAOIFeatures, \
                                           self.inputIncidents])
        
    def tearDown(self):
        if Configuration.DEBUG == True: print(".....HotSpotsByAreaTestCase.tearDown")
        UnitTestUtilities.deleteScratch(self.incidentScratchGDB)
        
    def test_hot_spots_by_area(self):
        '''test_hot_spots_by_area'''
        if Configuration.DEBUG == True: print(".....HotSpotsByAreaTestCase.test_hot_spots_by_area")

        arcpy.env.overwriteOutput = True

        arcpy.ImportToolbox(self.toolboxUnderTest, self.toolboxUnderTestAlias)

        runToolMessage = "Running tool (Hot Spots By Area)"
        arcpy.AddMessage(runToolMessage)
        Configuration.Logger.info(runToolMessage)
        incidentFieldName = "district"
        outputWorkspace = self.incidentScratchGDB

        results = None

        try:

            # second parameter: inputIncidents must be a Feature Layer
            layerName = "incidentsLayer"
            arcpy.MakeFeatureLayer_management(self.inputIncidents, layerName)

            # Tools have slightly different names in Pro vs. ArcMap ("By" vs. "by")
            if Configuration.Platform == Configuration.PLATFORM_PRO :
                results = arcpy.HotSpotsByArea_iaTools(self.inputAOIFeatures, layerName, \
                    incidentFieldName, outputWorkspace)
            else: 
                # WORKAROUND:
                # ArcMap version of tool ignores outputWorkspace parameter
                arcpy.env.scratchWorkspace = outputWorkspace
                arcpy.env.workspace = outputWorkspace
                # End WORKAROUNG 

                results = arcpy.HotSpotsbyArea_iaTools(self.inputAOIFeatures, layerName, \
                    incidentFieldName, outputWorkspace)

        except arcpy.ExecuteError:
            UnitTestUtilities.handleArcPyError()
        except Exception as e:
            UnitTestUtilities.handleGeneralError(e)

        self.assertIsNotNone(results)
        outputFeatureClasses = results[0].split(';')
        for outputFeatureClass in outputFeatureClasses:
            self.assertTrue(arcpy.Exists(outputFeatureClass))

if __name__ == "__main__":
    unittest.main()
