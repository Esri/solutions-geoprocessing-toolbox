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
# TestFastVisibilityByParameters_MulitpleInput.py
# Description: Test Publishable Tasks Toolbox > Fast Visibility By Parameters with multiple input points
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
    
    inputPoint = os.path.join(TestUtilities.inputGDB, "FV_InputPoint")
    OFFSETA = 2.0
    OFFSETB = 0.0
    RADIUS1 = 0.0
    RADIUS2 = 2000.0
    AZIMUTH1 = 0.0
    AZIMUTH2 = 360.0
    VERT1 = 90.0
    VERT2 = -90.0
    inputElevationURL = TestUtilities.inputElevationURL
    psOutput = os.path.join(TestUtilities.outputGDB, "FVBParam_m_vshed")
    
    #Testing Path Slope
    arcpy.AddMessage("Starting Test: Fast Visibility By Parameters _ Multiple Points")
    arcpy.FastVisibilityByParameters_pubtask(inputPoint,OFFSETA,OFFSETB,RADIUS1,RADIUS2,AZIMUTH1,AZIMUTH2,VERT1,VERT2, inputElevationURL, psOutput)
    
    #Verify Results
    outputFeatureCount = int(arcpy.GetCount_management(psOutput).getOutput(0)) 
    print "Output Viewshed: " + str(psOutput)
    print "Output Observer Count: " +  str(outputFeatureCount)
            
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