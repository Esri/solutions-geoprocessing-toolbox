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
FindPercentChangeTestCase.py
--------------------------------------------------
requirments: ArcGIS X.X, Python 2.7 or Python 3.4
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

class FindPercentChangeTestCase(unittest.TestCase):
    ''' Test all tools and methods related to the Find Percent Change tool
    in the Incident Analysis toolbox'''
 
    toolboxUnderTest = None # Set to Pro or ArcMap toolbox at runtime
    toolboxUnderTestAlias = 'iaTools'
    
    incidentScratchGDB = None
           
    inputOldIncidents = None
    inputNewIncidents = None
    inputAOIFeatures = None
    
    def setUp(self):
        if Configuration.DEBUG == True: print(".....FindPercentChangeTestCase.setUp")
        ''' Initialization needed if running Test Case standalone '''
        Configuration.GetLogger()
        Configuration.GetPlatform()
        ''' End standalone initialization '''

        self.toolboxUnderTest = Configuration.incidentToolboxPath + Configuration.GetToolboxSuffix()

        UnitTestUtilities.checkArcPy()

        DataDownload.runDataDownload(Configuration.incidentAnalysisDataPath, Configuration.incidentInputGDB, Configuration.incidentURL)
        if (self.incidentScratchGDB == None) or (not arcpy.Exists(self.incidentScratchGDB)):
            self.incidentScratchGDB = UnitTestUtilities.createScratch(Configuration.incidentAnalysisDataPath)

        # set up inputs        
        self.inputOldIncidents = os.path.join(Configuration.incidentInputGDB, "Incidents2014")
        self.inputNewIncidents = os.path.join(Configuration.incidentInputGDB, "Incidents2015")
        self.inputAOIFeatures = os.path.join(Configuration.incidentInputGDB, "Districts")

        UnitTestUtilities.checkFilePaths([Configuration.incidentAnalysisDataPath])

        UnitTestUtilities.checkGeoObjects([Configuration.incidentInputGDB, \
                                           self.incidentScratchGDB, \
                                           self.toolboxUnderTest, \
                                           self.inputOldIncidents, \
                                           self.inputNewIncidents, \
                                           self.inputAOIFeatures])
       
    def tearDown(self):
        if Configuration.DEBUG == True: print(".....FindPercentChangeTestCase.tearDown")
        UnitTestUtilities.deleteScratch(self.incidentScratchGDB)
        
    def test_percent_change(self):
        '''test_percent_change_pro'''
        if Configuration.DEBUG == True: print(".....FindPercentChangeTestCase.test_percent_change")
        arcpy.ImportToolbox(self.toolboxUnderTest, self.toolboxUnderTestAlias)
        runToolMessage = "Running tool (Find Percent Change)"
        arcpy.AddMessage(runToolMessage)
        Configuration.Logger.info(runToolMessage)
        outputFeatures = os.path.join(self.incidentScratchGDB, "outputPercentChange")
        # Pro adds an extra parameter for output
        try:
            arcpy.FindPercentChange_iaTools(self.inputOldIncidents, self.inputAOIFeatures, self.inputNewIncidents, outputFeatures)
        except:
            msg = arcpy.GetMessages(2)
            self.fail('Exception in FindPercentChange_iaTools for Pro toolbox \n' + msg)
        result = arcpy.GetCount_management(outputFeatures)
        count = int(result.getOutput(0))
        self.assertEqual(count, int(10))
      
if __name__ == "__main__":
    unittest.main()