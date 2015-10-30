# coding: utf-8
'''
------------------------------------------------------------------------------
 Copyright 2015 Esri
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
------------------------------------------------------------------------------
==================================================
UnitTestUtiliites.py
--------------------------------------------------
requirments:
* ArcGIS Desktop 10.X+ or ArcGIS Pro 1.X+
* Python 2.7 or Python 3.4
author: ArcGIS Solutions
company: Esri
==================================================
description:
Basic methods used in unit tests

==================================================
history:
10/06/2015 - JH - original coding
10/23/2015 - MF - mods for tests
==================================================
'''

import arcpy
import os
import sys
import platform
import logging
import TestUtilities
import datetime

def getLoggerName():
    ''' get unique log file name '''
    if TestUtilities.DEBUG == True:
        print("UnitTestUtilities - getLoggerName")
    seq = 0
    name = nameFromDate(seq)
    #add +=1 to seq until name doesn't exist as a path
    while os.path.exists(os.path.join(TestUtilities.logPath, name)):
        seq += 1
        name = nameFromDate(seq)
    #logFilePath = os.path.join(TestUtilities.logPath, name)
    return name

def nameFromDate(seq):
    ''' use NOW to make a file name'''
    return 'SGT_' + str(datetime.datetime.now().strftime("%Y-%B-%d_%H-%M-%S")) + '_seq' + str(seq) + '.log'

def initializeLogger(name):
    ''' get and return named logger '''
    if TestUtilities.DEBUG == True:
        print("UnitTestUtilities - initializeLogger")
    if not os.path.exists(TestUtilities.logPath):
        os.makedirs(os.path.dirname(TestUtilities.logPath))

    if name == None or name == "":
        #logFile = os.path.join(TestUtilities.logPath, 'test.log')
        logFile = getLoggerName()
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
    ''' Add a header to log file when initalized '''
    if TestUtilities.DEBUG == True:
        print("UnitTestUtilities - setUpLogFileHeader")
    log.info("------------ Begin Test ------------------")
    log.info("Platform: {0}".format(platform.platform()))
    log.info("Python Version {0}".format(sys.version))
    d = arcpy.GetInstallInfo()
    log.info("{0} Version {1}, installed on {2}.".format(d['ProductName'], d['Version'], d['InstallDate']))
    log.info("----------------------------------------")

def checkArcPy():
    ''' sanity check that ArcPy is working '''
    if TestUtilities.DEBUG == True: print("UnitTestUtilities - checkArcPy")
    print("Testing ArcPy")
    arcpy.AddMessage("ArcPy works")

def checkExists(p):
    ''' Python check for existance '''
    if TestUtilities.DEBUG == True: print("UnitTestUtilities - checkExists")
    return os.path.exists(p)

def createScratch(scratchPath):
    ''' create scratch geodatabase '''
    if TestUtilities.DEBUG == True: print("UnitTestUtilities - createScratch")
    scratchName = 'scratch.gdb'
    scratchGDB = os.path.join(scratchPath, scratchName)
    if checkExists(scratchGDB):
        print("Scratch already exists")
        return scratchGDB
    try:
        if TestUtilities.DEBUG == True: print("Creating scratch geodatabase...")
        arcpy.CreateFileGDB_management(scratchPath, scratchName)
        if TestUtilities.DEBUG == True: print("Created scratch gdb.")
    except:
        print("Problem creating scratch.gdb")
    return scratchGDB

def deleteScratch(scratchPath):
    ''' delete scratch geodatabase '''
    if TestUtilities.DEBUG == True: print("UnitTestUtilities - deleteScratch")
    try:
        arcpy.Delete_management(scratchPath)
        print("Deleted scratch gdb.")
    except:
        print("scratch.gdb delete failed")
    return

def checkFilePaths(paths):
    ''' check file/folder paths exist '''
    if TestUtilities.DEBUG == True: print("UnitTestUtilities - checkFilePaths")
    for path2check in paths:
        if os.path.exists(path2check):
            print("Valid Path: " + path2check)
        else:
            raise Exception('Bad Path: ' + str(path2check))

def checkGeoObjects(objects):
    ''' check geospatial stuff exists '''
    if TestUtilities.DEBUG == True: print("UnitTestUtilities - checkGeoObjects")
    for object2Check in objects:
        #TODO: Shouldn't we be using arcpy.Exists()?
        desc = arcpy.Describe(object2Check)
        if desc == None:
            print("--> Invalid Object: " + str(object2Check))
            arcpy.AddError("Bad Input")
            raise Exception('Bad Input')
        else:
            print("Valid Object: " + desc.Name)

def handleArcPyError(logger):
    ''' Basic GP error handling, errors printed to console and logger '''
    if TestUtilities.DEBUG == True: print("UnitTestUtilities - handleArcPyError")
    # Get the arcpy error messages
    msgs = arcpy.GetMessages()
    arcpy.AddError(msgs)
    print(msgs)
    logger.error(msgs)


def handleGeneralError(logger):
    ''' Basic error handler, errors printed to console and logger '''
    if TestUtilities.DEBUG == True: print("UnitTestUtilities - handleGeneralError")
    # Get the traceback object
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]

    # Concatenate information together concerning the error into a message string
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

    # Print Python error messages for use in Python / Python Window
    print(pymsg + "\n")
    logger.error(pymsg)
    print(msgs)
    logger.error(msgs)
