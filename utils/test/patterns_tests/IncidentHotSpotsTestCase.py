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
# IncidentHotSpotsTestCase.py
# --------------------------------------------------
# requirments: ArcGIS X.X, Python 2.7 or Python 3.4
# author: ArcGIS Solutions
# company: Esri
# ==================================================
# history:
# 12/16/2015 - JH - initial creation
# ==================================================

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
        if Configuration.DEBUG == True: print("     IncidentHotSpotsTestCase.setUp")    
        UnitTestUtilities.checkArcPy()
        
        Configuration.incidentDataPath = DataDownload.runDataDownload(Configuration.patternsPaths, Configuration.incidentGDBName, Configuration.incidentURL)
        if (Configuration.incidentScratchGDB == None) or (not arcpy.Exists(Configuration.incidentScratchGDB)):
            Configuration.incidentScratchGDB = UnitTestUtilities.createScratch(Configuration.incidentDataPath)
        Configuration.incidentInputGDB = os.path.join(Configuration.incidentDataPath, Configuration.incidentGDBName)
        
        UnitTestUtilities.checkFilePaths([Configuration.incidentDataPath, Configuration.incidentInputGDB, Configuration.patterns_ProToolboxPath, Configuration.patterns_DesktopToolboxPath])
            
        self.inputPointFeatures = os.path.join(Configuration.incidentInputGDB, "Incidents")
        self.inputBoundaryFeatures = os.path.join(Configuration.incidentInputGDB, "Districts")
            
    def tearDown(self):
        if Configuration.DEBUG == True: print("     IncidentHotSpotsTestCase.tearDown")
        UnitTestUtilities.deleteScratch(Configuration.incidentScratchGDB)
        
    def test_incident_hot_spots_pro(self):
        if Configuration.DEBUG == True: print("     IncidentHotSpotsTestCase.test_incident_hot_spots_pro")
        arcpy.AddMessage("Testing Incident Hot Spots (Pro).")
        self.test_incident_hot_spots(Configuration.patterns_ProToolboxPath)
    
    def test_incident_hot_spots_desktop(self):
        if Configuration.DEBUG == True: print("     IncidentHotSpotsTestCase.test_incident_hot_spots_desktop")    
        arcpy.AddMessage("Testing Incident Hot Spots (Desktop).")
        self.test_incident_hot_spots(Configuration.patterns_DesktopToolboxPath)
        
    def test_incident_hot_spots(self, toolboxPath):
        try:
            if Configuration.DEBUG == True: print("     IncidentHotSpotsTestCase.test_incident_hot_spots")
            
            arcpy.ImportToolbox(toolboxPath, "iaTools")
            
            runToolMessage = "Running tool (Incident Hot Spots)"
            arcpy.AddMessage(runToolMessage)
            Configuration.Logger.info(runToolMessage)
            
            outputFeatures = os.path.join(Configuration.incidentScratchGDB, "outputHotSpots")
            arcpy.IncidentHotSpots_iaTools(self.inputPointFeatures, self.inputBoundaryFeatures, outputFeatures)

            result = arcpy.GetCount_management(outputFeatures)
            featureCount = int(result.getOutput(0))
            self.assertEqual(featureCount, int(7302))
            
        except arcpy.ExecuteError:
            UnitTestUtilities.handleArcPyError()
            
        except:
            UnitTestUtilities.handleGeneralError()
            
        