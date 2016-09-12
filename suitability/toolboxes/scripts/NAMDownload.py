# coding: utf-8
'''
------------------------------------------------------------------------------
Copyright 2016 Esri
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
 http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
--------------------------------------------------------------------------

Name: NAMDownload.py

Description: Downloads the most up to date data from the NOAA site by getting the present date.

Script works as follow;
    Gets the present time date in UTC
    Uses the OPeNDAP to NetCDF tool from Multidimension Supplimental Tool
    Downloads the specified variables into NetCDF format files and saves them in the relative location, based on where the script file is located.
    The present data is removed from the Mosaic Dataset
    The new data is then loaded into the Mosiac Dataset


History:
9/21/2015 - ab - original coding
6/10/2016 - mf - Updates for dimension and formatting
9/12/2016 - mf - fix for Python3 not liking leading zeros
'''

#Import modules
#import arceditor
import arcpy
import os
import sys
import traceback
import datetime
from arcpy import env
from datetime import datetime
from datetime import time
from datetime import timedelta

#Gets the current directory where the script is sitting so that everything else can work off relative paths.
currentFolder = os.path.dirname(__file__)
topFolder = os.path.dirname(currentFolder)

#Names of folders to be added to topFolder generated above
gdb = "Geodatabase"
NetCDFData = "NetCDFdata"
tls = "Tools"

env.workspace = os.path.join(topFolder, gdb, r"MAOWdata.gdb")
env.scratchWorkspace = env.workspace

#Declaration of variables used later
opVariables = "rh2m;tcdcclm;tmpsfc;hgtclb;vissfc;ugrd10m;vgrd10m;ugrdmwl;vgrdmwl;snodsfc;gustsfc;apcpsfc"
windVariables = "ugrd10m;vgrd10m"
geoExtent = "-126 32 -114 43"
timeDimension = "time '2016-01-01 00:00:00' '2016-12-31 00:00:00'"

# Processing flags
REMOVE_EXISTING_RASTERS = True
DEBUG = True # Extra messaging while debugging

def makeOutputFilePath(topFolder, NetCDFData, stringDateNow, paramFN):
    '''Set output file paths for op weather and wind'''
    opDataFileName = "nam%s%s.nc" % (stringDateNow, paramFN)
    outputOpDataFile = os.path.join(topFolder, NetCDFData, opDataFileName)
    
    windDataFileName = "nam%s%sWind.nc" % (stringDateNow, paramFN)
    outputWindDataFile = os.path.join(topFolder, NetCDFData, windDataFileName)
    return [outputOpDataFile, outputWindDataFile]

def makeSourceURLPath(stringDateNow, paramDL):
    '''make the URL to the source forecast data'''
    return r"http://nomads.ncep.noaa.gov/dods/nam/nam%s/nam%s" % (stringDateNow, paramDL)

