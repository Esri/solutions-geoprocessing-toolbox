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
# IncidentTableToPointTestCase.py
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

class IncidentTableToPointTestCase(unittest.TestCase):
    ''' Test all tools and methods related to the Incident Table to Point tool
    in the Incident Analysis toolbox'''
    
    inputTable = None
    
    def setUp(self):
        if Configuration.DEBUG == True: print("     IncidentTableToPointTestCase.setUp")    
        UnitTestUtilities.checkArcPy()
        UnitTestUtilities.checkFilePaths([Configuration.incidentDataPath, Configuration.incidentInputGDB, Configuration.patterns_ProToolboxPath, Configuration.patterns_DesktopToolboxPath])
        if (Configuration.incidentScratchGDB == None) or (not arcpy.Exists(Configuration.incidentScratchGDB)):
            Configuration.incidentScratchGDB = UnitTestUtilities.createScratch(Configuration.incidentDataPath)
            
        self.inputTable = os.path.join(Configuration.incidentInputGDB, "MontereyIncidents")
            
    def tearDown(self):
        if Configuration.DEBUG == True: print("     IncidentTableToPointTestCase.tearDown")
        UnitTestUtilities.deleteScratch(Configuration.incidentScratchGDB)
        
    def test_incident_table_to_point_pro(self):
        if Configuration.DEBUG == True: print("     IncidentTableToPointTestCase.test_incident_table_to_point_pro")
        arcpy.AddMessage("Testing Incident Table To Point (Pro).")
        self.test_incident_table_to_point(Configuration.patterns_ProToolboxPath)
    
    def test_incident_table_to_point_desktop(self):
        if Configuration.DEBUG == True: print("     IncidentTableToPointTestCase.test_incident_table_to_point_desktop")    
        arcpy.AddMessage("Testing Incident Table To Point (Desktop).")
        self.test_incident_table_to_point(Configuration.patterns_DesktopToolboxPath)
        
    def test_incident_table_to_point(self, toolboxPath):
        try:
            if Configuration.DEBUG == True: print("     IncidentTableToPointTestCase.test_incident_table_to_point")
            
            arcpy.ImportToolbox(toolboxPath, "iaTools")
            
            runToolMessage = "Running tool (Incident Table To Point)"
            arcpy.AddMessage(runToolMessage)
            Configuration.Logger.info(runToolMessage)
            coordFormat = "MGRS"
            xField = "MGRS"
            yField = "MGRS"
            outputTable = os.path.join(Configuration.incidentScratchGDB, "outputTable")
            arcpy.IncidentTableToPoint_iaTools(self.inputTable, coordFormat, xField, yField, outputTable)
            
            result = arcpy.GetCount_management(outputTable)
            featureCount = int(result.getOutput(0))
            self.assertEqual(featureCount, int(5532))
            
        
        except arcpy.ExecuteError:
            UnitTestUtilities.handleArcPyError()
            
        except:
            UnitTestUtilities.handleGeneralError()
            