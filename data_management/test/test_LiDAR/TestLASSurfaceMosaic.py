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
# TestLASSurfaceMosaic.py
# Description: Test Create Source LAS Surface Elevation Mosaic
# Requirements: ArcGIS Desktop Advanced
# ----------------------------------------------------------------------------

import arcpy
import sys
import traceback
import TestUtilities
import os


try:
    print("==============================================================================")
    print("IMPORTANT:")
    print("This is a time-consuming test and will take several minutes to complete.")
    print("The test may not update status, or show progress during this time.")
    print("==============================================================================")

    print("Setting environment...")
    arcpy.ImportToolbox(TestUtilities.toolbox, "LidarTools")
    arcpy.env.overwriteOutput = True

    # Set tool param variables
    print("Setting inputs...")
    targetGeodatabase = TestUtilities.scratchGDB
    targetMosaicName = "S_DSMGround"
    srWGS84 = arcpy.SpatialReference(4326) #GCS_WGS_1984
    srNAD83StatePlaneCA4Ft = arcpy.SpatialReference(2228) #NAD_1983_StatePlane_California_IV_FIPS_0404_Feet
    coordinateSystem = srNAD83StatePlaneCA4Ft
    #rasterType = "LAS"
    rasterType = "#"
    dataPath = TestUtilities.lasSourcePath

    arcpy.AddMessage("Starting Test: Create Source LAS Surface Elevation Mosaic (" + str(datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S")) + ")")
    # CreateSourceLASSurfaceElevationMosaic_elevationmosaics (Target_Geodatabase, Source_Elevation_Mosaic_Dataset_Name,
    # Coordinate_System, Raster_Type,
    # Input_LAS_Files, {Coordinate_System_for_Input_Data})
    arcpy.CreateSourceLASSurfaceElevationMosaic_LidarTools(targetGeodatabase, targetMosaicName, coordinateSystem,
                                                           rasterType, dataPath)

    arcpy.AddMessage("Finished running tool (" + str(datetime.datetime.now().strftime("%m/%d/%Y %H:%M:%S") + ")"))
    # #Verify Results
    print("Verifying results...")
    countFootprints = int(arcpy.GetCount_management(os.path.join(targetGeodatabase, targetMosaicName)).getOutput(0))
    print("Footprint count: " + str(countFootprints))

    if not countFootprints == 5:
        print("ERROR: Expected five (5) footprints, found " + str(countFootprints))
        raise Exception("Test Failed")

    #Check for two 'primary' and three 'overview' in the 'category' field
    #Frequency_analysis (in_table, out_table, frequency_fields, {summary_fields})
    tempFreqTable = os.path.join(TestUtilities.scratchGDB, "tempFreqTable")
    arcpy.Frequency_analysis(os.path.join(targetGeodatabase, targetMosaicName), tempFreqTable, "Category")
    freqTable = {}
    rows = arcpy.da.SearchCursor(tempFreqTable, ["Category", "FREQUENCY"])
    for row in rows:
        if row[0] == 1:
            category = "Primary"
        if row[0] == 2:
            category = "Overview"
        frequency = row[1]
        freqTable[category] = frequency
          
    fail = False
    if not freqTable["Primary"] == 2:
        print("ERROR: Expected two (2) Primary footprints, found " + str(freqTable["Primary"]))
        fail = True
    if not freqTable["Overview"] == 3:
        print("ERROR: Expected three (3) Overview footprints, found " + str(freqTable["Overview"]))
        fail = True
    if fail == True:
        raise Exception("Test Failed")
    else:
        print("Test Passed")

    if arcpy.Exists(os.path.join(targetGeodatabase, targetMosaicName)):
        arcpy.Delete_management(os.path.join(targetGeodatabase, targetMosaicName))
    if arcpy.Exists(tempFreqTable):
        arcpy.Delete_management(tempFreqTable)

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
