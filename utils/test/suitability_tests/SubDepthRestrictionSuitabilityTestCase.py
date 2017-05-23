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
# SubDepthRestrictionSuitabilityTestCase.py
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

class SubDepthRestrictionSuitabilityTestCase(unittest.TestCase):
    ''' Test all tools and methods related to the Sub Depth Restriction Suitability tool
    in the Maritime Decision Aid toolbox'''
    
    maritimeGDB = None
    bathymetry = None
    subDepthOutput = None
    
    def setUp(self):
        if Configuration.DEBUG == True: print("     SubDepthRestrictionSuitabilityTestCase.setUp")
            
        UnitTestUtilities.checkArcPy()
        Configuration.maritimeDataPath = DataDownload.runDataDownload(Configuration.suitabilityPaths, Configuration.maritimeGDBName, Configuration.maritimeURL)
        if(Configuration.maritimeScratchGDB == None) or (not arcpy.Exists(Configuration.maritimeScratchGDB)):
            Configuration.maritimeScratchGDB = UnitTestUtilities.createScratch(Configuration.maritimeDataPath)
            
        self.maritimeDataGDB = os.path.join(Configuration.maritimeDataPath, "Maritime Decision Aid Tools.gdb")
        
        self.bathymetry = os.path.join(self.maritimeDataGDB, "SoCalDepthsGEBCO")
        self.subDepthOutput = os.path.join(Configuration.maritimeScratchGDB, "SubDepth")
        UnitTestUtilities.checkFilePaths([Configuration.maritimeDataPath, Configuration.maritime_DesktopToolboxPath, Configuration.maritime_ProToolboxPath])
        
    def tearDown(self):
        if Configuration.DEBUG == True: print("     SubDepthRestrictionSuitabilityTestCase.tearDown")
        UnitTestUtilities.deleteScratch(Configuration.maritimeScratchGDB)
    
    def test_sub_depth_restriction_suitability_desktop(self):
        arcpy.AddMessage("Testing Sub Depth Restriction Suitability (Desktop).")
        self.test_sub_depth_restriction_suitability(Configuration.maritime_DesktopToolboxPath)
    
    def test_sub_depth_restriction_suitability_pro(self):
        arcpy.AddMessage("Testing Sub Depth Restriction Suitability (Pro).")
        self.test_sub_depth_restriction_suitability(Configuration.maritime_ProToolboxPath)
        
    def test_sub_depth_restriction_suitability(self, toolboxPath):
        try:
            if Configuration.DEBUG == True: print("     SubDepthRestrictionSuitabilityTestCase.test_sub_depth_restriction_suitability")
            
            arcpy.ImportToolbox(toolboxPath, "mdat")
            runToolMessage = "Running tool (Sub Depth Restriction Suitability)"
            arcpy.AddMessage(runToolMessage)
            Configuration.Logger.info(runToolMessage)
            
            arcpy.CheckOutExtension("Spatial")
            arcpy.SubDepthRestrictionSuitability_mdat(self.bathymetry, Submarine_Depth_Navigability=self.subDepthOutput)

            subs = int(arcpy.GetCount_management(self.subDepthOutput).getOutput(0))
            self.assertEqual(subs, int(856))
            
        except arcpy.ExecuteError:
            UnitTestUtilities.handleArcPyError()
            
        except:
            UnitTestUtilities.handleGeneralError()
        
        finally:
            arcpy.CheckInExtension("Spatial")
            
            
        
        
        