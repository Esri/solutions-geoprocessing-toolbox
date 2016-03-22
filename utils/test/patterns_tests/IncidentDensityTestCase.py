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
# IncidentDensityTestCase.py
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

class IncidentDensityTestCase(unittest.TestCase):
    ''' Test all tools and methods related to the Incident Density tool
    in the Incident Analysis toolbox'''
     
    inputPointFeatures = None
    inputBoundaryFeatures = None
    
    def setUp(self):
        if Configuration.DEBUG == True: print("     IncidentDensityTestCase.setUp")    
        UnitTestUtilities.checkArcPy()
        
        Configuration.incidentDataPath = DataDownload.runDataDownload(Configuration.patternsPaths, Configuration.incidentGDBName, Configuration.incidentURL)
        if (Configuration.incidentScratchGDB == None) or (not arcpy.Exists(Configuration.incidentScratchGDB)):
            Configuration.incidentScratchGDB = UnitTestUtilities.createScratch(Configuration.incidentDataPath)
        Configuration.incidentInputGDB = os.path.join(Configuration.incidentDataPath, Configuration.incidentGDBName)
        
        UnitTestUtilities.checkFilePaths([Configuration.incidentDataPath, Configuration.incidentInputGDB, Configuration.patterns_ProToolboxPath, Configuration.patterns_DesktopToolboxPath])
        if (Configuration.incidentScratchGDB == None) or (not arcpy.Exists(Configuration.incidentScratchGDB)):
            Configuration.incidentScratchGDB = UnitTestUtilities.createScratch(Configuration.incidentDataPath)
            
        
        self.inputPointFeatures = os.path.join(Configuration.incidentInputGDB, "Incidents")
        self.inputBoundaryFeatures = os.path.join(Configuration.incidentInputGDB, "Districts")
        
        
    def tearDown(self):
        if Configuration.DEBUG == True: print("     IncidentDensityTestCase.tearDown")
        UnitTestUtilities.deleteScratch(Configuration.incidentScratchGDB)
        
    def test_incident_density_pro(self):
        if Configuration.DEBUG == True: print("     IncidentDensityTestCase.test_incident_density_pro")
        arcpy.AddMessage("Testing Incident Density (Pro).")
        self.test_incident_density(Configuration.patterns_ProToolboxPath)
    
    def test_incident_density_desktop(self):
        if Configuration.DEBUG == True: print("     IncidentDensityTestCase.test_incident_density_desktop")
        arcpy.AddMessage("Testing Incident Density (Desktop).")
        self.test_incident_density(Configuration.patterns_DesktopToolboxPath)
        
    def test_incident_density(self, toolboxPath):
        try:
            if Configuration.DEBUG == True: print("     IncidentDensityTestCase.test_incident_density")
            
            arcpy.CheckOutExtension("Spatial")        
            arcpy.ImportToolbox(toolboxPath, "iaTools")
            
            runToolMsg = "Running tool (Incident Density)"
            arcpy.AddMessage(runToolMsg)
            Configuration.Logger.info(runToolMsg)
            
            outputDensity = os.path.join(Configuration.incidentScratchGDB, "outputDensity")
            arcpy.IncidentDensity_iaTools(self.inputPointFeatures, self.inputBoundaryFeatures, outputDensity)
            arcpy.CheckInExtension("Spatial")
            self.assertTrue(arcpy.Exists(outputDensity))
            
        except arcpy.ExecuteError:
            UnitTestUtilities.handleArcPyError()
            
        except:
            UnitTestUtilities.handleGeneralError()
            
            