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
==================================================
'''

import unittest
import arcpy
import os
import UnitTestUtilities
import Configuration
import DataDownload

class HotSpotsByAreaTestCase(unittest.TestCase):
    ''' Test all tools and methods related to the Hot Spots by Area tool
    in the Incident Analysis toolbox'''
    
    inputAOIFeatures = None
    inputIncidents = None
    
    def setUp(self):
        if Configuration.DEBUG == True: print(".....HotSpotsByAreaTestCase.setUp")
        UnitTestUtilities.checkArcPy()
        
        Configuration.incidentDataPath = DataDownload.runDataDownload(Configuration.patternsPaths, Configuration.incidentGDBName, Configuration.incidentURL)
        if (Configuration.incidentScratchGDB == None) or (not arcpy.Exists(Configuration.incidentScratchGDB)):
            Configuration.incidentScratchGDB = UnitTestUtilities.createScratch(Configuration.incidentDataPath)
        Configuration.incidentInputGDB = os.path.join(Configuration.incidentDataPath, Configuration.incidentGDBName)    
        UnitTestUtilities.checkFilePaths([Configuration.incidentDataPath, Configuration.incidentInputGDB, Configuration.patterns_ProToolboxPath, Configuration.patterns_DesktopToolboxPath])
        
        self.inputAOIFeatures = os.path.join(Configuration.incidentInputGDB, "Districts")
        self.inputIncidents = os.path.join(Configuration.incidentInputGDB, "Incidents")
        
    def tearDown(self):
        if Configuration.DEBUG == True: print(".....HotSpotsByAreaTestCase.tearDown")
        UnitTestUtilities.deleteScratch(Configuration.incidentScratchGDB)
        
    def test_hot_spots_by_area_pro(self):
        '''test_hot_spots_by_area_pro'''
        if Configuration.DEBUG == True: print(".....HotSpotsByAreaTestCase.test_hot_spots_by_area_pro")  
        arcpy.ImportToolbox(Configuration.patterns_ProToolboxPath, "iaTools")
        runToolMessage = "Running tool (Hot Spots By Area - Pro)"
        arcpy.AddMessage(runToolMessage)
        Configuration.Logger.info(runToolMessage)
        incidentFieldName = "district"
        outputWorkspace = Configuration.incidentDataPath
        # second parameter: inputIncidents must be a Feature Layer
        arcpy.MakeFeatureLayer_management(self.inputIncidents, "incidentsLayer")
        try:
            arcpy.HotSpotsByArea_iaTools(self.inputAOIFeatures, "incidentsLayer", incidentFieldName, outputWorkspace)
        except:
            msg = arcpy.GetMessages(2)
            self.fail('Exception in HotSpotsByArea_iaTools for Pro toolbox \n' + msg)
        self.assertTrue(arcpy.Exists(outputWorkspace))
    
    def test_hot_spots_by_area_desktop(self):
        '''test_hot_spots_by_area_desktop'''
        if Configuration.DEBUG == True: print(".....HotSpotsByAreaTestCase.test_hot_spots_by_area_desktop")  
        arcpy.ImportToolbox(Configuration.patterns_DesktopToolboxPath, "iaTools")
        runToolMessage = "Running tool (Hot Spots By Area - Desktop)"
        arcpy.AddMessage(runToolMessage)
        Configuration.Logger.info(runToolMessage)
        incidentFieldName = "district"
        outputWorkspace = Configuration.incidentDataPath
        # second parameter: inputIncidents must be a Feature Layer
        arcpy.MakeFeatureLayer_management(self.inputIncidents, "incidentsLayer")
        try:
            arcpy.HotSpotsByArea_iaTools(self.inputAOIFeatures, "incidentsLayer", incidentFieldName, outputWorkspace)
        except:
            msg = arcpy.GetMessages(2)
            self.fail('Exception in HotSpotsByArea_iaTools for Desktop toolbox \n' + msg)
        self.assertTrue(arcpy.Exists(outputWorkspace))
