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
# Name: TestModelHighestPoint.py
# Description: Automatic Test of Highest Point Model
# Requirements: ArcGIS Desktop Standard with Spatial Analyst Extension
#------------------------------------------------------------------------------

import arcpy
import os
import sys
import traceback

import TestUtilities

def RunTest():
    try:
        arcpy.AddMessage("Starting Test: HighestPoint")
        
        if arcpy.CheckExtension("Spatial") == "Available":
            arcpy.CheckOutExtension("Spatial")
        else:
            # Raise a custom exception
            raise Exception("LicenseError")        
        
        # WORKAROUND
        print("Creating New Scratch Workspace (Workaround)")
        TestUtilities.createScratch()
            
        # Verify the expected configuration exists
        inputPolygonFC =  os.path.join(TestUtilities.inputGDB, "samplePolygonArea")
        inputSurface =  os.path.join(TestUtilities.inputGDB, "Jbad_SRTM_USGS_EROS")
        outputPointsFC =  os.path.join(TestUtilities.outputGDB, "HighestPoint")
        toolbox = TestUtilities.toolbox
        
        # Check For Valid Input
        objects2Check = []
        objects2Check.extend([inputPolygonFC, inputSurface, toolbox])
        for object2Check in objects2Check :
            desc = arcpy.Describe(object2Check)
            if desc == None :
                raise Exception("Bad Input")
            else :
                print("Valid Object: " + desc.Name )
        
        # Set environment settings
        print("Running from: " + str(TestUtilities.currentPath))
        print("Geodatabase path: " + str(TestUtilities.geodatabasePath))
        
        arcpy.env.overwriteOutput = True
        arcpy.env.scratchWorkspace = TestUtilities.scratchGDB
        arcpy.ImportToolbox(toolbox, "VandR")
    
        inputFeatureCount = int(arcpy.GetCount_management(inputPolygonFC).getOutput(0)) 
        print("Input FeatureClass: " + str(inputPolygonFC))
        print("Input Feature Count: " +  str(inputFeatureCount))
            
        if (inputFeatureCount < 1) :
            print("Invalid Input Feature Count: " +  str(inputFeatureCount))
           
        ########################################################3
        # Execute the Model under test:   
        arcpy.HighestPoints_VandR(inputPolygonFC, inputSurface, outputPointsFC)
        ########################################################3
    
        # Verify the results    
        outputFeatureCount = int(arcpy.GetCount_management(outputPointsFC).getOutput(0)) 
        print("Output FeatureClass: " + str(outputPointsFC))
        print("Output Feature Count: " +  str(outputFeatureCount))
                
        if (outputPointsFC < 1) :
            print("Invalid Output Feature Count: " +  str(outputFeatureCount))
            raise Exception("Test Failed")
            
        # WORKAROUND: delete scratch db
        print("Deleting Scratch Workspace (Workaround)")
        TestUtilities.deleteScratch()        
        
        print("Test Successful")
                
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
        
    finally:
        # Check in the 3D Analyst extension
        arcpy.CheckInExtension("Spatial")        
        

RunTest()