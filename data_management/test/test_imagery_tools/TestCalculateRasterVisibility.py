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
# Name: TestCalculateRasterVisibility.py
# Requirements: ArcGIS Desktop Standard
#------------------------------------------------------------------------------

import arcpy
import os
import sys
import traceback

import TestUtilities

def RunTest():
    try:
        arcpy.AddMessage("Starting Test: Calculate Raster Visibility")
   
        inputMosaicDataset =  os.path.join(TestUtilities.inputGDB, "Imagery_Test")
        toolbox = TestUtilities.toolbox
        
        arcpy.env.overwriteOutput = True
      
        arcpy.ImportToolbox(toolbox, "DefenseImagery")
    
        inputFeatureCount = int(arcpy.GetCount_management(inputMosaicDataset).getOutput(0)) 
        print "Input FeatureClass: " + str(inputMosaicDataset)
        print "Input Feature Count: " +  str(inputFeatureCount)
            
        if (inputFeatureCount < 1) :
            print "Invalid Input Feature Count: " +  str(inputFeatureCount)
                       
      
           
        ########################################################
        # Execute the Model under test:   
        arcpy.CalculateRasterVisibility_DefenseImagery(inputMosaicDataset, 10)
        ########################################################
       
        
        # Verify the results  
                
        min = arcpy.da.SearchCursor(inputMosaicDataset, ("MinPS"))
        for row in min:
            if( row[0] < 0) :
                raise Exception("Test Failed")
            
        max = arcpy.da.SearchCursor(inputMosaicDataset, ("MaxPS"))
        
        for row in max:
            if( row[0] < 0) :
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