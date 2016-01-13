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
# HotSpotsByAreaTestCase.py
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

class HotSpotsByAreaTestCase(unittest.TestCase):
    ''' Test all tools and methods related to the Hot Spots by Area tool
    in the Incident Analysis toolbox'''
    
    #TODO: find this test
    proToolboxPath = os.path.join(Configuration.patterns_ToolboxesPath, "Incident Analysis Tools.tbx")
    desktopToolboxPath = os.path.join(Configuration.patterns_ToolboxesPath, "Incident Analysis Tools_10.4.tbx")
    scratchGDB = None
    incidentDataPath = os.path.join(Configuration.patternsPaths, "data")
    incidentGDB = os.path.join(incidentDataPath, "IncidentAnalysis.gdb")
    
    def setUp(self):
        if Configuration.DEBUG == True: print("     HotSpotsByAreaTestCase.setUp")
        UnitTestUtilities.checkArcPy()
        UnitTestUtilities.checkFilePaths([self.incidentDataPath, self.proToolboxPath, self.desktopToolboxPath])
        if (self.scratchGDB == None) or (not arcpy.Exists(self.scratchGDB)):
            self.scratchGDB = UnitTestUtilities.createScratch(self.incidentDataPath)
            
    def tearDown(self):
        if Configuration.DEBUG == True: print("     HotSpotsByAreaTestCase.tearDown")
        UnitTestUtilities.deleteScratch(self.scratchGDB)
        
    def test_hot_spots_by_area_pro(self):
        if Configuration.DEBUG == True: print("     HotSpotsByAreaTestCase.test_hot_spots_by_area_pro")
        arcpy.AddMessage("Testing Hot Spots by Area (Pro).")
        self.test_hot_spots_by_area(self.proToolboxPath)
    
    def test_hot_spots_by_area_desktop(self):
        if Configuration.DEBUG == True: print("     HotSpotsByAreaTestCase.test_hot_spots_by_area_desktop")    
        arcpy.AddMessage("Testing Hot Spots by Area (Desktop).")
        self.test_hot_spots_by_area(self.desktopToolboxPath)
        
    def test_hot_spots_by_area(self, toolboxPath):
        try:
            if Configuration.DEBUG == True: print("     HotSpotsByAreaTestCase.test_hot_spots_by_area")
                
        except arcpy.ExecuteError:
            UnitTestUtilities.handleArcPyError()
            
        except:
            UnitTestUtilities.handleGeneralError()
            
            