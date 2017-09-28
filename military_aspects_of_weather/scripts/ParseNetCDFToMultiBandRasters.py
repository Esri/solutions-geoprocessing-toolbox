#------------------------------------------------------------------------------
# Copyright 2013 Esri
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
# ParseNetCDFToMultiBandRasters.py
# Description: Parse NetCDF To Individual Rasters - Exports the contents of a
#              NetCDF file to the latestforecast.gdb file geodatabase in the
#              MAoW Template. Uses configuration tables in MAoW.gdb in order to
#              determine how to name the exported files and whether to
#              calculate any derivatives.
# Requirements: ArcGIS Desktop Standard
# ----------------------------------------------------------------------------
# History:
# 3/27/2015 - mf - Update for Python 3 - tagged as #UPDATE2to3:

import arcpy
import os
import sys
import collections
import datetime, time, locale
import WeatherImportModule as wim
from arcpy import env

inNetCDF = arcpy.GetParameterAsText(0)
inputMD = arcpy.GetParameterAsText(1)

# Populate the key variables needed by this script
wim.PopulateVariables("NetCDF", inputMD)

# Empty the existing contents of the forecast GDB
wim.EmptyGDB(wim.forecastGDBPath)

# Load the config tables into dictionaries
wim.LoadConfigTables("NetCDF")

# set the locale to the user's environment
locale.setlocale(locale.LC_TIME, '')

# access the properties of the NetCDF file
ncFP = arcpy.NetCDFFileProperties(inNetCDF)

timeVar = "time"
latVar = "latitude"
longVar = "longitude"
vars = ncFP.getVariables()
# First, loop through the variables to get the latitude, longitude and time variables
for var in vars:
    stdvar = ""
    try:
        stdvar = ncFP.getAttributeValue(var, "standard_name")
        arcpy.AddMessage("Standard name for variable " + var + " is " + stdvar)
    except:
        arcpy.AddMessage("No standard name attribute for " + var)
        try:
            stdvar = ncFP.getAttributeValue(var, "long_name")
            arcpy.AddMessage("Will attempt using the long name, '" + stdvar + "' as a standard name, failing which '" + var + "'")
        except:
            arcpy.AddMessage("No long name attribute for " + var)
            stdvar = var
            arcpy.AddMessage("Will attempt using the variable name, '" + var + "' as a standard name")
    if stdvar.lower() == latVar.lower() or stdvar.lower() == latVar[0:2].lower(): latVar = var
    if stdvar.lower() == longVar.lower() or stdvar.lower() == longVar[0:2].lower(): longVar = var
    if stdvar.lower() == timeVar.lower(): timeVar = var

# Set up an empty list to hold the NetCDF Raster Layers that will form our bands (each band will represent a weather variable)
rasterBands = []
nullRaster = None
# Get the weather variables available in the NetCDF file
ncdfVars = ncFP.getVariablesByDimension(timeVar)
# Loop through an (ordered) dict of weather terms from the NetCDF variable mapping configuration table
#UPDATE2to3: for ncdfVar, maowVar in wim.weatherTerms.items():
for ncdfVar, maowVar in list(wim.weatherTerms.items()):
    fileVar = None
    if maowVar != None:
        # Check whether the configured variable exists in the NetCDF file
        arcpy.AddMessage("Checking for variable " + ncdfVar)
        vartype = ""
        for var in ncdfVars:
            try:
                stdvar = ncFP.getAttributeValue(var, "standard_name")
                vartype = "standard name"
            except:
                try:
                    stdvar = ncFP.getAttributeValue(var, "long_name")
                    vartype = "long name"
                except:
                    stdvar = var
                    vartype = "variable name"
            if stdvar.strip() == "":
                try:
                    stdvar = ncFP.getAttributeValue(var, "long_name")
                    vartype = "long name"
                except:
                    stdvar = var
                    vartype = "variable name"
            if stdvar.strip() == "":
                stdvar = var
                vartype = "variable name"               
            if ncdfVar == stdvar:
                arcpy.AddMessage("...matched with " + vartype)
                fileVar = var
                break
    if fileVar != None:
        # We've found a weather variable of interest to us within the NetCDF file, so...
        # now call Make NetCDF Raster Layer, passing lat,lon and the var, and append it to a list of rasters that will form our raster bands
        arcpy.AddMessage("Making NetCDF Raster Layer with " + inNetCDF + ", " + var + ", " + longVar + ", " + latVar + ", " + maowVar)
        rasterBands.append(arcpy.MakeNetCDFRasterLayer_md(inNetCDF, var, longVar, latVar, maowVar))
        # keep track of the weather variables that are available for generating derivatives
        wim.WeatherVarAvailableForDerivatives(maowVar)
##    else:
##        if nullRaster == None:
##            # create a null raster to fill the gap
##            nullRaster = wim.CreateEmptyRaster()
##        suffix = ""
##        if ncdfVar != None:
##            suffix = " for " + ncdfVar
##        if maowVar != None:
##            if suffix == "":
##                suffix = " for"
##            suffix += " (" + maowVar + ")"
##        arcpy.AddMessage("Setting empty raster" + suffix)
##        rasterBands.append(nullRaster)

# Now loop through each time dimentsion
for i in range(0, ncFP.getDimensionSize(timeVar)):
    arcpy.AddMessage("Looping through time")
    ncTimeValue = ncFP.getDimensionValue(timeVar, i)
    arcpy.AddMessage(ncTimeValue)
    arcpy.AddMessage("formatting the date")
    locale.setlocale(locale.LC_TIME, '')
    try:
        dt = time.strptime(ncTimeValue, "%c")
    except:
        # if the time is midnight, the time portion of the date string may be missing
        dt = time.strptime(ncTimeValue, "%x")
    arcpy.AddMessage("got the date...")
    strDate = time.strftime("%Y%m%dT%H%M", dt)
    arcpy.AddMessage(strDate)

    for rast in rasterBands:
        if rast != nullRaster:
            # call Select by Dimension tool to alter the raster layer visible dimension of each weather variable to be that of the time of interest
            arcpy.SelectByDimension_md(rast,[[timeVar, ncTimeValue]],"BY_VALUE")       

    # generate the name of the output raster
    outName = wim.forecastGDBPath + "\\" + wim.weatherName + strDate
    # generate the (multi-band) output raster
    arcpy.AddMessage("Running arcpy.CompositeBands_management('" + str(rasterBands) + "', '" + outName + "')")
    arcpy.CompositeBands_management(rasterBands, outName)

arcpy.AddMessage("Finished importing rasters from NetCDF file")

# Reload the Mosaic Dataset with the newly created forecast data
arcpy.AddMessage("")
arcpy.AddMessage("Refreshing the data in the Mosaic Dataset")
wim.ReloadMD()

# Calculate any derivatives as necessary
arcpy.AddMessage("Calculating derivatives...")
wim.CalcDerivatives()

# Return the mosaic dataset which contains the raw weather outputs of this tool
arcpy.SetParameterAsText(2, inputMD)

# Also return the latestforecast.gdb file geodatabase which further contains any derived outputs of this tool
arcpy.SetParameterAsText(3, wim.forecastGDBPath)
