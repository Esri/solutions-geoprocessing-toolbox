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
# TestRemoveDuplicateData.py
# Description: Automatic Test of GP script/toolbox
# Requirements: ArcGIS Desktop Standard
# -----------------------------------------------------------------------------

import arcpy
import os
import sys
import traceback

import TestUtilities

def RunTest():
    try:
        arcpy.AddMessage("Starting Test: TestRemoveDuplicateData")
                    
        # Prior to this, run TestTemplateConfig.py to verify the expected configuration exists

        inputTrackPointsFC = os.path.join(TestUtilities.inputGDB, "GPSData")

        outputPointsFC =  os.path.join(TestUtilities.outputGDB, "GPSData_Duplicates")
                
        try :
            # Delete Output if it exists   
            desc = arcpy.Describe(outputPointsFC)
            if desc != None :
                print("Deleting: " + str(outputPointsFC))
                arcpy.Delete_management(outputPointsFC)
        except:    
            print("Delete failed for: " + str(outputPointsFC))
       
        try :
            # Copy Input (with Duplicates) to Output
            print("Copying " + str(inputTrackPointsFC) + " --> " + str(outputPointsFC))
            arcpy.Copy_management(inputTrackPointsFC, outputPointsFC)
        except:    
            print("Copy failed for: " + str(inputTrackPointsFC) + ":" + str(outputPointsFC))
                                        
        toolbox = TestUtilities.toolbox
               
        # Set environment settings
        print("Running from: " + str(TestUtilities.currentPath))
        print("Geodatabase path: " + str(TestUtilities.geodatabasePath))
        
        arcpy.env.overwriteOutput = True
        arcpy.ImportToolbox(toolbox, "pdc")
               
        ########################################################3
        # Execute the Model under test:   
        arcpy.RemoveDuplicateGPSData_pdc(outputPointsFC)
        ########################################################3
        
        # Verify the results (Original Track Points)   
        inputFeatureCount = int(arcpy.GetCount_management(inputTrackPointsFC).getOutput(0)) 
        print("Input FeatureClass: " + str(inputTrackPointsFC))
        print("Input Feature Count: " +  str(inputFeatureCount))
                    
        if (inputFeatureCount < 1) :
            print("Invalid Output Feature Count: " +  str(inputFeatureCount))
            raise Exception("Test Failed")       
        
        # There is only 1 duplicate record so new count will be inputFeatureCount - 1

        # Verify the results (New Track Point)   
        outputFeatureCount = int(arcpy.GetCount_management(outputPointsFC).getOutput(0)) 
        print("Output FeatureClass: " + str(outputPointsFC))
        print("Output Feature Count: " +  str(outputFeatureCount))
                    
        if (outputFeatureCount >= inputFeatureCount) :
            print("Output Feature Count >= Input Feature Count: " + str(outputFeatureCount))
            raise Exception("Test Failed")                                              
        
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

RunTest()