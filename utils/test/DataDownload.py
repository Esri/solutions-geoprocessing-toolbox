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
#-----------------------------------------------------------------------------
# DataDownload.py
# Description: This script downloads sample data from ArcGIS Online, temporarily
# saves the zip file, extracts the zip to the target location, then deletes the 
# temporary zip file. 
# Requirements: ArcGIS Desktop Standard
# ----------------------------------------------------------------------------
#
# ==================================================
# history:
# 12/01/2015 - JH - creation
# ==================================================

import arcpy
import os
import sys
import logging
import zipfile
import TestUtilities
import UnitTestUtilities

''' ArcGIS Online URL's '''
sunPosUrl = "http://www.arcgis.com/sharing/content/items/bf6a04b4c9a3447b91e9c0b4074ca1e4/data"

####################################
def createDataFolder(path):
    ''' If it doesn't already exist, create a 'data' sub-directory in the path '''
    dataPath = os.path.normpath(os.path.join(path, r"data"))
    if not os.path.exists(dataPath):
        os.makedirs(dataPath)
    return dataPath
    
def saveOnlineDataAsZip(url, zipName):
    ''' Save the zip file from the specified url to the current directory, passing in '''
    ''' the name to use for the saved zip file '''
    try:
        # Python 2
        import urllib  
        #(zipFile, headers) = urllib.urlretrieve(url, "test_sun_position.gdb.zip")
        (zipFile, headers) = urllib.urlretrieve(url, zipName)
        return zipFile
    except:
        # Python 3
        import urllib.request
        #(zipFile, headers) = urllib.request.urlretrieve(url, "test_sun_position.gdb.zip")
        (zipFile, headers) = urllib.request.urlretrieve(url, zipName)
        return zipFile
        
def extractDataZip(zip, path):
    ''' Extract zip file data into the given path '''
    with zipfile.ZipFile(zip) as f:
        f.extractall(path)
        
def deleteZip(tempFile):
    ''' Delete the data zip file '''
    os.remove(tempFile)
    
    
def runDataDownload(gdbName, url):
    ''' Download and extract the geodatabase with specified gdbName from the given url '''
    visDataPath = createDataFolder(TestUtilities.visibilityPaths)
    #sunPosPath = os.path.normpath(os.path.join(visDataPath, "test_sun_position.gdb"))
    sunPosPath = os.path.normpath(os.path.join(visDataPath, gdbName))
    objects = [sunPosPath]
    exists = UnitTestUtilities.folderPathsExist(objects)
    print("Sun Pos GDB Exists? " + str(exists))
        
    if not exists:
        print("Save Online Data test...")
        zipName = gdbName + ".zip"
        print("Zip Name: " + zipName)
        sunPosZip = saveOnlineDataAsZip(url, zipName)
        print("Extracting zip...")
        extractDataZip(sunPosZip, sunPosPath)
        print("Deleting zip...")
        deleteZip(sunPosZip)
        return True
    else:
        return False
    