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
    
def createScratch():
    try:
        print("Creating scratch geodatabase...")
        arcpy.CreateFileGDB_management(TestUtilities.scratchGDB, "scratch")
        print("Created scratch gdb.")
    except:
        print("scratch.gdb already exists")
    return

def deleteScratch():
    try:
        arcpy.Delete_management(TestUtilities.scratchGDB)
        print("Deleted scratch gdb.")
    except:
        print("scratch.gdb delete failed")     
    return
    
def checkFilePaths():
    paths2Check = []
    paths2Check.extend([TestUtilities.geodatabasePath, TestUtilities.scratchPath, TestUtilities.toolboxesPath])

    for path2check in paths2Check:
        if os.path.exists(path2check):
            print("Valid Path: " + path2check)
        else:
            print("ERROR: Necessary Path not found: " + path2check)
            raise Exception('Bad Path')
            
def checkGeoObjects():
    objects2Check = []
    objects2Check.extend([TestUtilities.toolbox, TestUtilities.inputGDB, TestUtilities.outputGDB, TestUtilities.defaultGDB, TestUtilities.inputArea, TestUtilities.inputSurface, TestUtilities.compareResults]) 
        
    for object2Check in objects2Check:
        desc = arcpy.Describe(object2Check)
        if desc == None:
            print("--> Invalid Object: " + str(object2Check))
            arcpy.AddError("Bad Input")
            raise Exception('Bad Input')
        else:
            print("Valid Object: " + desc.Name)
            