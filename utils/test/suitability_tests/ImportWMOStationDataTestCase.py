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
# ImportWMOStationDataTestCase.py
# --------------------------------------------------
# requirements: 
# * ArcGIS Desktop 10.X
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

class ImportWMOStationDataTestCase(unittest.TestCase):
    ''' Test all tools and methods related to the Import WMO Station Data tool
    in the Military Aspects of Weather toolbox'''
    
    WMOGDB = None
    WMOFolder = None
    StationDataInputFC = None
    StationDataOutputFC = None
    outputFCName = None
    
    def setUp(self):
        if Configuration.DEBUG == True: print("     ImportWMOStationDataTestCase.setUp")
        UnitTestUtilities.checkArcPy()
        self.outputFCName = "WMOStationData"
        
        # DO NOT run data download again; dependent data is needed from the ImportWMOStationsTestCase
        self.WMOGDB = os.path.join(Configuration.suitabilityDataPath, "WMO.gdb")
        
        self.StationDataInputFC = os.path.join(self.WMOGDB, "WMOFC_output")
        self.StationDataOutputFC = os.path.join(self.WMOGDB, self.outputFCName)
        self.WMOFolder = os.path.join(Configuration.suitabilityDataPath, "WMOStationFiles")
        
        UnitTestUtilities.checkFilePaths([Configuration.suitabilityDataPath, Configuration.maow_ToolboxPath, self.WMOFolder, self.WMOGDB])
        UnitTestUtilities.deleteIfExists(self.StationDataOutputFC)
        
    def tearDown(self):
        if Configuration.DEBUG == True: print("     ImportWMOStationDataTestCase.tearDown")
        
    def test_import_wmo_station_data(self):
        try:  
            if Configuration.DEBUG == True: print("     ImportWMOStationDataTestCase.test_import_wmo_station_data")
            arcpy.AddMessage("Testing Import WMO Station Data (Desktop)")    
        
            arcpy.ImportToolbox(Configuration.maow_ToolboxPath, "maow")
            runToolMessage = "Running tool (Import WMO Station Data)"
            arcpy.AddMessage(runToolMessage)
            Configuration.Logger.info(runToolMessage)
            
            arcpy.ImportWMOStationData_maow(self.WMOGDB, self.outputFCName, self.WMOFolder, self.StationDataInputFC) 

            wmoStationCount = int(arcpy.GetCount_management(self.StationDataOutputFC).getOutput(0))
            self.assertEqual(wmoStationCount, int(252))
            
        except arcpy.ExecuteError:
            UnitTestUtilities.handleArcPyError()
            
        except:
            UnitTestUtilities.handleGeneralError()
        
    