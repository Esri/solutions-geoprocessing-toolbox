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
IncidentHotSpotsTestCase.py
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

class IncidentHotSpotsTestCase(unittest.TestCase):
    ''' Test all tools and methods related to the Incident Hot Spots tool
    in the Incident Analysis toolbox'''
    
    inputPointFeatures = None
    inputBoundaryFeatures = None
    
    def setUp(self):
        if Configuration.DEBUG == True: print(".....IncidentHotSpotsTestCase.setUp")    
        UnitTestUtilities.checkArcPy()
        Configuration.incidentDataPath = DataDownload.runDataDownload(Configuration.patternsPaths, Configuration.incidentGDBName, Configuration.incidentURL)
        if (Configuration.incidentScratchGDB == None) or (not arcpy.Exists(Configuration.incidentScratchGDB)):
            Configuration.incidentScratchGDB = UnitTestUtilities.createScratch(Configuration.incidentDataPath)
        Configuration.incidentInputGDB = os.path.join(Configuration.incidentDataPath, Configuration.incidentGDBName)
        UnitTestUtilities.checkFilePaths([Configuration.incidentDataPath, Configuration.incidentInputGDB, Configuration.patterns_ProToolboxPath, Configuration.patterns_DesktopToolboxPath])
        self.inputPointFeatures = os.path.join(Configuration.incidentInputGDB, "Incidents")
        self.inputBoundaryFeatures = os.path.join(Configuration.incidentInputGDB, "Districts")
            
    def tearDown(self):
        if Configuration.DEBUG == True: print(".....IncidentHotSpotsTestCase.tearDown")
        UnitTestUtilities.deleteScratch(Configuration.incidentScratchGDB)
        
    def test_incident_hot_spots_pro(self):
        '''test_incident_hot_spots_pro'''
        if Configuration.DEBUG == True: print(".....IncidentHotSpotsTestCase.test_incident_hot_spots_pro")
        arcpy.ImportToolbox(Configuration.patterns_ProToolboxPath, "iaTools")
        runToolMessage = "Running tool (Incident Hot Spots - Pro)"
        arcpy.AddMessage(runToolMessage)
        Configuration.Logger.info(runToolMessage)
        outputFeatures = os.path.join(Configuration.incidentScratchGDB, "outputHotSpots")
        try:
            arcpy.IncidentHotSpots_iaTools(self.inputPointFeatures, self.inputBoundaryFeatures, outputFeatures)
        except:
            msg = arcpy.GetMessages(2)
            self.fail('Exception in IncidentHotSpots_iaTools for Pro toolbox \n' + msg)
        result = arcpy.GetCount_management(outputFeatures)
        featureCount = int(result.getOutput(0))
        self.assertEqual(featureCount, int(7302))
    
    def test_incident_hot_spots_desktop(self):
        '''test_incident_hot_spots_desktop'''
        if Configuration.DEBUG == True: print(".....IncidentHotSpotsTestCase.test_incident_hot_spots_desktop")
        arcpy.ImportToolbox(Configuration.patterns_DesktopToolboxPath, "iaTools")
        runToolMessage = "Running tool (Incident Hot Spots - Desktop)"
        arcpy.AddMessage(runToolMessage)
        Configuration.Logger.info(runToolMessage)
        outputFeatures = os.path.join(Configuration.incidentScratchGDB, "outputHotSpots")
        try:
            arcpy.IncidentHotSpots_iaTools(self.inputPointFeatures, self.inputBoundaryFeatures, outputFeatures)
        except:
            msg = arcpy.GetMessages(2)
            self.fail('Exception in IncidentHotSpots_iaTools for Desktop toolbox \n' + msg)
        result = arcpy.GetCount_management(outputFeatures)
        featureCount = int(result.getOutput(0))
        self.assertEqual(featureCount, int(7302))
