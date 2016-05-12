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
# VisibilityRangeAtSeaTestCase.py
# --------------------------------------------------
# requirements:
# * ArcGIS Desktop 10.X+ or ArcGIS Pro 1.X+
# * Python 2.7 or Python 3.4
#
# author: ArcGIS Solutions
# company: Esri
#
# ==================================================
# history:
# 3/1/2016 - JH - initial creation
# ==================================================

import unittest
import arcpy
import os
import UnitTestUtilities
import Configuration
import DataDownload

class VisibilityRangeAtSeaTestCase(unittest.TestCase):
    ''' Test all tools and methods related to the Visibility Range At Sea tool
    in the Maritime Decision Aid toolbox'''
    
    maritimeDataGDB = None
    visibleRange = None
    vessel = None
    shipLocation = None
    
    def setUp(self):
        if Configuration.DEBUG == True: print("     VisibilityRangeAtSeaTestCase.setUp")
        
        UnitTestUtilities.checkArcPy()
        Configuration.maritimeDataPath = DataDownload.runDataDownload(Configuration.suitabilityPaths, Configuration.maritimeGDBName, Configuration.maritimeURL)
        if(Configuration.maritimeScratchGDB == None) or (not arcpy.Exists(Configuration.maritimeScratchGDB)):
            Configuration.maritimeScratchGDB = UnitTestUtilities.createScratch(Configuration.maritimeDataPath)
            
        self.maritimeDataGDB = os.path.join(Configuration.maritimeDataPath, "Maritime Decision Aid Tools.gdb")
        
        self.visibleRange = os.path.join(Configuration.maritimeScratchGDB, "visRangeOutput")
        self.vessel = os.path.join(Configuration.maritimeScratchGDB, "vesselOutput")
        self.shipLocation = os.path.join(self.maritimeDataGDB, "Vessel")
        
        UnitTestUtilities.checkFilePaths([Configuration.maritimeDataPath, Configuration.maritime_DesktopToolboxPath, Configuration.maritime_ProToolboxPath])
        
    def tearDown(self):
        if Configuration.DEBUG == True: print("     VisibilityRangeAtSeaTestCase.tearDown")
        UnitTestUtilities.deleteScratch(Configuration.maritimeScratchGDB)
    
    def test_visibility_range_at_sea_desktop(self):
        arcpy.AddMessage("Testing Visibility Range At Sea (Desktop).")
        self.test_visibility_range_at_sea(Configuration.maritime_DesktopToolboxPath)
        
    def test_visibility_range_at_sea_pro(self):
        arcpy.AddMessage("Testing Visibility Range At Sea (Pro).")
        self.test_visibility_range_at_sea(Configuration.maritime_ProToolboxPath)
        
    def test_visibility_range_at_sea(self, toolboxPath):
        try:
            if Configuration.DEBUG == True: print("     VisibilityRangeAtSeaTestCase.test_visibility_range_at_sea")
                
            arcpy.ImportToolbox(toolboxPath, "mdat")
            runToolMessage = "Running tool (Visibility Range At Sea)"
            arcpy.AddMessage(runToolMessage)
            Configuration.Logger.info(runToolMessage)
            
            arcpy.HorizonVisibility_mdat(self.shipLocation, "#", self.visibleRange, self.vessel)
            
            visibleRangeCount = int(arcpy.GetCount_management(self.visibleRange).getOutput(0))
            self.assertEqual(visibleRangeCount, int(1))
            
            vesselCount = int(arcpy.GetCount_management(self.vessel).getOutput(0))
            self.assertEqual(vesselCount, int(1))
            
            
        except arcpy.ExecuteError:
            UnitTestUtilities.handleArcPyError()
            
        except:
            UnitTestUtilities.handleGeneralError()
            