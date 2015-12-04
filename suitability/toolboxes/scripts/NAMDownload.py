# coding: utf-8
'''
-----------------------------------------------------------------------------
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
-----------------------------------------------------------------------------

==================================================
NAMDownload.py
--------------------------------------------------
requirements:
* ArcGIS 10.3+
* Python 2.7
* Multidimension Supplemental Tools - download and install from:
    http://www.arcgis.com/home/item.html?id=9f963f362fe5417f87d44618796db938
author: ArcGIS Solutions
company: Esri
==================================================
description:
Downloads the most up to date data from the NOAA site by getting the present date.
Script works as follow;
1. Gets the present time date in UTC
2. Uses the OPeNDAP to NetCDF tool from Multidimension Supplemental Tool
3. Downloads the specified variables into NetCDF format files and saves
     them in the relative location, based on where the script file is located.
4. The present data is removed from the Mosaic Dataset
5. The new data is then loaded into the Mosaic Dataset

==================================================
history:
9/21/2015 - AB - Original development
12/2/2015 - MF - Updates optimization and path changes
==================================================
'''

#Import modules
import arceditor
import arcpy
import os
import sys
import datetime
from arcpy import env
from datetime import datetime
from datetime import time
import traceback

# Required folder paths:
scriptsFolder = os.path.dirname(__file__) #.\solutions-geoprocessing-toolbox\suitability\toolboxes\scripts
toolboxFolder = os.path.dirname(scriptsFolder) #.\solutions-geoprocessing-toolbox\suitability\toolboxes
tooldataFolder = os.path.join(toolboxFolder, "tooldata") #.\solutions-geoprocessing-toolbox\suitability\toolboxes\tooldata
maowOperationalWeatherGeodatabase = os.path.join(tooldataFolder, "OperationalWeather.gdb")
maowDefaultGeodatabase = os.path.join(tooldataFolder, "MAOWdata.gdb")
netcdfFolder = os.path.join(tooldataFolder, "NetCDFData")
mstToolboxPath = os.path.join(scriptsFolder,
                              "MultidimensionSupplementalTools",
                              "MultidimensionSupplementalTools",
                              "Multidimension Supplemental Tools.pyt")

#TODO: I'm thinking we need to redo this to let user decide where to clip the weather, and not hardcode it
extent = "-126 32 -114 43"
dimension = "time '2015-01-01 00:00:00' '2015-12-31 00:00:00'"
Raster_Type = "NetCDF"
stringDateNow = None
env.workspace = maowDefaultGeodatabase

class NAMDownloadException(Exception):
    ''' custom exception '''
    def __init__(self, msg):
        ''' override init'''
        if sys.exc_info()[2] != None:
            msg += traceback.format_tb(sys.exc_info()[2])[0]
        self.tb = msg
    def __str__(self):
        ''' override str '''
        return repr(self.tb)

def checkArcPyExists(f):
    ''' use ArcPy to check if geo-objects exist or not'''
    return arcpy.Exists(f)

def checkOSExists(f):
    ''' use Python's os.exists to check if something exists or not'''
    return os.path.exists(f)

def removeFile(f):
    ''' os.remove '''
    print("Removing " + str(f))
    if os.path.exists(f):
        os.remove(f)
    return

def urlToFile(url, variable, dfile):
    ''' Get netcdf data from OPeNDAP URL '''
    try:
        print("Getting data from: " + str(url))
        arcpy.OPeNDAPtoNetCDF_mds(url, variable, dfile, extent, dimension, "BY_VALUE")
        return True
    except NAMDownloadException as e:
        print("Error in urlToFile: \n" + str(e.tb))

def removeFromMosaics(data):
    ''' remove rasters from mosaic dataset '''
    base = os.path.basename(data)
    print("Removing existing mosaics from: " + str(base))
    try:
        if base == "OperationalData":
            arcpy.RemoveRastersFromMosaicDataset_management(data,
                                                            "OBJECTID >=0",
                                                            "NO_BOUNDARY",
                                                            "NO_MARK_OVERVIEW_ITEMS",
                                                            "NO_DELETE_OVERVIEW_IMAGES",
                                                            "NO_DELETE_ITEM_CACHE",
                                                            "REMOVE_MOSAICDATASET_ITEMS",
                                                            "NO_CELL_SIZES")
            return True
        elif base == "OperationalWind":
            arcpy.RemoveRastersFromMosaicDataset_management(data,
                                                            "OBJECTID >= 0",
                                                            "UPDATE_BOUNDARY",
                                                            "MARK_OVERVIEW_ITEMS",
                                                            "DELETE_OVERVIEW_IMAGES",
                                                            "DELETE_ITEM_CACHE",
                                                            "REMOVE_MOSAICDATASET_ITEMS",
                                                            "UPDATE_CELL_SIZES")
            return True
        else:
            return False
    except NAMDownloadException as e:
        print("Error in removeFromMosaics: \n" + str(e.tb))

