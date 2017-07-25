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
# WeatherImportModule.py
# Description: Weather Import Module - Contains functions to support the import
#              of weather files (and calculation of derivatives) to the
#              latestforecast.gdb file geodatabase in the MAoW Template.
#              Functions use configuration tables in MAoW.gdb in order to
#              determine how to name the imported files and whether to
#              calculate any derivatives.
# Requirements: ArcGIS Desktop Standard
# -----------------------------------------------------------------------------
# History:
# 3/27/2015 - mf - Updated for Python 3 - tagged as #UPDATE2to3:
#

import arcpy
import os
import sys
import collections
import locale

toolboxesPath = ""
scratchFolder = ""
toolboxPath = ""
forecastGDBPath = ""
maowGDBPath = ""
appPath = ""
configMappings = ""
#configConversions = ""
configDerivatives = ""
weatherTerms = {}
weatherConversions = {}
derivatives = {}
missingWeatherVars = {}
weatherName = "Weather_"
inputMD = ""
dateForecastImportedField = "DateTimeForecastImported"
dateForecastEffectiveFromField = "DateTimeForecastEffectiveFrom"
dateForecastEffectiveToField = "DateTimeForecastEffectiveTo"

def PopulateVariables(pFileType, pInputMD):
    # Identify the module-level variables in use in this function
    global toolboxesPath
    global scratchFolder
    global toolboxPath
    global forecastGDBPath
    global maowGDBPath
    global appPath
    global configMappings
    #global configConversions
    global configDerivatives
    global inputMD

    # Check the pInputMD exists
    if not arcpy.Exists(pInputMD):
        arcpy.AddError("The given Mosaic Dataset does not exist!")
        sys.exit()
    inputMD = pInputMD
    
    # Get the pathname to this script
    scriptPath = sys.path[0]

    # Get the pathname to the MAoW folder and toolbox
    toolboxesPath = os.path.dirname(scriptPath)
    templatePath = os.path.dirname(toolboxesPath)
    dataPath = os.path.join(templatePath, "data")
    appPath = os.path.join(templatePath, "application")
    scratchFolder = os.path.join(arcpy.env.scratchFolder, "ImportedForecast")
    toolboxPath = os.path.join(toolboxesPath, "MAoW Tools.tbx")

    # Now construct pathname to the latest forecast GDB and MAoW GDB
    forecastGDBPath = os.path.join(dataPath, "geodatabases\\latestforecast.gdb")
    maowGDBPath = os.path.join(dataPath, "geodatabases\\MAoW.gdb")

    # And construct the paths to the config tables
    configMappings = maowGDBPath + "\\" + pFileType + "VariableMappings"
    #configConversions = maowGDBPath + "\\ForecastUnitConversions"
    configDerivatives = maowGDBPath + "\\ForecastDerivatives"

    #Check fields exist in the pInputMD
    field_names = [f.name for f in arcpy.ListFields(pInputMD, "", "Date")]
    arcpy.AddMessage(field_names)
    if not dateForecastImportedField in field_names:
        arcpy.AddError("The given Mosaic Dataset does not include a Date field with the name '" + dateForecastImportedField + "'")
        sys.exit()
    if not dateForecastEffectiveFromField in field_names:
        arcpy.AddError("The given Mosaic Dataset does not include a Date field with the name '" + dateForecastEffectiveFromField + "'")
        sys.exit()
    if not dateForecastEffectiveToField in field_names:
        arcpy.AddError("The given Mosaic Dataset does not include a Date field with the name '" + dateForecastEffectiveToField + "'")
        sys.exit()

    # Ensure the scratch folder ("ImportedForecast") exists
    if not os.path.exists(scratchFolder):
        try:
            os.makedirs(scratchFolder)
        except:
            arcpy.AddError("Could not create the folder '" + scratchFolder + "', which doesn't currently exist")
            sys.exit()
    
def EmptyGDB(pGDB):
    # Empty the contents of pGDB
    arcpy.AddMessage("Emptying the contents of " + pGDB)
    arcpy.env.workspace = pGDB
    datasetList = arcpy.ListDatasets("*", "")
    datasetList.extend(arcpy.ListFeatureClasses("*", ""))
    datasetList.extend(arcpy.ListTables("*", ""))
    for dataset in datasetList:
        try:
            arcpy.Delete_management(dataset)
        except:
            arcpy.AddWarning("Could not delete " + dataset + "\n- check for possible locks?\n" + str(sys.exc_info()[0]))
    arcpy.AddMessage("Compacting " + pGDB)
    try:
        arcpy.Compact_management(pGDB)
    except:
        arcpy.AddWarning("Could not compact " + pGDB)

#def LoadDictionaryFromTable(pTable, pKeyField, pValueField):
#    try:
#        return dict([(r.getValue(pKeyField), r.getValue(pValueField)) for r in arcpy.SearchCursor(pTable)])
#    except:
#        arcpy.AddWarning("An error occurred trying to extract attributes\n'" + pKeyField + "' and '" + pValueField + "' from table '" + pTable + "'\n" + str(sys.exc_info()[0]))
#        return {}

