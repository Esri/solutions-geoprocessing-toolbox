# coding: utf-8
# -----------------------------------------------------------------------------
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
# -----------------------------------------------------------------------------

# ==================================================
# CountIncidentsByLOCTestCase.py
# --------------------------------------------------
# requirments: ArcGIS X.X, Python 2.7 or Python 3.4
# author: ArcGIS Solutions
# company: Esri
# ==================================================
# history:
# 12/16/2015 - JH - initial creation
# ==================================================

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
        if Configuration.DEBUG == True: print("     CountIncidentsByLOCTestCase.setUp")  
        UnitTestUtilities.checkArcPy()
        
        Configuration.incidentDataPath = DataDownload.runDataDownload(Configuration.patternsPaths, Configuration.incidentGDBName, Configuration.incidentURL)
        if (Configuration.incidentScratchGDB == None) or (not arcpy.Exists(Configuration.incidentScratchGDB)):
            Configuration.incidentScratchGDB = UnitTestUtilities.createScratch(Configuration.incidentDataPath)
        Configuration.incidentInputGDB = os.path.join(Configuration.incidentDataPath, Configuration.incidentGDBName)
        
        UnitTestUtilities.checkFilePaths([Configuration.incidentDataPath, Configuration.incidentInputGDB, Configuration.patterns_ProToolboxPath, Configuration.patterns_DesktopToolboxPath])
        if (Configuration.incidentScratchGDB == None) or (not arcpy.Exists(Configuration.incidentScratchGDB)):
            Configuration.incidentScratchGDB = UnitTestUtilities.createScratch(Configuration.incidentDataPath)
        
        # set up inputs    
        self.inputPointsFeatures = os.path.join(Configuration.incidentInputGDB, "Incidents")
        self.inputLinesFeatures = os.path.join(Configuration.incidentInputGDB, "Roads")
            
    def tearDown(self):
        if Configuration.DEBUG == True: print("     CountIncidentsByLOCTestCase.tearDown")
        UnitTestUtilities.deleteScratch(Configuration.incidentScratchGDB)
        
    def test_count_incidents_pro(self):
        if Configuration.DEBUG == True: print("     CountIncidentsByLOCTestCase.test_count_incidents_pro")
        arcpy.AddMessage("Testing Count Incidents by LOC (Pro).")
        self.test_count_incidents(Configuration.patterns_ProToolboxPath)
    
    def test_count_incidents_desktop(self):
        if Configuration.DEBUG == True: print("     CountIncidentsByLOCTestCase.test_count_incidents_desktop")
        arcpy.AddMessage("Testing Count Incidents by LOC (Desktop).")
        self.test_count_incidents(Configuration.patterns_DesktopToolboxPath)
        
    def test_count_incidents(self, toolboxPath):
        try:
            if Configuration.DEBUG == True: print("     CountIncidentsByLOCTestCase.test_count_incidents")
            
            # import the toolbox
            arcpy.ImportToolbox(toolboxPath, "iaTools")
            outputCountFeatures = os.path.join(Configuration.incidentScratchGDB, "outputCount")
            
            runToolMsg = "Running tool (Count Incidents By LOC)"
            arcpy.AddMessage(runToolMsg)
            Configuration.Logger.info(runToolMsg)
            
            arcpy.CountIncidentsByLOC_iaTools(self.inputPointsFeatures, self.inputLinesFeatures, "#", outputCountFeatures)
            result = arcpy.GetCount_management(outputCountFeatures)
            featureCount = int(result.getOutput(0))
            self.assertEqual(featureCount, int(2971))
        
        except arcpy.ExecuteError:
            UnitTestUtilities.handleArcPyError()
            
        except:
            UnitTestUtilities.handleGeneralError()
            