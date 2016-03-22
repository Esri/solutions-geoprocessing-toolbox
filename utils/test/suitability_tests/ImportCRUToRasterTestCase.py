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
# ImportCRUToRasterTestCase.py
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

class ImportCRUToRasterTestCase(unittest.TestCase):
    ''' Test all tools and methods related to the Import CRU CL 2.0 To Raster tool
    in the Military Aspects of Weather toolbox'''
    
    inputCRUFolder = None
    outputWorkspace = None
    
    def setUp(self):
        if Configuration.DEBUG == True: print("     ImportCRUToRasterTestCase.setUp")
        UnitTestUtilities.checkArcPy()

        Configuration.suitabilityDataPath = DataDownload.runDataDownload(Configuration.suitabilityPaths, "MilitaryAspectsOfWeatherTestData", Configuration.maowURL)
        self.inputCRUFolder = os.path.join(Configuration.suitabilityDataPath, "CRUdata")
        self.outputWorkspace = os.path.join(Configuration.suitabilityDataPath, "CRURasters.gdb")
       
        UnitTestUtilities.checkFilePaths([Configuration.suitabilityDataPath, Configuration.maow_ToolboxPath, self.outputWorkspace])
        
    def tearDown(self):
        if Configuration.DEBUG == True: print("     ImportCRUToRasterTestCase.tearDown")
        
    def test_import_cru_to_raster(self):
        try:
            if Configuration.DEBUG == True: print("     ImportCRUToRasterTestCase.test_import_cru_to_raster")
            arcpy.AddMessage("Testing Import CRU CL2.0 To Raster (Desktop)")
        
            arcpy.ImportToolbox(Configuration.maow_ToolboxPath, "maow")
            runToolMessage = "Running tool (Import CRU CL2.0 To Raster)"
            arcpy.AddMessage(runToolMessage)
            Configuration.Logger.info(runToolMessage)
        
            arcpy.ImportCRUCL2ToRaster_maow(self.inputCRUFolder, self.outputWorkspace)
            
            # check that dtr_feb raster exists, then check that its bandCount = 1
            dtr_feb_output = os.path.join(self.outputWorkspace, "dtr_feb")
            self.assertTrue(arcpy.Exists(dtr_feb_output))
            dtr_desc = arcpy.Describe(dtr_feb_output)
            self.assertEqual(dtr_desc.bandCount, int(1))
            
        except arcpy.ExecuteError:
            UnitTestUtilities.handleArcPyError()
            
        except:
            UnitTestUtilities.handleGeneralError()
            
            
        