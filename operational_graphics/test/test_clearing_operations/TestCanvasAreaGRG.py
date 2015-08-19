#------------------------------------------------------------------------------
# Copyright 2013 Esri
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
# TestCanvasAreaGRG.py
# Description: Test Canvas Area GRG tool in the Clearing Operations Tools_10.3.tbx.
# Requirements: ArcGIS Desktop Standard
# ----------------------------------------------------------------------------

import arcpy
import sys
import traceback
import TestUtilities
import os

try:
    arcpy.AddMessage("Starting Test: TestCanvasAreaGRG.")
    
    arcpy.ImportToolbox(TestUtilities.toolbox, "ClearingOperations")
    arcpy.env.overwriteOutput = True
    inputCellWidth = 40
    inputCellHeight = 40
    inputCellUnits = "Meters"
    inputCanvasAreaPath = os.path.join(TestUtilities.inputGDB, "AO")
    inputLabelingStartPosition = "Lower-Left"
    inputLabelingStyle = "Alpha-Numeric"
    outputFeatureClass = os.path.join(TestUtilities.scratchGDB, "testOutput")

    #CanvasAreaGRG_ClearingOperations (Canvas_Area, Cell_Width, Cell_Height, Cell_Units, {Draw_Cell}, Labeling_Start_Position, Labeling_Style, Output_Name) 
    arcpy.CanvasAreaGRG_ClearingOperations(inputCanvasAreaPath, inputCellWidth, inputCellHeight, inputCellUnits, "#", inputLabelingStartPosition, inputLabelingStyle, outputFeatureClass)
    countOutputFeatures = int(arcpy.GetCount_management(outputFeatureClass).getOutput(0))
    print("Output Feature count: " + str(countOutputFeatures))
    if (countOutputFeatures != 294):
        print("Invalid output feature count.")
        raise Exception("Test Failed")
    else:
        print("Test Passed")


except arcpy.ExecuteError: 
    # Get the arcpy error messages 
    msgs = arcpy.GetMessages() 
    arcpy.AddError(msgs) 
    print(msgs)
    
    # return a system error code
    sys.exit(-1)

except:
    # Get the traceback object
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]

    # Concatenate information together concerning the error into a message string
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

    # Return python error messages for use in script tool or Python Window
    arcpy.AddError(pymsg)
    arcpy.AddError(msgs)

    # Print Python error messages for use in Python / Python Window
    print(pymsg + "\n")
    print(msgs)
    
    # return a system error code  
    sys.exit(-1)
