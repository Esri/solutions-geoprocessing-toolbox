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
# TestCreateSourceElevationMosaic.py
# Description: Test Create Source Elevation Mosaic
# Requirements: ArcGIS Desktop Standard
# ----------------------------------------------------------------------------

import arcpy
import sys
import traceback
import TestUtilities
import os


try:

    print("Setting environment...")
    arcpy.ImportToolbox(TestUtilities.toolbox, "cadrg")
    arcpy.env.overwriteOutput = True

    # Set tool param variables
    print("Setting inputs...")
    targetGeodatabase = TestUtilities.scratchGDB
    targetMosaicName = "cadrgMD"
    coordinateSystem = arcpy.SpatialReference(4326)
    dataPath = TestUtilities.cadrgSourcePath
    dataFilter = "*.*"
    #Testing CADRG/ECRG tool
    arcpy.AddMessage("Starting Test: CADRB/ECRG Mosaic")
    # cadrgecrg_cadrg (workspace, md_name, spref, {datapath}, {datafilter}, {useoview}, {ovscale}, {psValue})
    arcpy.cadrgecrg_cadrg(targetGeodatabase, targetMosaicName, coordinateSystem, dataPath, dataFilter)

    # #Verify Results
    print("Verifying results...")
    countFootprints = int(arcpy.GetCount_management(os.path.join(targetGeodatabase, targetMosaicName)).getOutput(0))
    print("Footprint count: " + str(countFootprints))

    if (countFootprints < 3):
        print("ERROR: Less than 3 footprints! (found " + str(countFootprints) + ")")
        raise Exception("Test Failed")
    else:
        print("Test Passed")
        if arcpy.Exists(os.path.join(targetGeodatabase, targetMosaicName)):
            arcpy.Delete_management(os.path.join(targetGeodatabase, targetMosaicName))


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

        