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
import traceback
import platform
import logging
import Configuration
import datetime

def getLoggerName():
    ''' get unique log file name '''
    if Configuration.DEBUG == True:
        print("UnitTestUtilities - getLoggerName")
    seq = 0
    name = nameFromDate(seq)
    #add +=1 to seq until name doesn't exist as a path
    while os.path.exists(os.path.join(Configuration.logPath, name)):
        seq += 1
        name = nameFromDate(seq)
    #logFilePath = os.path.join(Configuration.logPath, name)
    return name

def getCurrentDateTimeForLogFile():
    ''' Get current date/time string as: YYYY-MM-DD_HH-MM-SS '''
    return datetime.datetime.now().strftime("%Y-%B-%d_%H-%M-%S")

def getCurrentDateTime():
    ''' Get current date/time string as: DD/MM/YYYY HH:MM:SS '''
    return datetime.datetime.now().strftime("%d/%B/%Y %H:%M:%S")

def nameFromDate(seq):
    ''' Make log file name'''
    return 'SGT_' + str(getCurrentDateTimeForLogFile()) + '_seq' + str(seq) + '.log'

def makeFileFromPath(filePath):
    ''' make a file object from a path to that
    file if it doesn't already exist '''
    if not checkExists(filePath):
        try:
            fd = open(filePath, 'a')
            fd.close()
        except:
            print("Can't make file for some reason.")
    return filePath

def makeFolderFromPath(folderPath):
    ''' make a folder(s) from a path if it doesn't
    already exist '''
    if not checkExists(folderPath):
        try:
            os.makedirs(folderPath)
        except:
            print("Can't make the folder for some reason.")
    return folderPath

def initializeLogger(name):
    ''' get and return named logger '''
    if Configuration.DEBUG == True:
        print("UnitTestUtilities - initializeLogger")

    # Check if the path to the log files exists, and create if not
    if not os.path.exists(Configuration.logPath):
        dummy = makeFolderFromPath(Configuration.logPath)

    # get a unique log file name if we don't have a name already
    if name == None or name == "":
        name = getLoggerName()

    logFile = os.path.join(Configuration.logPath, name)

    # if the log file does NOT exist, create it
    if not os.path.exists(logFile):
        logFile = makeFileFromPath(logFile)

    logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', filename=logFile, level=logging.DEBUG)
    logger = logging.getLogger(name)
    return logger

def setUpLogFileHeader():
    ''' Add a header to log file when initalized '''
    if Configuration.DEBUG == True:
        print("UnitTestUtilities - setUpLogFileHeader")
    Configuration.Logger.info("------------ Begin Test ------------------")
    Configuration.Logger.info("Platform: {0}".format(platform.platform()))
    Configuration.Logger.info("Python Version {0}".format(sys.version))
    d = arcpy.GetInstallInfo()
    Configuration.Logger.info("{0} Version {1}, installed on {2}.".format(d['ProductName'], d['Version'], d['InstallDate']))
    Configuration.Logger.info("----------------------------------------")

def checkArcPy():
    ''' sanity check that ArcPy is working '''
    if Configuration.DEBUG == True: print("UnitTestUtilities - checkArcPy")
    arcpy.AddMessage("ArcPy works")

def checkExists(p):
    ''' Python check for existance '''
    if Configuration.DEBUG == True: print("UnitTestUtilities - checkExists")
    return os.path.exists(p)

def createScratch(scratchPath):
    ''' create scratch geodatabase '''
    if Configuration.DEBUG == True: print("UnitTestUtilities - createScratch")
    scratchName = 'scratch.gdb'
    scratchGDB = os.path.join(scratchPath, scratchName)
    if checkExists(scratchGDB):
        print("Scratch already exists")
        return scratchGDB
    try:
        if Configuration.DEBUG == True: print("Creating scratch geodatabase...")
        arcpy.CreateFileGDB_management(scratchPath, scratchName)
        if Configuration.DEBUG == True: print("Created scratch gdb.")
    except:
        print("Problem creating scratch.gdb")
    return scratchGDB

def deleteScratch(scratchPath):
    ''' delete scratch geodatabase '''
    if Configuration.DEBUG == True: print("UnitTestUtilities - deleteScratch")
    try:
        arcpy.Delete_management(scratchPath)
        if Configuration.DEBUG == True: print("Deleted scratch gdb.")
    except:
        print("scratch.gdb delete failed")
    return

def checkFilePaths(paths):
    ''' check file/folder paths exist '''
    if Configuration.DEBUG == True: print("UnitTestUtilities - checkFilePaths")
    for path2check in paths:
        if os.path.exists(path2check):
            if Configuration.DEBUG == True: print("Valid Path: " + path2check)
        else:
            raise Exception('Bad Path: ' + str(path2check))

def checkGeoObjects(objects):
    ''' check geospatial stuff exists '''
    if Configuration.DEBUG == True: print("UnitTestUtilities - checkGeoObjects")
    for object2Check in objects:
        #TODO: Shouldn't we be using arcpy.Exists()?
        desc = arcpy.Describe(object2Check)
        if desc == None:
            print("--> Invalid Object: " + str(object2Check))
            arcpy.AddError("Bad Input")
            raise Exception('Bad Input')
        else:
            if Configuration.DEBUG == True: print("Valid Object: " + desc.Name)

def handleArcPyError():
    ''' Basic GP error handling, errors printed to console and logger '''
    if Configuration.DEBUG == True: print("UnitTestUtilities - handleArcPyError")
    # Get the arcpy error messages
    msgs = arcpy.GetMessages()
    arcpy.AddError(msgs)
    print(msgs)
    Configuration.Logger.error(msgs)

def handleGeneralError():
    ''' Basic error handler, errors printed to console and logger '''
    if Configuration.DEBUG == True: print("UnitTestUtilities - handleGeneralError")
    # Get the traceback object
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]

    # Concatenate information together concerning the error into a message string
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

    # Print Python error messages for use in Python / Python Window
    print(pymsg + "\n")
    Configuration.Logger.error(pymsg)
    print(msgs)
    Configuration.Logger.error(msgs)
    
def geoObjectsExist(objects):
    ''' Return true if all of the input list of geo-objects exist, false otherwise '''
    allExist = True
    for obj in objects:
        if not arcpy.Exists(obj):
            allExist = False
    return allExist
    
def folderPathsExist(paths):
    ''' Return true if all input paths exist, false otherwise '''
    allExist = True
    for p in paths:
        if not os.path.exists(p):
            allExist = False
    return allExist
    
def deleteIfExists(dataset):
    ''' Delete the input dataset if it exists '''
    if (arcpy.Exists(dataset)):
        arcpy.Delete_management(dataset)
        arcpy.AddMessage("deleted dataset: " + dataset)
    