def download(stringDateNow, stringTimeNow, paramFN, paramDL):
    '''Download NetCDF data and add to mosaic dataset'''
    
    if DEBUG: print ("datetime to use: %s, %s" % (stringDateNow, stringTimeNow))
    
    #Import required Multidimensional tools
    tbxMST = os.path.join(topFolder, tls, r"MultidimensionSupplementalTools\Multidimension Supplemental Tools.pyt")
    if DEBUG: print ("Importing %s" % tbxMST)
    arcpy.ImportToolbox(tbxMST)   

    # Get target NetCDF data file names
    outputOpDataFile, outputWindDataFile = makeOutputFilePath(topFolder, NetCDFData, stringDateNow, paramFN)
    
    if os.path.exists(outputOpDataFile):
        print("removing existing %s" % outputOpDataFile)
        os.remove(outputOpDataFile)
        
    if os.path.exists(outputWindDataFile):
        print("removing existing %s" % outputWindDataFile)
        os.remove(outputWindDataFile)
    
    # Get source URL path
    in_url = makeSourceURLPath(stringDateNow, paramDL)
    
    #Run OPeNDAP to NetCDF tool
    if DEBUG:
        print("in_url: %s" % in_url)
        print("variable: %s" % opVariables)
        print("dimension: %s" % timeDimension )
    print ("OPeNDAP Tool run for Operational Weather variables...")
    arcpy.OPeNDAPtoNetCDF_mds(in_url, opVariables, outputOpDataFile, geoExtent, timeDimension, "BY_VALUE")

    #Run OPeNDAP to NetCDF tool
    print ("OPeNDAP Tool run for Wind variables...")
    arcpy.OPeNDAPtoNetCDF_mds(in_url, windVariables, outputWindDataFile, geoExtent, timeDimension, "BY_VALUE")

    targetOpDataMosaic = os.path.join(topFolder, gdb, r"OperationalWeather.gdb\OperationalData") 
    targetWindDataMosaic = os.path.join(topFolder, gdb, r"OperationalWeather.gdb\OperationalWind")

    # Remove Rasters From Mosaic Dataset
    if REMOVE_EXISTING_RASTERS:
        print ("Removing existing rasters from Operational Weather...")
        arcpy.RemoveRastersFromMosaicDataset_management(targetOpDataMosaic, "OBJECTID >=0", "NO_BOUNDARY", "NO_MARK_OVERVIEW_ITEMS",
                                                        "NO_DELETE_OVERVIEW_IMAGES", "NO_DELETE_ITEM_CACHE", "REMOVE_MOSAICDATASET_ITEMS",
                                                        "NO_CELL_SIZES")
        print ("Removing existing rasters from Wind...")
        arcpy.RemoveRastersFromMosaicDataset_management(targetWindDataMosaic, "OBJECTID >= 0", "UPDATE_BOUNDARY", "MARK_OVERVIEW_ITEMS",
                                                        "DELETE_OVERVIEW_IMAGES", "DELETE_ITEM_CACHE", "REMOVE_MOSAICDATASET_ITEMS",
                                                        "UPDATE_CELL_SIZES")

    # Add Rasters To Mosaic Dataset
    print ("Adding new rasters from Operational Weather...")
    arcpy.AddRastersToMosaicDataset_management(targetOpDataMosaic, "NetCDF", outputOpDataFile, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY",
                                               "NO_OVERVIEWS", "", "0", "1500", "", "*.nc", "SUBFOLDERS", "ALLOW_DUPLICATES",
                                               "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", "", "NO_FORCE_SPATIAL_REFERENCE")
    print ("Adding new rasters from Wind...")
    arcpy.AddRastersToMosaicDataset_management(targetWindDataMosaic, "NetCDF", outputWindDataFile, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY",
                                               "NO_OVERVIEWS", "", "0", "1500", "", "*.nc", "SUBFOLDERS", "ALLOW_DUPLICATES",
                                               "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", "", "NO_FORCE_SPATIAL_REFERENCE")
    return

def main():
    '''Decide which time period to download'''
    try:
        now_time = time(int(datetime.utcnow().strftime("%H")), int(datetime.utcnow().strftime("%M")), int(datetime.utcnow().strftime("%S")))
        print("UTC time is (now_time): %s" % now_time)
        
        patternDate = '%Y%m%d'
        patternTime = '%H:%M:%S'
        stringDateNow = datetime.utcnow().strftime(patternDate)
        stringTimeNow = datetime.utcnow().strftime(patternTime)
        
        if now_time >= time(2,50,00) and now_time < time(8,50,00):
            print("Going to download 1hr_00z...")
            download(stringDateNow, stringTimeNow,"1hr00z", "1hr_00z")
            
        elif now_time >= time(8,50,00) and now_time < time(14,50,00):
            print("Going to download 1hr_06z...")
            download(stringDateNow, stringTimeNow,"1hr06z", "1hr_06z")
         
        elif now_time >= time(14,50,00) and now_time < time(21,00,00):
            print("Going to download 1hr_12z...")
            download(stringDateNow, stringTimeNow,"1hr12z", "1hr_12z")
        
        elif (now_time >= time(21,00,00) and now_time <= time(23,59,59)):
            print("Going to download 1hr_18z...")
            download(stringDateNow, stringTimeNow,"1hr18z", "1hr_18z")
            
        elif (now_time >= time(00,00,00) and now_time <= time(2,49,59)):
            # Get yesterday's forecast, because today's isn't
            # published yet:
            stringDateNow = (datetime.utcnow() - timedelta(days=1)).strftime(patternDate)
            print("Going to download 1hr_18z for %s..." % stringDateNow)
            download(stringDateNow, stringTimeNow,"1hr18z", "1hr_18z")
        print("Done.") 
    except:
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
        pymsg = "ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        print(pymsg + "\n")
        sys.exit(1)

# MAIN =============================================
if __name__ == "__main__":
    main()
