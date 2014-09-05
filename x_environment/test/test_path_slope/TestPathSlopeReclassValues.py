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
# TestPathSlopeReclassValues.py
# Description: Test Path Slope Toolbox
# Requirements: ArcGIS Desktop Standard with Spatial Analyst Extension
# ----------------------------------------------------------------------------

import arcpy
import sys
import traceback
import TestUtilities
import os

class LicenseError(Exception):
    pass

try:
    if arcpy.CheckExtension("Spatial") == "Available":
        arcpy.CheckOutExtension("Spatial")
    
    else:
        raise LicenseError
    
    arcpy.ImportToolbox(TestUtilities.toolbox)
    arcpy.env.overwriteOutput = True
    arcpy.env.scratchWorkspace = TestUtilities.scratchGDB
    
    inputPolyArea = os.path.join(TestUtilities.inputGDB, "samplePolygonArea")
    inputRoads = os.path.join(TestUtilities.defaultGDB, "roads")
    inputSurface = os.path.join(TestUtilities.defaultGDB, "Jbad_SRTM_USGS_EROS")
    psOutputRV = os.path.join(TestUtilities.outputGDB, "PathSlopeOutputRV")
    classValue = '0 3 1;3 10 2;10 15 3;15 20 4;20 30 5;30 45 6;45 60 7;60 85 8;85 10000000000000 9;NODATA 0'
    
    #Testing Path Slope by Reclass Values
    arcpy.AddMessage("Starting Test: Path Slope by Reclass Values")
    TestUtilities.createScratch()
    arcpy.PathSlopeByRanges_path(inputPolyArea, inputRoads, inputSurface, 'DEGREE', classValue, psOutputRV)

    
    #Test for Feature Outpu
    outputFeatureCount = int(arcpy.GetCount_management(psOutputRV).getOutput(0)) 
    print "Output FeatureClass: " + str(psOutputRV)
    print "Output Feature Count: " +  str(outputFeatureCount)
            
    if (outputFeatureCount < 1):
        print "Invalid Output Feature Count: " +  str(outputFeatureCount)
        raise Exception("Test Failed")  

    print("Test Passed")

except LicenseError:
    print "Spatial Analyst license is unavailable"  

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