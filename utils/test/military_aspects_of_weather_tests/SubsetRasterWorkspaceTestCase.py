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
# SubsetRasterWorkspaceTestCase.py
# --------------------------------------------------
# requirements:
# * ArcGIS Desktop 10.X+
# * Python 2.7
#
# author: ArcGIS Solutions
# company: Esri
#
# ==================================================
# history:
# 2/10/2016 - JH - initial creation
# ==================================================


import unittest
import arcpy
import os
import UnitTestUtilities
import Configuration
import DataDownload

class SubsetRasterWorkspaceTestCase(unittest.TestCase):
    ''' Test all tools and methods related to the Subset Raster Workspace tool
    in the Military Aspects of Weather toolbox'''
    
    sourceWorkspace = None
    targetWorkspace = None
    
    def setUp(self):
        if Configuration.DEBUG == True: print("     SubsetRasterWorkspaceTestCase.setUp")
        UnitTestUtilities.checkArcPy()

        # DO NOT run data download again; dependent data is needed from ImportCRUToRasterTestCase
        self.sourceWorkspace = os.path.join(Configuration.suitabilityDataPath, "CRURasters.gdb")
        self.targetWorkspace = os.path.join(Configuration.suitabilityDataPath, "SubsetRasters.gdb")
        
        UnitTestUtilities.checkFilePaths([Configuration.suitabilityDataPath, Configuration.maow_ToolboxPath, self.sourceWorkspace, self.targetWorkspace])
    
    def tearDown(self):
        if Configuration.DEBUG == True: print("     SubsetRasterWorkspaceTestCase.tearDown")
        
    def test_subset_raster_workspace(self):
        try:    
            if Configuration.DEBUG == True: print("     SubsetRasterWorkspaceTestCase.test_subset_raster_workspace")
            arcpy.AddMessage("Testing Subset Raster Workspace (Desktop)")
        
            arcpy.ImportToolbox(Configuration.maow_ToolboxPath, "maow")
            runToolMessage = "Running tool (Subset Raster Workspace)"
            arcpy.AddMessage(runToolMessage)
            Configuration.Logger.info(runToolMessage)
            
            inputAreaPath = os.path.join(self.sourceWorkspace, "AOI")
            inputArea = arcpy.FeatureSet(inputAreaPath)
            arcpy.SubsetRasterWorkspace_maow(inputArea, self.sourceWorkspace, self.targetWorkspace)
            
            dtr_feb_output = os.path.join(self.targetWorkspace, "dtr_feb")
            self.assertTrue(arcpy.Exists(dtr_feb_output))
            dtr_desc = arcpy.Describe(dtr_feb_output)
            self.assertEqual(dtr_desc.bandCount, int(1))
            
        except arcpy.ExecuteError:
            UnitTestUtilities.handleArcPyError()
            
        except:
            UnitTestUtilities.handleGeneralError()
            
        