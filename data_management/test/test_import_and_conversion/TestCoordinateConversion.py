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
# Name: TestCoordinateConversion.py
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
        arcpy.AddMessage("Starting Test: CoordinateConversion")
        
        # WORKAROUND
        print("Creating New Scratch Workspace (Workaround)")
        TestUtilities.createScratch()
            
        inputTable =  os.path.join(TestUtilities.csvPath, "SigActs.csv")
        outputDbf =  os.path.join(TestUtilities.scratchPath, "test_coordinate_cc.dbf")
        toolbox = TestUtilities.toolbox        
        
        # Set environment settings
        print("Running from: " + str(TestUtilities.currentPath))
        print("Geodatabase path: " + str(TestUtilities.geodatabasePath))
        
        arcpy.env.overwriteOutput = True
        arcpy.env.scratchWorkspace = TestUtilities.scratchGDB
        arcpy.ImportToolbox(toolbox, "InC")
    
        inputFeatureCount = int(arcpy.GetCount_management(inputTable).getOutput(0)) 
        print("Input FeatureClass: " + str(inputTable))
        print("Input Feature Count: " +  str(inputFeatureCount))
            
        if (inputFeatureCount < 1) :
            print("Invalid Input Feature Count: " +  str(inputFeatureCount))
                       
        coordinateConversionFrom = 'MGRS'
        coordinateFieldX = 'Location'
        coordinateFieldY = None
        
        ########################################################3       
        arcpy.ConvertCoordinates_InC(inputTable, coordinateConversionFrom, coordinateFieldX, coordinateFieldY, outputDbf)
        ########################################################3
    
        # Verify the results    
        outputFeatureCount = int(arcpy.GetCount_management(outputDbf).getOutput(0)) 
        print("Output FeatureClass: " + str(outputDbf))
        print("Output Feature Count: " +  str(outputFeatureCount))
                    
        if (outputFeatureCount <>  inputFeatureCount) :
            print("Input / Output Feature Count don't match: " +  str(inputFeatureCount) + ":" + str(outputFeatureCount))
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

RunTest()