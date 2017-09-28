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
# ParseGRIBToMultiBandRasters.py
# Description: Parse GRIB(s) To MultiBand Rasters - Exports the contents of a
#              folder of GRIB file(s) to the latestforecast.gdb file gdb in the
#              MAoW Template, creating one raster per timeframe, with one
#              weather variable per band.
#              Employs the NOAA tool "Degrib" in order to extract the GRIB
#              files to rasters in a temporary output folder, which should be
#              downloaded into your project by an ANT script when you grab it
#              from GitHub.
#              Uses configuration tables in MAoW.gdb in order to determine how
#              to name the exported files and whether to calculate any
#              derivatives.
# Requirements: ArcGIS Desktop Basic, DeGRIB exectuable (3rd Party)
# ----------------------------------------------------------------------------
# History: 
# 3/27/2015 - mf - update for python 3 - tagged as #UPDATE2to3:
#

import arcpy
import os
import sys
import datetime, time, locale
import subprocess
import WeatherImportModule as wim
from arcpy import env

inputfolder = arcpy.GetParameterAsText(0)
inputMD = arcpy.GetParameterAsText(1)

if (not os.path.exists(inputfolder)):
    arcpy.AddError("The folder '" + inputfolder + "' does not exist.")
    sys.exit()

# Populate the key variables needed by this script
wim.PopulateVariables("Grib", inputMD)

#Get the path to the Degrib executable (NB: This path must NOT contain spaces)
#ANT should have built the executable into your template...
degribExec = os.path.join(wim.appPath, r"degrib\bin\degrib.exe")

if not os.path.exists(degribExec):
   arcpy.AddError("The specified path to DeGRIB does not exist - '" + degribExec + "'")
   sys.exit()
elif degribExec.find(" ") >= 0:
   arcpy.AddError("The path to the DeGRIB executable must not contain any spaces")
   sys.exit()
   
# Empty the existing contents of the forecast GDB
wim.EmptyGDB(wim.forecastGDBPath)

# Empty the scratch folder
arcpy.AddMessage("Checking whether anything exists in " + wim.scratchFolder)
scratchdir = os.listdir(wim.scratchFolder)
if scratchdir:
   arcpy.AddMessage("Deleting the contents of " + wim.scratchFolder)
   for the_file in scratchdir:
       file_path = os.path.join(wim.scratchFolder, the_file)
       try:
           if os.path.isfile(file_path):
               os.unlink(file_path)
       #UPDATE2to3:except Exception, e:
       except Exception as e:
           arcpy.AddError("There was a problem deleting the file '" + file_path + "'\n\n" + e.message)

# Load the config tables into dictionaries
wim.LoadConfigTables("Grib")

#Run degrib.exe to produce output rasters
for root, dirs, filenames in os.walk(inputfolder):
   for filename in filenames:
        filename = os.path.join(root, filename)
        # grab the extent of the file
        gribExt = arcpy.Raster(filename).extent
        cmdLine = degribExec + " -in \"" + filename + "\" -C -msg all -Flt -Interp 0 -Decimal 5 -AscGrid -nMet -Unit m -nameStyle \"%e__%V.asc\" -namePath \"" + wim.scratchFolder + "\""
        arcpy.AddMessage(cmdLine)
        if os.name == "nt":
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            subprocess.call(cmdLine, shell=True, startupinfo=startupinfo)
        else:
            os.system(cmdLine)

arcpy.ImportToolbox(wim.toolboxPath)
try:
    result = arcpy.ListRasters_maow(wim.scratchFolder, "*")
    out = str(result.getOutput(0))
    datasetList = out.split(";")
except:
    arcpy.AddWarning("An error occurred listing the rasters in '" + wim.scratchFolder + "' with the wildcard '*'\n" + str(sys.exc_info()))
    datasetList = []
if datasetList:
    # create a dictionary, keyed on date, to hold the rasters
    dictData = {}
    for dataset in datasetList:
        # we are now iterating each raster that has been pulled out of the GRIB file(s)
        # Remove any quotes from start and end of the path
        arcpy.AddMessage("1:" + dataset)
        if dataset.startswith("'") and dataset.endswith("'"):
            dataset = dataset[1:-1]
        arcpy.AddMessage("2:" + dataset)
        filename = os.path.basename(dataset)
        arcpy.AddMessage("3:" + filename)
        stdvar = filename[0:filename.find("__")]
        strDate = filename[filename.find("__")+2:filename.rfind(".")]
        unknownVar = "unknown"
        arcpy.AddMessage("Retrieving weather term for " + stdvar)
        weatherVar = wim.weatherTerms.get(stdvar, unknownVar)
        if weatherVar == unknownVar or weatherVar == None:
            arcpy.AddMessage("No weather term exists for " + stdvar)
        else:
            arcpy.AddMessage("variable: " + weatherVar)

            # keep track of the weather variables that are available for generating derivatives
            wim.WeatherVarAvailableForDerivatives(weatherVar)

            # re-format the datetime to include a "T" between date and time
            arcpy.AddMessage("formatting the date")
            strDate = strDate[0:8] + "T" + strDate[8:]
            arcpy.AddMessage(strDate)

            # add a (weatherVar, dataset) tuple to the dictionary dictData, with strDate as key
            dictData.setdefault(strDate, []).append((weatherVar, dataset))
            
    # Now iterate dictData to create multi-band rasters for each strDate (each weatherVar is a band - in appropriate order)
    #UPDATE2to3: for dt, lst in dictData.items():
    for dt, lst in list(dictData.items()):
        nullRaster = None
        rasterPaths = []
        #UPDATE2to3: for wt in wim.weatherTerms.values():
        for wt in list(wim.weatherTerms.values()):
            addRaster = None
            for wt2, rasterPath in lst:
                if wt == wt2:
                    addRaster = rasterPath
                    break
##            if addRaster == None:
##                if nullRaster == None:
##                    # create a null raster to fill the gap
##                    nullRaster = wim.CreateEmptyRaster()
##                addRaster = nullRaster
            # append the raster to the list of raster paths
            if addRaster != None:
               rasterPaths.append(addRaster)

        # generate the name of the output raster
        outName = wim.forecastGDBPath + "\\" + wim.weatherName + dt
        # generate the (multi-band) output raster
        arcpy.AddMessage("Running arcpy.CompositeBands_management('" + str(rasterPaths) + "', '" + outName + "')")
        # set the original processing extent (degrib sometimes adds an empty column)
        arcpy.env.extent = gribExt
        arcpy.CompositeBands_management(rasterPaths, outName)

# Reload the Mosaic Dataset with the newly created forecast data
arcpy.AddMessage("")
arcpy.AddMessage("Refreshing the data in the Mosaic Dataset")
wim.ReloadMD()

# Calculate any derivatives as necessary
wim.CalcDerivatives()

# Return the mosaic dataset which contains the raw weather outputs of this tool
arcpy.SetParameterAsText(2, inputMD)

# Also return the latestforecast.gdb file geodatabase which further contains any derived outputs of this tool
arcpy.SetParameterAsText(3, wim.forecastGDBPath)
