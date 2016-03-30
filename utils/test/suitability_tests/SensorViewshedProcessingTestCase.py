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
# 3/28/2016 - JH - initial creation
# ==================================================

import unittest
import arcpy
import os
import UnitTestUtilities
import Configuration
import DataDownload

class SensorViewshedProcessingTestCase(unittest.TestCase):
    ''' Test all tools and methods related to the Sensor Viewshed Processing tool
    in the Maritime Decision Aid toolbox'''
    
    maritimeOutputGDB = None
    maritimeDataGDB = None
    AOI = None
    sensorLocations = None
    bathymetry = None
    viewshedOutput = None
    
    def setUp(self):
        if Configuration.DEBUG == True: print("     SensorViewshedProcessingTestCase.setUp")    
        
        UnitTestUtilities.checkArcPy()
        self.maritimeOutputGDB = os.path.join(Configuration.maritimeDataPath, "output.gdb")
        self.maritimeDataGDB = os.path.join(Configuration.maritimeDataPath, "data.gdb")

        self.AOI = os.path.join(self.maritimeDataGDB, "AOI")
        self.sensorLocations = os.path.join(self.maritimeDataGDB, "InputSensors")
        self.bathymetry = os.path.join(self.maritimeDataGDB, "SoCalDepths32Aux")
        self.viewshedOutput = os.path.join(self.maritimeOutputGDB, "viewshedOutput")
        
        UnitTestUtilities.checkFilePaths([Configuration.maritimeDataPath, Configuration.maritime_DesktopToolboxPath, Configuration.maritime_ProToolboxPath])
        UnitTestUtilities.deleteIfExists(self.viewshedOutput)
        
    def tearDown(self):
        if Configuration.DEBUG == True: print("     SensorViewshedProcessingTestCase.tearDown")
    
    def test_sensor_viewshed_processing_desktop(self):
        arcpy.AddMessage("Testing Sensor Viewshed Processing (Desktop).")
        self.test_sensor_viewshed_processing(Configuration.maritime_DesktopToolboxPath)
        
    def test_sensor_viewshed_processing_pro(self):
        arcpy.AddMessage("Testing Sensor Viewshed Processing (Pro).")
        self.test_sensor_viewshed_processing(Configuration.maritime_ProToolboxPath)
        
    def test_sensor_viewshed_processing(self, toolboxPath):
        try:
            if Configuration.DEBUG == True: print("     SensorViewshedProcessingTestCase.test_sensor_viewshed_processing") 
            
            arcpy.ImportToolbox(toolboxPath, "mdat")
            runToolMessage = "Running tool (Sensor Viewshed Processing)"
            arcpy.AddMessage(runToolMessage)
            Configuration.Logger.info(runToolMessage)
            
            arcpy.CheckOutExtension("Spatial")
            arcpy.SensorProcessing_mdat(self.sensorLocations, self.bathymetry, self.AOI, self.viewshedOutput)
            
            self.assertTrue(arcpy.Exists(self.viewshedOutput))
       
            
        except arcpy.ExecuteError:
            UnitTestUtilities.handleArcPyError()
            
        except:
            UnitTestUtilities.handleGeneralError()
            
        finally:
            arcpy.CheckInExtension("Spatial")
            
        