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
# TestDistiguishTracks.py
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
        arcpy.AddMessage("Starting Test: TestDistiguishTracks")
                    
        # Prior to this, run TestTemplateConfig.py to verify the expected configuration exists

        inputTrackPointsFC = os.path.join(TestUtilities.inputGDB, "GPSData")

        outputPointsFC =  os.path.join(TestUtilities.outputGDB, "SeparatedGPSData")
        outputLinesFC =  os.path.join(TestUtilities.outputGDB, "TrackLines")        
                                        
        toolbox = TestUtilities.toolbox
               
        # Set environment settings
        print "Running from: " + str(TestUtilities.currentPath)
        print "Geodatabase path: " + str(TestUtilities.geodatabasePath)
        
        arcpy.env.overwriteOutput = True
        arcpy.ImportToolbox(toolbox, "PDCAlias")
               
        dateTimeField = "Date_Time"
        maximumTimeDelta = 100.0
        
        ########################################################
        # Execute the Model under test:   
        # Format: DistinguishTracks_MyAlias(GPS_Data, DateTime_Field, Maximum_Time_Difference, SeparatedGPSData, TrackLines)
        arcpy.DistinguishTracks_PDCAlias(inputTrackPointsFC, dateTimeField, maximumTimeDelta, outputPointsFC, outputLinesFC)
        ########################################################
        
        # Verify the results (Track Points)   
        outputFeatureCount = int(arcpy.GetCount_management(outputPointsFC).getOutput(0)) 
        print "Output FeatureClass (Points): " + str(outputPointsFC)
        print "Output Feature Count: " +  str(outputFeatureCount)
                    
        if (outputFeatureCount < 1) :
            print "Invalid Output Feature Count: " +  str(outputFeatureCount)
            raise Exception("Test Failed")       
        
        # Verify the results (Track Lines)       
        outputFeatureCount = int(arcpy.GetCount_management(outputLinesFC).getOutput(0)) 
        print "Output FeatureClass (Lines): " + str(outputLinesFC)
        print "Output Feature Count: " +  str(outputFeatureCount)
                    
        if (outputFeatureCount < 1) :
            print "Invalid Output Feature Count: " +  str(outputFeatureCount)
            raise Exception("Test Failed")                                              
        
        print "Test Successful"        
                
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