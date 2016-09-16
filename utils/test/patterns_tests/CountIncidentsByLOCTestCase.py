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
CountIncidentsByLOCTestCase.py
--------------------------------------------------
requirments: ArcGIS X.X, Python 2.7 or Python 3.4
author: ArcGIS Solutions
company: Esri
==================================================
history:
12/16/2015 - JH - initial creation
09/15/2016 - mf - update to two test case instead of three
==================================================
'''

import arcpy
import os
import unittest
import UnitTestUtilities
import Configuration
import DataDownload

class CountIncidentsByLOCTestCase(unittest.TestCase):
    ''' Test all tools and methods related to the Count Incidents by LOC tool
    in the Incident Analysis toolbox'''
    
    inputPointsFeatures = None
    inputLinesFeatures = None
    
    def setUp(self):
        if Configuration.DEBUG == True: print(".....CountIncidentsByLOCTestCase.setUp")  
        UnitTestUtilities.checkArcPy()
        
        Configuration.incidentDataPath = DataDownload.runDataDownload(Configuration.patternsPaths, Configuration.incidentGDBName, Configuration.incidentURL)
        if (Configuration.incidentScratchGDB == None) or (not arcpy.Exists(Configuration.incidentScratchGDB)):
            Configuration.incidentScratchGDB = UnitTestUtilities.createScratch(Configuration.incidentDataPath)
        Configuration.incidentInputGDB = os.path.join(Configuration.incidentDataPath, Configuration.incidentGDBName)
        
        UnitTestUtilities.checkFilePaths([Configuration.incidentDataPath, Configuration.incidentInputGDB, Configuration.patterns_ProToolboxPath, Configuration.patterns_DesktopToolboxPath])
     
        # set up inputs    
        self.inputPointsFeatures = os.path.join(Configuration.incidentInputGDB, "Incidents")
        self.inputLinesFeatures = os.path.join(Configuration.incidentInputGDB, "Roads")
            
    def tearDown(self):
        if Configuration.DEBUG == True: print(".....CountIncidentsByLOCTestCase.tearDown")
        UnitTestUtilities.deleteScratch(Configuration.incidentScratchGDB)
        
    def test_count_incidents_pro(self):
        if Configuration.DEBUG == True: print(".....CountIncidentsByLOCTestCase.test_count_incidents_pro")
        arcpy.ImportToolbox(Configuration.patterns_ProToolboxPath, "iaTools")
        outputCountFeatures = os.path.join(Configuration.incidentScratchGDB, "outputCount")
        
        runToolMsg = "Running tool (Count Incidents By LOC)"
        arcpy.AddMessage(runToolMsg)
        Configuration.Logger.info(runToolMsg)
        
        arcpy.CountIncidentsByLOC_iaTools(self.inputPointsFeatures, self.inputLinesFeatures, "#", outputCountFeatures)
        result = arcpy.GetCount_management(outputCountFeatures)
        featureCount = int(result.getOutput(0))
        self.assertEqual(featureCount, int(2971))
        return
    
    def test_count_incidents_desktop(self):
        if Configuration.DEBUG == True: print(".....CountIncidentsByLOCTestCase.test_count_incidents_desktop")
        arcpy.ImportToolbox(Configuration.patterns_DesktopToolboxPath, "iaTools")
        outputCountFeatures = os.path.join(Configuration.incidentScratchGDB, "outputCount")
        
        runToolMsg = "Running tool (Count Incidents By LOC)"
        arcpy.AddMessage(runToolMsg)
        Configuration.Logger.info(runToolMsg)
        
        arcpy.CountIncidentsByLOC_iaTools(self.inputPointsFeatures, self.inputLinesFeatures, "#", outputCountFeatures)
        result = arcpy.GetCount_management(outputCountFeatures)
        featureCount = int(result.getOutput(0))
        self.assertEqual(featureCount, int(2971))
        return
