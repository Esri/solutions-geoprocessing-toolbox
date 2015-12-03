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
12/2/2015 - MF - Updates for standards
==================================================
'''

#Import modules
import arceditor
import arcpy
import os
import datetime
from arcpy import env
from datetime import datetime
from datetime import time

#Gets the current directory where the script is sitting so that everything else can work off relative paths.
folder = os.path.dirname(__file__)
topFolder = os.path.dirname(folder)

#Names of folders to be added to topFolder generated above
gdb = "Geodatabase"
NetCDFData = "NetCDFdata"
tls = "Tools"

#Declaration of variables used later
variable = "rh2m;tcdcclm;tmpsfc;hgtclb;vissfc;ugrd10m;vgrd10m;ugrdmwl;vgrdmwl;snodsfc;gustsfc;apcpsfc"
variable2 = "ugrd10m;vgrd10m"
extent = "-126 32 -114 43"
dimension = "time '2015-01-01 00:00:00' '2015-12-31 00:00:00'"
env.workspace = topFolder + os.sep + gdb + "\MAOWdata.gdb"

print(env.workspace)

#______________________________________________________________________________________

def download(paramFN,paramDL):
    #Import custom toolbox required
    arcpy.ImportToolbox(topFolder + os.sep + tls + "\MultidimensionSupplementalTools\Multidimension Supplemental Tools.pyt")
    print("Multidimension Supplemental Tools imported")

    #Get present date and time
    patternDate = '%Y%m%d'
    patternTime = '%H:%M:%S'
    stringDateNow = datetime.utcnow().strftime(patternDate)
    #stringTimeNow = datetime.utcnow().strftime(patternTime) #stringTimeNow not used
    print("datetime returned")

    #Insert present date into string for out_file
    stringToChange = topFolder + os.sep + NetCDFData + r"\nam%s" + paramFN + ".nc"
    stringToChange2 = topFolder + os.sep + NetCDFData + r"\nam%s" + paramFN + "Wind.nc"
    stringToChange3 = r"http://nomads.ncep.noaa.gov/dods/nam/nam%s/nam" + paramDL

    stringToInsert = stringDateNow

    stringFinal = stringToChange % stringToInsert
    stringFinal2 = stringToChange2 % stringToInsert
    stringFinal3 = stringToChange3 % stringToInsert
    filename = "nam%s1hr00z.nc" % stringToInsert

    #Declare variables to be added into OPeNDAP to NetCDF tool for general data
    in_url = stringFinal3
    out_file = stringFinal

    #Run OPeNDAP to NetCDF tool
    arcpy.OPeNDAPtoNetCDF_mds(in_url, variable, out_file, extent, dimension, "BY_VALUE")
    print("OPeNDAP Tool run")

    #Declare variables to be added into OPeNDAP to NetCDF tool for download of wind data
    in_url2 = stringFinal3
    out_file2 = stringFinal2

    #Run OPeNDAP to NetCDF tool
    arcpy.OPeNDAPtoNetCDF_mds( in_url2, variable2, out_file2, extent, dimension, "BY_VALUE")
    print("OPeNDAP Tool run")

    #______________________________________________________________________


    Input_Data = out_file
    Input_Data2 = out_file2

    Raster_Type = "NetCDF" 

    output = topFolder + os.sep + gdb + "\OperationalWeather.gdb\\OperationalData" 
    output2 = topFolder + os.sep + gdb + "\OperationalWeather.gdb\\OperationalWind"

     #Check if the geodatabases stated above exist

    if arcpy.Exists(topFolder + os.sep + gdb):
        print("output exist")
    else:
        print("outout does not exist")

    if arcpy.Exists(topFolder + os.sep + gdb):
        print("output2 exist")
    else:
        print("output2 does not exist")

    # Process: Remove Rasters From Mosaic Dataset
    arcpy.RemoveRastersFromMosaicDataset_management(output, "OBJECTID >=0", "NO_BOUNDARY", "NO_MARK_OVERVIEW_ITEMS", "NO_DELETE_OVERVIEW_IMAGES", "NO_DELETE_ITEM_CACHE", "REMOVE_MOSAICDATASET_ITEMS", "NO_CELL_SIZES")

    arcpy.RemoveRastersFromMosaicDataset_management(output2, "OBJECTID >= 0", "UPDATE_BOUNDARY", "MARK_OVERVIEW_ITEMS", "DELETE_OVERVIEW_IMAGES", "DELETE_ITEM_CACHE", "REMOVE_MOSAICDATASET_ITEMS", "UPDATE_CELL_SIZES")

    print("Removed Raster from Mosaic Dataset")

    # Process: Add Rasters To Mosaic Dataset
    arcpy.AddRastersToMosaicDataset_management(output, Raster_Type, Input_Data, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", "", "0", "1500", "", "*.nc", "SUBFOLDERS", "ALLOW_DUPLICATES", "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", "", "NO_FORCE_SPATIAL_REFERENCE")
    arcpy.AddRastersToMosaicDataset_management(output2, Raster_Type, Input_Data2, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", "", "0", "1500", "", "*.nc", "SUBFOLDERS", "ALLOW_DUPLICATES", "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", "", "NO_FORCE_SPATIAL_REFERENCE")

    print("Rasters added to Mosaic Datasets - "+ filename)

#________________________________________________________________________________________

# get the present time in utc.
# set times are set around the times that the data is released by NOAA

now_time = time(int(datetime.utcnow().strftime("%H")), int(datetime.utcnow().strftime("%M")), int(datetime.utcnow().strftime("%S")))

if now_time >= time(02, 50, 00) and now_time < time(8, 50, 00):
    download("1hr00z", "1hr_00z")

elif now_time >= time(8, 50, 00) and now_time < time(14, 50, 00):
    download("1hr06z", "1hr_06z")

elif now_time >= time(14, 50, 00) and now_time < time(21, 00, 00):
    download("1hr12z", "1hr_12z")

elif ((now_time >= time(21, 00, 00) and now_time <= time(23, 59, 59)) or (now_time >= time(00, 00, 00) and now_time <= time(02, 49, 59))):
    download("1hr18z", "1hr_18z")