def LoadDictionaryFromTable(pTable, pKeyField, pValueField, pOrderField):
    #try:
        if pOrderField == None:
            return dict([(r.getValue(pKeyField), r.getValue(pValueField)) for r in arcpy.SearchCursor(pTable)])
        else:
            return collections.OrderedDict([(r.getValue(pKeyField), r.getValue(pValueField)) for r in arcpy.SearchCursor(pTable, "", None, "", pOrderField)])
    #except:
    #    arcpy.AddWarning("An error occurred trying to extract attributes\n'" + pKeyField + "' and '" + pValueField + "' from table '" + pTable + "' ordering by '" + pOrderField + "'\n" + str(sys.exc_info()[0]))
    #    return {}

#def LoadOrderedListFromTable(pTable, pField, pOrderField):
#    try:
#        return list([r.getValue(pField) for r in arcpy.SearchCursor(pTable,"","","",pOrderField + " A")])
#    except:
#        arcpy.AddWarning("An error occurred trying to extract attribute\n'" + pField + "' from table '" + pTable + "'\n" + str(sys.exc_info()[0]))
#        return []
    
def WeatherVarAvailableForDerivatives(wVar):
    # Remove wVar from any of the lists in the missingWeatherVars dictionary
    # (Eventually, we will check this dictionary to see which derivative tools have
    # no missing variables and so can be run)
    arcpy.AddMessage("Recording that " + wVar + " is available for the creation of any derivatives.")
    #UPDATE2to3: for tool, lst in missingWeatherVars.iteritems():
    for tool, lst in missingWeatherVars.items():
        if wVar in lst:
            lst.remove(wVar)
            arcpy.AddMessage("Removed " + wVar + " from the parameter list for " + tool)
        missingWeatherVars[tool] = lst

def CalculateDerivative(tool, toolboxPath, params, wksp):
    arcpy.AddMessage("CalculateDerivative(" + tool + ", " + toolboxPath + ", " + str(params) + ", " + wksp + ")")
    # first get the tool that we're calling
    arcpy.ImportToolbox(toolboxPath)
    try:
        toolToCall = getattr(arcpy, tool)
    except:
        arcpy.AddWarning("An error occurred trying to find tool '" + tool + "'\n" + str(sys.exc_info()))
        return
    # then grab references to all the bands that relate to the params
    paramBandNumbers = []
    lastIndex = len(params) - 1
    for index, param in enumerate(params):
        if index != lastIndex: # ignore the output parameter (i.e. the last one)
            #UPDATE2to3: paramBandNumbers.append("Band_" + str(weatherTerms.values().index(param) + 1))
            paramBandNumbers.append("Band_" + str(list(weatherTerms.values()).index(param) + 1))
                  
    arcpy.AddMessage("Calculating derivative: calling '" + tool + "' with params '" + str(params) + "' which are represented by bands '" + str(paramBandNumbers) + "'")
    try:
        result = arcpy.ListRasters_maow(wksp, weatherName + "*")
        out = str(result.getOutput(0))
        datasetList = out.split(";")
    except:
        arcpy.AddWarning("An error occurred listing the rasters in '" + wksp + "'\n" + str(sys.exc_info()))
        datasetList = []
    if datasetList:
        for dataset in datasetList:
            # we are now iterating each forecast period (datetime)
            
            # Remove any quotes from start and end of the path
            if dataset.startswith("'") and dataset.endswith("'"):
                dataset = dataset[1:-1]
                
            # Construct the parameters that we'll pass to the derivative tool
            newparams = []
            del newparams[:]
            for band in paramBandNumbers:
                newparams.append(dataset + "\\" + band)

            # Add the output parameter
            outParam = dataset.replace(weatherName, params[-1].replace(" ","_") + "__")
            newparams.append(outParam)
            # Run the tool to create the derivative for this forecast period
            arcpy.AddMessage("Running tool : " + tool + "(" + str(newparams) + ")")
            arcpy.ImportToolbox(toolboxPath)
            try:
                toolToCall(*newparams)
            except:
                arcpy.AddWarning("An error occured trying to call tool '" + tool + "' with parameters\n" + str(newparams) + "\n" + str(sys.exc_info()))                                                                                                                     
    else:
        arcpy.AddMessage("No datasets found in '" + wksp + "'")

