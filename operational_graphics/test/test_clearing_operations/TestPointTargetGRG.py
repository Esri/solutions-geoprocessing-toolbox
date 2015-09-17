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
# Name: TestPointTargetGRG.py
# Description: Test Point Target GRG tool in the Clearing Operations Tools_10.3.tbx.
# Requirements: ArcGIS Desktop Standard
#------------------------------------------------------------------------------

import arcpy
import os
import sys
import traceback
import TestUtilities

try:

    arcpy.AddMessage("Starting Test: TestPointTargetGRG.")

    arcpy.ImportToolbox(TestUtilities.toolbox, "ClearingOperations")
    arcpy.env.overwriteOutput = True

    # Inputs
    inputTargetPoint = os.path.join(TestUtilities.inputGDB, "CenterPoint")
    inputHorizontalCells = 10
    inputVerticalCells = 10
    inputCellWidth = 100
    inputCellHeight = 100
    inputCellUnits = "Meters"
    inputLabelStartPosition = "Upper-Left"
    inputLabelStyle = "Alpha-Numeric"
    outputFeatureClass = os.path.join(TestUtilities.scratchGDB, "PointTargetGRGOutput")

    arcpy.PointTargetGRG_ClearingOperations(inputTargetPoint, inputHorizontalCells, inputVerticalCells, inputCellWidth, inputCellHeight, inputCellUnits, "#", inputLabelStartPosition, inputLabelStyle, outputFeatureClass)

    # Verify the results
    outputCount = int(arcpy.GetCount_management(outputFeatureClass).getOutput(0))
    print("Output Feature count: " + str(outputCount))

    if(outputCount != 100):
        print("Invalid output feature count.")
        raise Exception("Test Failed")
    else:
        print("Test Passed")

except arcpy.ExecuteError:
    # Get the tool error messages
    msgs = arcpy.GetMessages()
    arcpy.AddError(msgs)

    # return a system error code
    sys.exit(-1)

except Exception as e:
    # Get the traceback object
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]

    # Concatenate information together concerning the error into a message string
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

    # Return python error messages for use in script tool or Python Window
    arcpy.AddError(pymsg)
    arcpy.AddError(msgs)

    # return a system error code
    sys.exit(-1)
