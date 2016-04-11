#------------------------------------------------------------------------------
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
#------------------------------------------------------------------------------

import logging
import arcpy
from arcpy.sa import *
import sys
import traceback
import datetime
import os
import unittest
import Configuration
import UnitTestUtilities
import DataDownload

class SunPositionAndHillshadeTestCase(unittest.TestCase):

    proToolboxPath = os.path.join(Configuration.vis_ToolboxesPath, "Sun Position Analysis Tools.tbx")
    desktopToolboxPath = os.path.join(Configuration.vis_ToolboxesPath, "Sun Position Analysis Tools_10.4.tbx")

    inputGDB = None
    inputArea = None
    inputSurface = None
    compareResults = None

    sunPosUrl = "http://www.arcgis.com/sharing/content/items/bf6a04b4c9a3447b91e9c0b4074ca1e4/data"
    sunPosDataPath = None
    sunPosGDBPath = None
    scratchGDB = None

    def setUp(self):
        if Configuration.DEBUG == True: print("         SunPositionAndHillshadeTestCase.setUp")
        UnitTestUtilities.checkArcPy()

        name = "test_sun_position.gdb"
        self.sunPosDataPath = DataDownload.runDataDownload(Configuration.visibilityPaths, name, self.sunPosUrl)
        if (self.scratchGDB == None) or (not arcpy.Exists(self.scratchGDB)):
            self.scratchGDB = UnitTestUtilities.createScratch(self.sunPosDataPath)

        UnitTestUtilities.checkFilePaths([self.proToolboxPath, self.desktopToolboxPath, Configuration.visibilityPaths, self.sunPosDataPath])
        # set up inputs
        self.sunPosGDBPath = os.path.join(self.sunPosDataPath, name)
        self.inputArea = os.path.join(self.sunPosGDBPath, r"inputArea")
        self.inputSurface = os.path.join(self.sunPosGDBPath, r"Jbad_SRTM_USGS_EROS")
        self.compareResults = os.path.join(self.sunPosGDBPath, r"compareResults")
        UnitTestUtilities.checkGeoObjects([self.inputArea, self.inputSurface, self.compareResults])

    def tearDown(self):
        if Configuration.DEBUG == True: print("         SunPositionAndHillshadeTestCase.tearDown")
        UnitTestUtilities.deleteScratch(self.scratchGDB)

    def test_sun_position_analysis_pro(self):
        arcpy.AddMessage("Testing Sun Position Analysis (Pro).")
        self.test_sun_position_analysis(self.proToolboxPath)

    def test_sun_position_analysis_desktop(self):
        arcpy.AddMessage("Testing Sun Position Analysis (Desktop).")
        self.test_sun_position_analysis(self.desktopToolboxPath)

    def test_sun_position_analysis(self, toolboxPath):
        try:
            print("Importing toolbox... ")
            arcpy.ImportToolbox(toolboxPath)
            arcpy.env.overwriteOutput = True

            # Inputs
            print("Setting up inputs... ")
            # '''
            # Tool comparison is based on static dataset in Web Mercator
            # over Afghanistan, for 7/30/2015 at 14:28:36.
            # '''
            dtCompare = datetime.datetime(2015, 7, 30, 14, 28, 36)
            print("Set date...")
            utcAfghanistan = r'(UTC+4:30) Afghanistan'
            print("Set UTCAfg...")
            # outHillshade = os.path.join(Configuration.vis_ScratchPath, "outputHS")
            outHillshade = os.path.join(self.scratchGDB, "outputHS")
            print("Set output hillshade...")

            # Testing
            runToolMsg = "Running tool (Sun Position and Hillshade)"
            arcpy.AddMessage(runToolMsg)
            Configuration.Logger.info(runToolMsg)
            arcpy.SunPositionAnalysis_sunpos(self.inputArea, self.inputSurface, dtCompare, utcAfghanistan, outHillshade)

            compareMessage = "Comparing expected values with tool results from " + str(dtCompare) + " in " + str(utcAfghanistan)
            Configuration.Logger.info(compareMessage)
            compareResults = self.compareResults

            arcpy.CheckOutExtension("Spatial")
            diff = Minus(Raster(outHillshade),Raster(compareResults))
            diff.save(os.path.join(self.scratchGDB, "diff"))
            arcpy.CalculateStatistics_management(diff)
            rasMinimum = float(arcpy.GetRasterProperties_management(diff,"MINIMUM").getOutput(0))
            rasMaximum = float(arcpy.GetRasterProperties_management(diff,"MAXIMUM").getOutput(0))
            rasMean = float(arcpy.GetRasterProperties_management(diff,"MEAN").getOutput(0))
            rasSTD = float(arcpy.GetRasterProperties_management(diff,"STD").getOutput(0))
            rasUnique = int(arcpy.GetRasterProperties_management(diff,"UNIQUEVALUECOUNT").getOutput(0))

            self.assertEqual(rasMaximum, float(0))
            self.assertEqual(rasMinimum, float(0))
            self.assertEqual(rasUnique, int(1))

            # if (rasMaximum == float(0)) and (rasMinimum == float(0)) and (rasUnique == int(1)):
                # print("No differences between tool output and expected results.")
                # print("Test Passed")
            # else:
                # msg = "ERROR IN TOOL RESULTS: \n"\
                    # + "Difference between tool output and expected results found:\n"\
                    # + "Difference Minimum: " + str(rasMinimum) + "\n"\
                    # + "Difference Maximum: " + str(rasMaximum) + "\n"\
                    # + "Difference Mean: " + str(rasMean) + "\n"\
                    # + "Difference Std. Deviation: " + str(rasSTD) + "\n"\
                    # + "Difference Number of Unique Values: " + str(rasUnique) + "\n"
                # raise ValueDifferenceError(msg)

        except arcpy.ExecuteError:
            UnitTestUtilities.handleArcPyError()

        except:
            UnitTestUtilities.handleGeneralError()
            
        finally:
            arcpy.CheckInExtension("Spatial")
        
        
