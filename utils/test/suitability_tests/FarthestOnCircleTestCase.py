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
# FarthestOnCircleTestCase.py
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

class FarthestOnCircleTestCase(unittest.TestCase):
    ''' Test all tools and methods related to the Farthest On Circle tool
    in the Maritime Decision Aid toolbox'''
    
    maritimeDataGDB = None
    position = None
    hoursOfTransit = None
    
    def setUp(self):
        if Configuration.DEBUG == True: print("     FarthestOnCircleTestCase.setUp")    
        
        UnitTestUtilities.checkArcPy()
        Configuration.maritimeDataPath = DataDownload.runDataDownload(Configuration.suitabilityPaths, Configuration.maritimeGDBName, Configuration.maritimeURL)
        if(Configuration.maritimeScratchGDB == None) or (not arcpy.Exists(Configuration.maritimeScratchGDB)):
            Configuration.maritimeScratchGDB = UnitTestUtilities.createScratch(Configuration.maritimeDataPath)
            
        self.maritimeDataGDB = os.path.join(Configuration.maritimeDataPath, "Maritime Decision Aid Tools.gdb")

        self.position = os.path.join(self.maritimeDataGDB, "Vessel")
        self.hoursOfTransit = os.path.join(Configuration.maritimeScratchGDB, "hoursOutput")
        UnitTestUtilities.checkFilePaths([Configuration.maritimeDataPath, Configuration.maritime_DesktopToolboxPath, Configuration.maritime_ProToolboxPath])
        
    def tearDown(self):
        if Configuration.DEBUG == True: print("     FarthestOnCircleTestCase.tearDown")
        UnitTestUtilities.deleteScratch(Configuration.maritimeScratchGDB)
    
    def test_farthest_on_circle_desktop(self):
        arcpy.AddMessage("Testing Farthest On Circle (Desktop).")
        self.test_farthest_on_cirle(Configuration.maritime_DesktopToolboxPath)
        
    def test_farthest_on_circle_pro(self):
        arcpy.AddMessage("Testing Farthest On Circle (Pro).")
        self.test_farthest_on_cirle(Configuration.maritime_ProToolboxPath)
        
    def test_farthest_on_cirle(self, toolboxPath):
        try:
            if Configuration.DEBUG == True: print("     FarthestOnCircleTestCase.test_farthest_on_cirle") 
            
            arcpy.ImportToolbox(toolboxPath, "mdat")
            runToolMessage = "Running tool (Farthest On Circle)"
            arcpy.AddMessage(runToolMessage)
            Configuration.Logger.info(runToolMessage)
            
            arcpy.CheckOutExtension("Spatial")
            arcpy.FarthestOnCircle_mdat(self.position, "#", "#", self.hoursOfTransit)
            
            self.assertTrue(arcpy.Exists(self.hoursOfTransit))
       
            
        except arcpy.ExecuteError:
            UnitTestUtilities.handleArcPyError()
            
        except:
            UnitTestUtilities.handleGeneralError()
            
        finally:
            arcpy.CheckInExtension("Spatial")
            
        