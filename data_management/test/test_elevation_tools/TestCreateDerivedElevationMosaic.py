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
# TestCreateDerivedElevationMosaic.py
# Description: Test Create Derived Elevation Mosaic
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

    print("Setting environment...")
    arcpy.ImportToolbox(TestUtilities.toolbox,"elev")
    arcpy.env.overwriteOutput = True

    #Set tool param variables
    print("Setting inputs...")
    targetGeodatabase = TestUtilities.scratchGDB
    targetMosaicName = "DerivedDTM"
    inputSourceMosaic = os.path.join(TestUtilities.scratchGDB,"DigitalTerrainModel")

    #Testing Create Derived Elevation Mosaic
    arcpy.AddMessage("Starting Test: Create Derived Elevation Mosaic")
    arcpy.createDerivedMD_elev(targetGeodatabase, targetMosaicName, arcpy.Describe(inputSourceMosaic).spatialReference, inputSourceMosaic)

    #Verify Results
    print("Verifying results...")
    countDTMFootprints = int(arcpy.GetCount_management(os.path.join(targetGeodatabase, targetMosaicName)).getOutput(0))
    print "DTM Footprint count: " + str(countDTMFootprints)

    if (countDTMFootprints < 1):
        print("Less than one footprint! (" + str(countDTMFootprints) + ")")
        raise Exception("Test Failed")
    else:
        print("Test Passed")

except LicenseError:
    print("Spatial Analyst license is unavailable")

except arcpy.ExecuteError: 
    # Get the arcpy error messages 
    msgs = arcpy.GetMessages()
    arcpy.AddError(msgs)

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
    print(pymsg + "\n")
    print(msgs)

    # return a system error code  
    sys.exit(-1)

finally:
    if arcpy.CheckExtension("Spatial") == "Available":
        arcpy.CheckInExtension("Spatial")
    print("Deleting source mosaic...")
    arcpy.Delete_management(inputSourceMosaic)
    print("Deleteing derived mosaic...")
    arcpy.Delete_management(os.path.join(targetGeodatabase, targetMosaicName))