def addMosaics(data, dfile):
    ''' Add data to mosaic dataset  '''
    print("Adding new data to mosaic")
    try:
        arcpy.AddRastersToMosaicDataset_management(data, Raster_Type, dfile,
                                                   "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY",
                                                   "NO_OVERVIEWS", "",
                                                   "0", "1500",
                                                   "", "*.nc",
                                                   "SUBFOLDERS", "ALLOW_DUPLICATES",
                                                   "NO_PYRAMIDS", "NO_STATISTICS",
                                                   "NO_THUMBNAILS", "",
                                                   "NO_FORCE_SPATIAL_REFERENCE")
        return True
    except NAMDownloadException as e:
        print("Error in addMosaics: \n" + str(e.tb))

def process(url, variable, dfile, data):
    ''' Combine processes for base and wind data '''
    try:
        if not urlToFile(url, variable, dfile):
            raise
        if not removeFromMosaics(data):
            raise
        if not addMosaics(data, dfile):
            raise
        return True
    except NAMDownloadException as e:
        print("Error in process: \n" + str(e.tb))

def download(paramFN, paramDL):
    ''' main work method '''
    try:
        print("Working on time index: " + str(paramFN))
        #Multidimension Supplemental Tools are required!
        arcpy.ImportToolbox(mstToolboxPath, "mds")

        #Get present date
        patternDate = '%Y%m%d'
        global stringDateNow
        if stringDateNow == None:
            stringDateNow = datetime.utcnow().strftime(patternDate)
        print("Target date: " + str(stringDateNow))

        noaaURLBase = r"http://nomads.ncep.noaa.gov/dods/nam/nam%s/nam" + paramDL
        noaaURL = noaaURLBase % stringDateNow
        #filename = "nam%s1hr00z.nc" % stringDateNow

        print("Building forecast data...")
        netcdfDataFileBase = os.path.join(netcdfFolder, r"nam%s" + paramFN + ".nc") % stringDateNow
        if checkOSExists(netcdfDataFileBase):
            print("deleting existing " + str(netcdfDataFileBase))
            removeFile(netcdfDataFileBase)
        forecastVariable = r"rh2m;tcdcclm;tmpsfc;hgtclb;vissfc;ugrd10m;vgrd10m;ugrdmwl;vgrdmwl;snodsfc;gustsfc;apcpsfc"
        operationalData = os.path.join(maowOperationalWeatherGeodatabase, "OperationalData")
        result = process(noaaURL, forecastVariable, netcdfDataFileBase, operationalData)

        print("Building wind data...")
        netcdfWindFileBase = os.path.join(netcdfFolder, r"nam%s" + paramFN + "Wind.nc") % stringDateNow
        if checkOSExists(netcdfWindFileBase):
            print("deleting existing " + str(netcdfWindFileBase))
            removeFile(netcdfWindFileBase)
        windVariable = r"ugrd10m;vgrd10m"
        operationalWind = os.path.join(maowOperationalWeatherGeodatabase, "OperationalWind")
        result = process(noaaURL, windVariable, netcdfWindFileBase, operationalWind)

        print("Done.")

    except NAMDownloadException as e:
        print("Error in main: \n" + str(e.tb))

# get the present time in utc.
# set times are set around the times that the data is released by NOAA
now_time = time(int(datetime.utcnow().strftime("%H")),
                int(datetime.utcnow().strftime("%M")),
                int(datetime.utcnow().strftime("%S")))
print("Now time: " + str(now_time))
if now_time >= time(2, 50, 00) and now_time < time(8, 50, 00):
    download("1hr00z", "1hr_00z")

elif now_time >= time(8, 50, 00) and now_time < time(14, 50, 00):
    download("1hr06z", "1hr_06z")

elif now_time >= time(14, 50, 00) and now_time < time(21, 00, 00):
    download("1hr12z", "1hr_12z")

elif ((now_time >= time(21, 00, 00) and now_time <= time(23, 59, 59)) or (now_time >= time(00, 00, 00) and now_time <= time(2, 49, 59))):
    download("1hr18z", "1hr_18z")
