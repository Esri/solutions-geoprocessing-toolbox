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
# TestBuildElevationMosaic.py
# Description: Test Build Elevation Mosaic Toolbox
# Requirements: ArcGIS Desktop Standard
# ----------------------------------------------------------------------------

import arcpy
import sys
import traceback
import TestUtilities
import os

class LicenseError(Exception):
    pass

try:
        
    arcpy.ImportToolbox(TestUtilities.toolbox)
    arcpy.env.overwriteOutput = True
    
    #Set tool param variables
    inputElevationFolderPath = os.path.join(TestUtilities.elevSourcePath)
    inputRasterType = "DTED"
    inputAspectFunctionTemplateFile = os.path.join(TestUtilities.toolboxesPath,"Raster Functions","Aspect.rft.xml")
    inputPercentSlopeFunctionTemplateFile = os.path.join(TestUtilities.toolboxesPath,"Raster Functions","PercentSlope.rft.xml")
    inputHillshadeFunctionTemplateFile = os.path.join(TestUtilities.toolboxesPath,"Raster Functions","Hillshade.rft.xml")
    outputDTMMosaic = "DigitalTerrainModel"
    outputHillshadeMosaic = os.path.join(TestUtilities.outputGDB, "Hillshade")
    outputAspectMosaic = os.path.join(TestUtilities.outputGDB,"Aspect")
    outputPercentSlopeMosaic = os.path.join(TestUtilities.outputGDB,"PercentSlope")
    
    #Testing Build Elevation Mosaics - DTED input
    arcpy.AddMessage("Starting Test: Build Elevation Mosaic Tools")
    arcpy.BuildElevationMosaics_BuildMosaics(TestUtilities.outputGDB,inputElevationFolderPath,inputRasterType,
                                             inputAspectFunctionTemplateFile,inputPercentSlopeFunctionTemplateFile,
                                             inputHillshadeFunctionTemplateFile,outputDTMMosaic,outputHillshadeMosaic,
                                             outputAspectMosaic,outputPercentSlopeMosaic)
    
    #Verify Results
    countDTMFootprints = int(arcpy.GetCount_management(os.path.join(TestUtilities.outputGDB,outputDTMMosaic)).getOutput(0))
    print "DTM Footprint count: " + str(countDTMFootprints)
    
    countSlopeFootprints = int(arcpy.GetCount_management(outputPercentSlopeMosaic).getOutput(0))
    print "PercentSlope Footprint count: " + str(countSlopeFootprints)
    
    countHillshadeFootprints = int(arcpy.GetCount_management(outputHillshadeMosaic).getOutput(0))
    print "Hillshade Footprint count: " + str(countHillshadeFootprints)
    
    countAspectFootprints = int(arcpy.GetCount_management(outputAspectMosaic).getOutput(0))
    print "Aspect Footprint count: " + str(countAspectFootprints)
    
    if (countDTMFootprints < 1) or (countSlopeFootprints < 1) or (countHillshadeFootprints < 1) or (countAspectFootprints < 1):
        print "Invalid output footprint count!"
        raise Exception("Test Failed")
    
    print("Test Passed")

except LicenseError:
    print "Spatial Analyst license is unavailable"  

except arcpy.ExecuteError: 
    # Get the arcpy error messages 
    msgs = arcpy.GetMessages() 
    arcpy.AddError(msgs) 
    print msgs
    
    # return a system error code
    sys.exit(-1)

except:
    # Get the traceback object
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]

    # Concatenate information together concerning the error into a message string
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

    # Return python error messages for use in script tool or Python Window
    arcpy.AddError(pymsg)
    arcpy.AddError(msgs)

    # Print Python error messages for use in Python / Python Window
    print pymsg + "\n"
    print msgs
    
    # return a system error code  
    sys.exit(-1)
    
finally:
    if arcpy.CheckExtension("Spatial") == "Available":
        arcpy.CheckInExtension("Spatial")