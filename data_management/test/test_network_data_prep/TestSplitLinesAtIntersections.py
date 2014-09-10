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
# TestSplitLinesAtIntersections.py
# Description: Test Split Lines At Intersections Tool
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
    
    #check product for Advanced (ArcInfo)
    productLevel = arcpy.CheckProduct("ArcInfo")
    print("CheckProduct(ArcInfo): " + productLevel)

    if (productLevel == "Available"):
        import arcinfo
    elif (productLevel != "Available") and (productLevel != "AlreadyInitialized"):
        raise Exception("Advanced license is required")

    
    #Set tool param variables
    inputUTDSRoadFeatures = os.path.join(TestUtilities.inputGDB,"UTDSRoads")
    outputSplitRoadFeatures = os.path.join(TestUtilities.outputGDB,"RoadFeat")
    
    #Testing Build Elevation Mosaics - DTED input
    arcpy.AddMessage("Starting Test: Split Lines At Intersection (this test may take a while)")
    arcpy.SplitLinesAtIntersections_netprep(inputUTDSRoadFeatures,outputSplitRoadFeatures)
    
    #Verify Results
    countBeforeRoadFeatures = int(arcpy.GetCount_management(inputUTDSRoadFeatures).getOutput(0))
    print("Before road feature count: " + str(countBeforeRoadFeatures))
    
    countAfterRoadFeatures = int(arcpy.GetCount_management(outputSplitRoadFeatures).getOutput(0))
    print("After road feature count: " + str(countAfterRoadFeatures))
    
    if (countBeforeRoadFeatures >= countAfterRoadFeatures):
        print("Feature count is not greater")
        raise Exception("Test Failed")
    
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
    
finally:
    if arcpy.CheckExtension("Spatial") == "Available":
        arcpy.CheckInExtension("Spatial")