def LoadConfigTables(pFileType):
    # Identify the module-level variables in use in this function
    global weatherTerms
    global weatherConversions
    global derivatives
    global orderedTools
    global missingWeatherVars
    
    # Pull the mappings between file variable names and MAoW variable names into a dictionary (ordered)
    myKeyField = pFileType + "Variable"
    myValueField = "MAoWVariable"
    myOrderField = "BandOrder"
    weatherTerms = LoadDictionaryFromTable(configMappings, myKeyField, myValueField, myOrderField)

    # Set up dictionary of conversions to be applied
    #myKeyField = "VariableName"
    #myValueField = "MAoWTool"
    #myOrderField = None
    #weatherConversions = LoadDictionaryFromTable(configConversions, myKeyField, myValueField, myOrderField)

    # Set up a dictionary (ordered) of derivatives to be built
    myKeyField = "DerivativeTool"
    myValueField = "ToolParameters"
    myOrderField = "OrderToRun"
    derivatives = LoadDictionaryFromTable(configDerivatives, myKeyField, myValueField, myOrderField)
    #...and turn the comma-separated values into lists...
    #UPDATE2to3: for k, v in derivatives.iteritems():
    for k, v in derivatives.items():
        if v == "":
            vLst = []
        else:
            vLst = v.split(",")
            #remove leading and trailing spaces
            vLst = [s.strip(' ') for s in vLst]
        derivatives[k] = vLst

    # Keep a dynamic copy of the derivatives dictionary, which we'll edit as we go to keep track of whether we've got the params we need
    missingWeatherVars = dict(derivatives)
    # Clearly, we don't need the output parameter as an input to check for, so drop that off
    #UPDATE2to3: for key, val in missingWeatherVars.iteritems():
    for key, val in missingWeatherVars.items():
        varList = list(val)
        if varList: varList.pop()
        missingWeatherVars[key] = varList

def CreateEmptyRaster():
    # Create an empty raster dataset
    # For use primarily to provide placeholders in multi-band rasters where the data for a band is missing
    #emptyRaster = os.path.join(toolboxesPath, "scratch\\scratch.gdb")
    #arcpy.AddMessage("Creating Empty Raster in '" + emptyRaster + "'")
    try:
        arcpy.CreateRasterDataset_management(scratchFolder, "EmptyRaster.tif",
                                             "#","8_BIT_UNSIGNED","#","1","#","NONE","128 128","LZ77","#")
    except:
        return scratchFolder + "\\EmptyRaster.tif"
    return scratchFolder + "\\EmptyRaster.tif"

def ReloadMD():
    # Empty the mosaic dataset prior to reloading it
    arcpy.AddMessage("Removing previous forecast data from mosaic dataset...")
    arcpy.RemoveRastersFromMosaicDataset_management(inputMD, "1=1")
    # Add the rasters to the mosaic dataset
    arcpy.AddMessage("Adding new forecast data to mosaic dataset...")
    arcpy.AddRastersToMosaicDataset_management(inputMD, "Raster Dataset", forecastGDBPath)
    # Check something was imported
    result = int(arcpy.GetCount_management(inputMD).getOutput(0))
    if result > 0:
        # Re-calculate statistics on the mosaic dataset
        arcpy.AddMessage("Calculating statistics on the newly loaded mosaic dataset")
        arcpy.CalculateStatistics_management(inputMD)
        # Re-build overviews on the mosaic dataset
        #arcpy.AddMessage("Building overviews on the mosaic dataset")
        #arcpy.BuildOverviews_management(inputMD)
        # Calculate the time fields on the mosaic dataset
        arcpy.AddMessage("Calculating the time fields on the mosaic dataset")
        locale.setlocale(locale.LC_TIME, '')
        mdLayer = "mdLayer"
        arcpy.MakeMosaicLayer_management(inputMD, mdLayer, "Category = 1") # Leave out overviews - only calculate fields on primary rasters
        arcpy.CalculateField_management(mdLayer, dateForecastImportedField, """time.strftime("%c")""", "PYTHON","#")
        arcpy.CalculateField_management(mdLayer, dateForecastEffectiveFromField, """time.strftime("%c", time.strptime(!Name!,""" + "\"" + weatherName + """%Y%m%dT%H%M"))""", "PYTHON", "#")
        arcpy.CalculateField_management(mdLayer, dateForecastEffectiveToField, "!" + dateForecastEffectiveFromField + "!", "PYTHON", "#")

        # Now *** deal with all the referenced mosaic datasets that hang off this one - recalc stats, overviews etc ***

def CalcDerivatives():
    # Look through the missingWeatherVars dictionary to check for empty lists against tool names.
    # If a list is empty, that means we've imported all the weather variables needed to run that tool, so
    # we can go ahead and run it. Note that we ensure we run tools in the order they are specified in config
    # so that if one derivative uses another derivative as input, we won't get an error
    arcpy.AddMessage("Iterating derivatives: " + str(derivatives))
    #UPDATE2to3: for tool, params in derivatives.items():
    for tool, params in list(derivatives.items()):
        arcpy.AddMessage("Checking whether all parameters are available for running " + tool)
        if not missingWeatherVars[tool]:
            CalculateDerivative(tool, toolboxPath, params, forecastGDBPath)
        else:
            arcpy.AddWarning("Could not run " + tool + " because there are missing parameters: " + str(missingWeatherVars[tool]))
