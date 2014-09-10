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
# TestDriveTime_Simple.py
# Description: Test Publishable Tasks Toolbox > Drive Time with no barriers
# Requirements: ArcGIS Desktop Standard with Network Analyst
# ----------------------------------------------------------------------------

import arcpy
import sys
import traceback
import TestUtilities
import os

class LicenseError(Exception):
    pass

try:
    if arcpy.CheckExtension("Network") == "Available":
        arcpy.CheckOutExtension("Network")
    else:
        raise LicenseError
    
    arcpy.ImportToolbox(TestUtilities.toolbox)
    arcpy.env.overwriteOutput = True
    
    inputDriveTimeStartPoint = os.path.join(TestUtilities.inputGDB, "DT_StartPoint")
    inputDriveTimeValue = "1 2 3 5"
    inputDriveTimeUnit = "Minutes"
    inputPointBarrier = "#"
    inputLineBarrier = "#"
    inputPolygonBarrier = "#"
    psOutput = os.path.join(TestUtilities.outputGDB, "DriveTime_Simple")
    
    #Testing Path Slope
    arcpy.AddMessage("Starting Test: Drive Time - Simple - single start point, no barriers")
    arcpy.DriveTime_pubtask(inputDriveTimeStartPoint,inputDriveTimeValue,inputDriveTimeUnit,inputPointBarrier,inputLineBarrier,inputPolygonBarrier,psOutput)
    
    #Verify Results
    outputFeatureCount = int(arcpy.GetCount_management(psOutput).getOutput(0)) 
    print("Output Drive Time: " + str(psOutput))
    print("Output Drive Time polygon count: " +  str(outputFeatureCount))
            
    if (outputFeatureCount < 1):
        print("Invalid Output poly count: " +  str(outputFeatureCount))
        raise Exception("Test Failed")  

    print("Test Passed")

except LicenseError:
    print("Network Analyst license is unavailable")

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
    
finally:
    if arcpy.CheckExtension("Spatial") == "Available":
        arcpy.CheckInExtension("Spatial")