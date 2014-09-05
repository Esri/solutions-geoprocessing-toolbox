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
# TestAddTravelTimeToRoads.py
# Description: Test Add Travel Time To Roads Tool
# Requirements: ArcGIS Desktop Advanced
# ----------------------------------------------------------------------------

import arcpy
import sys
import traceback
import TestUtilities
import os

class LicenseError(Exception):
    pass

try:
        
    arcpy.ImportToolbox(TestUtilities.toolbox)
    arcpy.env.overwriteOutput = True
    
    #Set tool param variables
    # mfunk 7/30/2013: this tool must run AFTER TestSplitLinesAtIntersections.py
    inputRoadFeatures = os.path.join(TestUtilities.outputGDB,"RoadFeat")
    inputTravelVelocityTable = os.path.join(TestUtilities.inputGDB,"RoadTravelVelocity")
    
    #Testing 
    arcpy.AddMessage("Starting Test: Add Travel Time To Roads")
    arcpy.AddTravelTimeToRoads_netprep(inputRoadFeatures,inputTravelVelocityTable)
    
    #Verify Results
    
    #check output fields are there
    fieldNames = []
    for field in arcpy.ListFields(inputRoadFeatures): fieldNames.append(field.name)
    if not ("FT_MINUTES" in fieldNames) or not ("TF_MINUTES" in fieldNames):
        raise Exception("Output field (TF_MINUTES or FT_MINUTES) are not present in output")
        
    print("Test Passed")
    

except arcpy.ExecuteError: 
    # Get the arcpy error messages 
    msgs = arcpy.GetMessages() 
    arcpy.AddError(msgs) 
    print msgs
    
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
    print pymsg + "\n"
    print msgs
    
    # return a system error code  
    sys.exit(-1)
    
finally:
    if arcpy.CheckExtension("Spatial") == "Available":
        arcpy.CheckInExtension("Spatial")