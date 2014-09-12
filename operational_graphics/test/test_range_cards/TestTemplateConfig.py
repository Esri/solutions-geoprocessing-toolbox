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
# TestTemplateConfig.py
# Description: Common objects/methods used by test scripts
# Requirements: ArcGIS Desktop Standard
# -----------------------------------------------------------------------------

import arcpy
import os
import sys
import traceback

import TestUtilities

try:
    print("Testing ArcPy")
    arcpy.AddMessage("ArcPy works")
    
    if not arcpy.Exists(TestUtilities.scratchGDB):
        TestUtilities.createScratch()
    
    # WORKAROUND: delete scratch db (having problems with scratch read-only "scheme lock" errors
    # print "Deleting Scratch Workspace (Workaround)"    
    # TestUtilities.deleteScratch()
      
    print("Testing Necessary Paths"                )
    
    print("Running from: " + str(TestUtilities.currentPath))
           
    paths2Check = []
    paths2Check.extend([TestUtilities.geodatabasePath, TestUtilities.scratchPath, \
                        TestUtilities.toolboxesPath])
    
    for path2check in paths2Check :
        if os.path.exists(path2check) :
            print("Valid Path: " + path2check)
        else :     
            print("ERROR: Necessary Path not found: " + path2check )
            raise Exception('Bad Path')
    
    # WORKAROUND
    # print "Creating New Scratch Workspace (Workaround)"    
    # TestUtilities.createScratch()

    print("Testing Necessary Geo Objects")
    
    objects2Check = []
    objects2Check.extend([TestUtilities.toolbox, TestUtilities.inputGDB, TestUtilities.outputGDB, \
                         TestUtilities.defaultGDB]) 
    for object2Check in objects2Check :
        desc = arcpy.Describe(object2Check)
        if desc == None :
            print("--> Invalid Object: " + str(object2Check)    )
            arcpy.AddError("Bad Input")
            raise Exception('Bad Input')
        else :
            print("Valid Object: " + desc.Name)
            
    print("Test Successful")
    
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