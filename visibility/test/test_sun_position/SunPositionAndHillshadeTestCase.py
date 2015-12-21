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
import TestUtilities
import UnitTestUtilities
import UnitTestCase               
                
class SunPositionAndHillshadeTestCase(UnitTestCase.UnitTestCase):
    
    inputGDB = os.path.join(TestUtilities.vis_GeodatabasePath, "test_sun_position.gdb")
    inputArea = os.path.join(inputGDB, "inputArea")
    inputSurface = os.path.join(inputGDB, "Jbad_SRTM_USGS_EROS")
    compareResults = os.path.join(inputGDB, "compareResults")
    
    def setUp(self):
        UnitTestCase.UnitTestCase.setUp(self)
        testObjects = [TestUtilities.sunPosToolbox, self.inputGDB, self.inputArea, self.inputSurface, self.compareResults]
        UnitTestUtilities.checkGeoObjects(testObjects)
        UnitTestUtilities.createScratch(TestUtilities.vis_ScratchPath)
        
    def test_sun_position_analysis(self):
        try:
            arcpy.AddMessage("Testing Sun Position Analysis (unit).")
            print("Importing toolbox... ")
            arcpy.ImportToolbox(TestUtilities.sunPosToolbox, "sunpos")
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
            outHillshade = os.path.join(TestUtilities.vis_ScratchPath, "outputHS")
            print("Set output hillshade...")

            # Testing
            arcpy.AddMessage("Running tool (Sun Position and Hillshade)")
            # arcpy.SunPositionAnalysis_sunpos(TestUtilities.vis_inputArea, TestUtilities.vis_inputSurface, dtCompare, utcAfghanistan, outHillshade)
            arcpy.SunPositionAnalysis_sunpos(self.inputArea, self.inputSurface, dtCompare, utcAfghanistan, outHillshade)
            
            print("Comparing expected values with tool results from " + str(dtCompare) + " in " + str(utcAfghanistan))
            compareResults = self.compareResults

            arcpy.CheckOutExtension("Spatial")
            diff = Minus(Raster(outHillshade),Raster(compareResults))
            diff.save(os.path.join(TestUtilities.vis_ScratchPath, "diff"))
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
            # # Get the arcpy error messages
            # msgs = arcpy.GetMessages()
            # arcpy.AddError(msgs)
            # print(msgs)

            # # return a system error code
            # sys.exit(-1)

        except:
            UnitTestUtilities.handleGeneralError()
            # # Get the traceback object
            # tb = sys.exc_info()[2]
            # tbinfo = traceback.format_tb(tb)[0]

            # # Concatenate information together concerning the error into a message string
            # pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n"\
                # + str(sys.exc_info()[1])
            # msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

            # # Return python error messages for use in script tool or Python Window
            # arcpy.AddError(pymsg)
            # arcpy.AddError(msgs)

            # # Print Python error messages for use in Python / Python Window
            # print(pymsg + "\n")
            # print(msgs)

            # # return a system error code
            # sys.exit(-1)
            
        finally:
            arcpy.CheckInExtension("Spatial")
        
        
