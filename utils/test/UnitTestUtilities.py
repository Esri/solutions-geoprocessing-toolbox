#------------------------------------------------------------------------------
# Copyright 2015 Esri
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

import arcpy
import os
import sys
import platform
import logging
import TestUtilities

def initializeLogger(name):
    # get and return named logger
    logFile = os.path.join(TestUtilities.logPath, 'test.log')
    logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', filename=logFile, level=logging.DEBUG)
    logger = logging.getLogger(name)
    return logger
    
def setUpLogFileHeader(log):
    log.info("------------ New Test ------------------")
    log.info("Platform: {0}".format(platform.platform()))
    log.info("Python Version {0}".format(sys.version))
    d = arcpy.GetInstallInfo()
    log.info("{0} Version {1}, installed on {2}.".format(d['ProductName'], d['Version'], d['InstallDate']))
    log.info("----------------------------------------")
    
def checkArcPy():
    print("Testing ArcPy")
    arcpy.AddMessage("ArcPy works")
    
def createScratch(scratchPath):
    try:
        print("Creating scratch geodatabase...")
        arcpy.CreateFileGDB_management(scratchPath, "scratch.gdb")
        print("Created scratch gdb.")
    except:
        print("scratch.gdb already exists")
    return

def deleteScratch(scratchPath):
    try:
        arcpy.Delete_management(scratchPath)
        print("Deleted scratch gdb.")
    except:
        print("scratch.gdb delete failed")     
    return
  
def checkFilePaths(paths):   
    for path2check in paths:
        if os.path.exists(path2check):
            print("Valid Path: " + path2check)
        else:
            print("ERROR: Necessary Path not found: " + path2check)
            raise Exception('Bad Path')

def checkGeoObjects(objects):       
    for object2Check in objects:
        desc = arcpy.Describe(object2Check)
        if desc == None:
            print("--> Invalid Object: " + str(object2Check))
            arcpy.AddError("Bad Input")
            raise Exception('Bad Input')
        else:
            print("Valid Object: " + desc.Name)
            
def handleArcPyError():
    # Get the arcpy error messages
    msgs = arcpy.GetMessages()
    arcpy.AddError(msgs)
    print(msgs)

    # return a system error code
    sys.exit(-1)
   
def handleGeneralError():
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