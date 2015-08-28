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
# TestSunPositionAndHillshade.py
# Description: Test Sun Position Analysis Tools
# Requirements: ArcGIS Desktop Standard
# ----------------------------------------------------------------------------

import arcpy
from arcpy.sa import *
import sys
import traceback
import TestUtilities
import os
import datetime

import SunPositionAndHillshadeUnitTest

try:
    ###### Call Unit Test code
    sunPosTestCase = SunPositionAndHillshadeUnitTest.SunPositionAndHillshadeUnitTest('test_sun_position_analysis')
    sunPosTestCase.run()
    
    ######
    
    # print("Importing toolbox... ")
    # arcpy.ImportToolbox(TestUtilities.toolbox, "sunpos")
    # arcpy.env.overwriteOutput = True

    # # Inputs
    # print("Setting up inputs... ")
    # '''
    # Tool comparison is based on static dataset in Web Mercator
    # over Afghanistan, for 7/30/2015 at 14:28:36.
    # '''
    # dtCompare = datetime.datetime(2015, 7, 30, 14, 28, 36)
    # utcAfghanistan = r'(UTC+4:30) Afghanistan'
    # outHillshade = os.path.join(TestUtilities.outputGDB, "outputHS")

    # # Testing
    # arcpy.AddMessage("Running tool (Sun Position and Hillshade)")
    # arcpy.SunPositionAnalysis_sunpos(TestUtilities.inputArea, TestUtilities.inputSurface, dtCompare, utcAfghanistan, outHillshade)

    # print("Comparing expected values with tool results from " + str(dtCompare)\
          # + " in " + str(utcAfghanistan))
    # compareResults = TestUtilities.compareResults

    # arcpy.CheckOutExtension("Spatial")
    # diff = Minus(Raster(outHillshade),Raster(compareResults))
    # diff.save(os.path.join(TestUtilities. scratchGDB, "diff"))
    # arcpy.CalculateStatistics_management(diff)
    # rasMinimum = float(arcpy.GetRasterProperties_management(diff,"MINIMUM").getOutput(0))
    # rasMaximum = float(arcpy.GetRasterProperties_management(diff,"MAXIMUM").getOutput(0))
    # rasMean = float(arcpy.GetRasterProperties_management(diff,"MEAN").getOutput(0))
    # rasSTD = float(arcpy.GetRasterProperties_management(diff,"STD").getOutput(0))
    # rasUnique = int(arcpy.GetRasterProperties_management(diff,"UNIQUEVALUECOUNT").getOutput(0))

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


# except arcpy.ExecuteError:
    # # Get the arcpy error messages
    # msgs = arcpy.GetMessages()
    # arcpy.AddError(msgs)
    # print(msgs)

    # # return a system error code
    # sys.exit(-1)

# except ValueDifferenceError as e:
    # print(e.message)
    # sys.exit(-1)

except:
    # Get the traceback object
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]

    # Concatenate information together concerning the error into a message string
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n"\
        + str(sys.exc_info()[1])
    msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

    # Return python error messages for use in script tool or Python Window
    arcpy.AddError(pymsg)
    arcpy.AddError(msgs)

    # Print Python error messages for use in Python / Python Window
    print(pymsg + "\n")
    print(msgs)

    # return a system error code
    sys.exit(-1)

# finally:
    # arcpy.CheckInExtension("Spatial")
