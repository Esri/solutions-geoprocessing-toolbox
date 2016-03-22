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
# FindSubmarinesTestCase.py
# --------------------------------------------------
# requirements:
# * ArcGIS Desktop 10.X+ or ArcGIS Pro 1.X
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

class FindSubmarinesTestCase(unittest.TestCase):
    ''' Test all tools and methods related to the Find Submarines tool
    in the Maritime Decision Aid toolbox'''
    
    def setUp(self):
        if Configuration.DEBUG == True: print("     FindSubmarinesTestCase.setUp")
        
    def tearDown(self):
        if Configuration.DEBUG == True: print("     FindSubmarinesTestCase.tearDown")
    
    def test_find_submarine_desktop(self):
        arcpy.AddMessage("Testing Find Submarines (Desktop).")
        self.test_find_submarine(Configuration.maritime_DesktopToolboxPath)
        
    def test_find_submarine_pro(self):
        arcpy.AddMessage("Testing Find Submarines (Pro).")
        self.test_find_submarine(Configuration.maritime_ProToolboxPath)
        
    def test_find_submarine(self, toolboxPath):
        try:
            if Configuration.DEBUG == True: print("     FindSubmarinesTestCase.test_find_submarine")
            
            runToolMessage = "Running tool (Find Submarines)"
            arcpy.AddMessage(runToolMessage)
            Configuration.Logger.info(runToolMessage)
            
            
        except arcpy.ExecuteError:
            UnitTestUtilities.handleArcPyError()
            
        except:
            UnitTestUtilities.handleGeneralError()
            
    
    