# coding: utf-8
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
    print("UnitTestUtilities - initializeLogger")
    if not os.path.exists(TestUtilities.logPath):
        os.makedirs(os.path.dirname(TestUtilities.logPath))

    if name == None or name == "":
        logFile = os.path.join(TestUtilities.logPath, 'test.log')
    else:
        logFile = os.path.join(TestUtilities.logPath, name)

    if not os.path.exists(logFile):
        fd = open(logFile, 'w')
        fd.close()

    #TODO: Check if log file path exists, if not, create it
    logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', filename=logFile, level=logging.DEBUG)
    logger = logging.getLogger(name)
    return logger

def setUpLogFileHeader(log):
    print("UnitTestUtilities - setUpLogFileHeader")
    log.info("------------ New Test ------------------")
    log.info("Platform: {0}".format(platform.platform()))
    log.info("Python Version {0}".format(sys.version))
    d = arcpy.GetInstallInfo()
    log.info("{0} Version {1}, installed on {2}.".format(d['ProductName'], d['Version'], d['InstallDate']))
    log.info("----------------------------------------")

def checkArcPy():
    print("UnitTestUtilities - checkArcPy")
    print("Testing ArcPy")
    arcpy.AddMessage("ArcPy works")

def checkExists(p):
    print("UnitTestUtilities - checkExists")
    return os.path.exists(p)

def createScratch(scratchPath):
    print("UnitTestUtilities - createScratch")
    if checkExists(scratchPath):
        print("Scratch already exists")
        return scratchPath
    try:
        print("Creating scratch geodatabase...")
        path = os.path.join(scratchPath,"scratch.gdb")
        arcpy.CreateFileGDB_management(os.path.dirname(path), os.path.basename(path))
        print("Created scratch gdb.")
    except:
        print("Problem creating scratch.gdb")
    return path

def deleteScratch(scratchPath):
    print("UnitTestUtilities - deleteScratch")
    try:
        arcpy.Delete_management(scratchPath)
        print("Deleted scratch gdb.")
    except:
        print("scratch.gdb delete failed")
    return

def checkFilePaths(paths):
    print("UnitTestUtilities - checkFilePaths")
    for path2check in paths:
        if os.path.exists(path2check):
            print("Valid Path: " + path2check)
        else:
            raise Exception('Bad Path: ' + str(path2check))

def checkGeoObjects(objects):
    print("UnitTestUtilities - checkGeoObjects")
    for object2Check in objects:
        desc = arcpy.Describe(object2Check)
        if desc == None:
            print("--> Invalid Object: " + str(object2Check))
            arcpy.AddError("Bad Input")
            raise Exception('Bad Input')
        else:
            print("Valid Object: " + desc.Name)

def handleArcPyError():
    print("UnitTestUtilities - handleArcPyError")
    # Get the arcpy error messages
    msgs = arcpy.GetMessages()
    arcpy.AddError(msgs)
    print(msgs)

    # return a system error code
    sys.exit(-1)

def handleGeneralError():
    print("UnitTestUtilities - handleGeneralError")
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
    