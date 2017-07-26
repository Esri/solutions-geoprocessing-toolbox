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
==================================================
'''

import unittest
import arcpy
import os
import UnitTestUtilities
import Configuration
import DataDownload

class FindPercentChangeTestCase(unittest.TestCase):
    ''' Test all tools and methods related to the Find Percent Change tool
    in the Incident Analysis toolbox'''
    
    inputOldIncidents = None
    inputNewIncidents = None
    inputAOIFeatures = None
    
    def setUp(self):
        if Configuration.DEBUG == True: print(".....FindPercentChangeTestCase.setUp")
        UnitTestUtilities.checkArcPy()
        
        Configuration.incidentDataPath = DataDownload.runDataDownload(Configuration.patternsPaths, Configuration.incidentGDBName, Configuration.incidentURL)
        if (Configuration.incidentScratchGDB == None) or (not arcpy.Exists(Configuration.incidentScratchGDB)):
            Configuration.incidentScratchGDB = UnitTestUtilities.createScratch(Configuration.incidentDataPath)
        Configuration.incidentInputGDB = os.path.join(Configuration.incidentDataPath, Configuration.incidentGDBName)
        
        UnitTestUtilities.checkFilePaths([Configuration.incidentDataPath, Configuration.incidentInputGDB, Configuration.patterns_ProToolboxPath, Configuration.patterns_DesktopToolboxPath])
            
        self.inputOldIncidents = os.path.join(Configuration.incidentInputGDB, "Incidents2014")
        self.inputNewIncidents = os.path.join(Configuration.incidentInputGDB, "Incidents2015")
        self.inputAOIFeatures = os.path.join(Configuration.incidentInputGDB, "Districts")
            
    def tearDown(self):
        if Configuration.DEBUG == True: print(".....FindPercentChangeTestCase.tearDown")
        UnitTestUtilities.deleteScratch(Configuration.incidentScratchGDB)
        
    def test_percent_change_pro(self):
        '''test_percent_change_pro'''
        if Configuration.DEBUG == True: print(".....FindPercentChangeTestCase.test_percent_change_pro")
        arcpy.ImportToolbox(Configuration.patterns_ProToolboxPath, "iaTools")
        runToolMessage = "Running tool (Find Percent Change - Pro)"
        arcpy.AddMessage(runToolMessage)
        Configuration.Logger.info(runToolMessage)
        outputFeatures = os.path.join(Configuration.incidentScratchGDB, "outputPercentChange")
        # Pro adds an extra parameter for output
        try:
            arcpy.FindPercentChange_iaTools(self.inputOldIncidents, self.inputAOIFeatures, self.inputNewIncidents, outputFeatures)
        except:
            msg = arcpy.GetMessages(2)
            self.fail('Exception in FindPercentChange_iaTools for Pro toolbox \n' + msg)
        proResult = arcpy.GetCount_management(outputFeatures)
        proCount = int(proResult.getOutput(0))
        self.assertEqual(proCount, int(10))
        
    def test_percent_change_desktop(self):
        '''test_percent_change_desktop'''
        if Configuration.DEBUG == True: print(".....FindPercentChangeTestCase.test_percent_change_desktop")
        arcpy.ImportToolbox(Configuration.patterns_DesktopToolboxPath, "iaTools")
        runToolMessage = "Running tool (Find Percent Change)"
        arcpy.AddMessage(runToolMessage)
        Configuration.Logger.info(runToolMessage)
        try:
            result = arcpy.FindPercentChange_iaTools(self.inputOldIncidents, self.inputAOIFeatures, self.inputNewIncidents)
        except:
            msg = arcpy.GetMessages(2)
            self.fail('Exception in FindPercentChange_iaTools for Desktop toolbox \n' + msg)
        featureResult = arcpy.GetCount_management(result)
        featureCount = int(featureResult.getOutput(0))
        self.assertEqual(featureCount, int(10))
        
    # def test_percent_change(self, toolboxPath, platform):
    #     try:
    #         if Configuration.DEBUG == True: print("     FindPercentChangeTestCase.test_percent_change")
    #         arcpy.ImportToolbox(toolboxPath, "iaTools")
    #         runToolMessage = "Running tool (Find Percent Change)"
    #         arcpy.AddMessage(runToolMessage)
    #         Configuration.Logger.info(runToolMessage)
    #         if platform == "Pro":
    #             outputFeatures = os.path.join(Configuration.incidentScratchGDB, "outputPercentChange")
    #             # Pro adds an extra parameter for output
    #             arcpy.FindPercentChange_iaTools(self.inputOldIncidents, self.inputAOIFeatures, self.inputNewIncidents, outputFeatures)
    #             proResult = arcpy.GetCount_management(outputFeatures)
    #             proCount = int(proResult.getOutput(0))
    #             self.assertEqual(proCount, int(10))
    #         else:
    #             result = arcpy.FindPercentChange_iaTools(self.inputOldIncidents, self.inputAOIFeatures, self.inputNewIncidents)
    #             featureResult = arcpy.GetCount_management(result)
    #             featureCount = int(featureResult.getOutput(0))
    #             self.assertEqual(featureCount, int(10))
    #     except arcpy.ExecuteError:
    #         UnitTestUtilities.handleArcPyError()
    #     except:
    #         UnitTestUtilities.handleGeneralError()
            