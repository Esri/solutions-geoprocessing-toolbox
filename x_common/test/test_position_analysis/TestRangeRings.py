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
# Name: TestRangeRings.py
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
        arcpy.AddMessage("Starting Test: RangeRings")
        
        # WORKAROUND
        print "Creating New Scratch Workspace (Workaround)"    
        TestUtilities.createScratch()
            
        inputPointsFC =  os.path.join(TestUtilities.inputGDB, "sampleRangePoints")
        outputRangeRingsFC =  os.path.join(TestUtilities.outputGDB, "RangeRings")
        outputRangeRadialsFC =  os.path.join(TestUtilities.outputGDB, "RangeRadials") 
        toolbox = TestUtilities.toolbox
        
        # Check For Valid Input
        objects2Check = []
        objects2Check.extend([inputPointsFC, toolbox])
        for object2Check in objects2Check :
            desc = arcpy.Describe(object2Check)
            if desc == None :
                raise Exception("Bad Input")
            else :
                print "Valid Object: " + desc.Name 
        
        # Set environment settings
        print "Running from: " + str(TestUtilities.currentPath)
        print "Geodatabase path: " + str(TestUtilities.geodatabasePath)
        
        arcpy.env.overwriteOutput = True
        arcpy.env.scratchWorkspace = TestUtilities.scratchGDB
        arcpy.ImportToolbox(toolbox, "Position")
    
        inputFeatureCount = int(arcpy.GetCount_management(inputPointsFC).getOutput(0)) 
        print "Input FeatureClass: " + str(inputPointsFC)
        print "Input Feature Count: " +  str(inputFeatureCount)
            
        if (inputFeatureCount < 1) :
            print "Invalid Input Feature Count: " +  str(inputFeatureCount)
                       
        numberOfRings = 5
        ringInterval = 1000.0
        distanceUnits = "METERS"
        numberOfRadials = 8
           
        ########################################################3
        # Execute the Model under test:   
        arcpy.RangeRings_Position(inputPointsFC, numberOfRings, ringInterval, distanceUnits, numberOfRadials, outputRangeRingsFC, outputRangeRadialsFC)
        ########################################################3
    
        # Verify the results    
        outputFeatureCountRings = int(arcpy.GetCount_management(outputRangeRingsFC).getOutput(0)) 
        print "Output FeatureClass: " + str(outputRangeRingsFC)
        print "Output Feature Count: " +  str(outputFeatureCountRings)
    
        outputFeatureCountRadials = int(arcpy.GetCount_management(outputRangeRadialsFC).getOutput(0))
        print "Output FeatureClass: " + str(outputRangeRadialsFC)
        print "Output Feature Count: " +  str(outputFeatureCountRadials)
                
        if (outputFeatureCountRings < 1) or (outputFeatureCountRadials < 1) :
            print "Invalid Output Feature Count: " +  str(outputFeatureCountRings) + ":" + str(outputFeatureCountRadials)
            raise Exception("Test Failed")            
            
        # WORKAROUND: delete scratch db
        print "Deleting Scratch Workspace (Workaround)"    
        TestUtilities.deleteScratch()        
        
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