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
# Name: TestCreateRangeFanIndexFeatures.py
# Description: Automatic Test of Range Rings Model
# Requirements: ArcGIS Desktop Standard
#------------------------------------------------------------------------------

import arcpy
import os
import sys
import traceback

import TestUtilities

def RunTest():
    try:
        arcpy.AddMessage("Starting Test: TestCreateRangeFanIndexFeatures")
        
        # WORKAROUND
        print("Creating New Scratch Workspace (Workaround)")
        TestUtilities.createScratch()
            
        inputPolygonFC =  os.path.join(TestUtilities.inputGDB, "RangeFans")
        outputExtentBoxes =  os.path.join(TestUtilities.outputGDB, "OutputExtentBoxes")
        outputRangeVertices =  os.path.join(TestUtilities.outputGDB, "RangeVertices")
        toolbox = TestUtilities.toolbox
                
        # Set environment settings
        print("Running from: " + str(TestUtilities.currentPath))
        print("Geodatabase path: " + str(TestUtilities.geodatabasePath))
        
        arcpy.env.overwriteOutput = True
        arcpy.env.scratchWorkspace = TestUtilities.scratchGDB
        arcpy.ImportToolbox(toolbox, "Range")
    
        inputFeatureCount = int(arcpy.GetCount_management(inputPolygonFC).getOutput(0)) 
        print("Input FeatureClass: " + str(inputPolygonFC))
        print("Input Feature Count: " +  str(inputFeatureCount))
            
        if (inputPolygonFC < 1) :
            print("Invalid Input Feature Count: " +  str(inputPolygonFC)                       )
                   
        ########################################################3
        # Execute the Model under test:   
        arcpy.CreateRangeFanIndexFeatures_Range(inputPolygonFC, outputExtentBoxes, outputRangeVertices)
        ########################################################3
    
        # Verify the results    
        outputFeatureCountExtent = int(arcpy.GetCount_management(outputExtentBoxes).getOutput(0)) 
        print("Output FeatureClass: " + str(outputExtentBoxes))
        print("Output Feature Count: " +  str(outputFeatureCountExtent))
    
        outputFeatureCountPoints = int(arcpy.GetCount_management(outputRangeVertices).getOutput(0))
        print("Output FeatureClass: " + str(outputRangeVertices))
        print("Output Feature Count: " +  str(outputFeatureCountPoints))
                
        if (outputFeatureCountExtent < 1) or (outputFeatureCountPoints < 1) :
            print("Invalid Output Feature Count: " +  str(outputFeatureCountExtent) + ":" + str(outputFeatureCountPoints))
            raise Exception("Test Failed")                                  
            
        # WORKAROUND: delete scratch db
        print "Deleting Scratch Workspace (Workaround)"    
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

RunTest()