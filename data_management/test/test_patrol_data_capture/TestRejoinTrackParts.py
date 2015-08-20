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
# TestRejoinTrackParts.py
# Description: Automatic Test of GP script/toolbox
# Requirements: ArcGIS Desktop Standard
# -----------------------------------------------------------------------------

import arcpy
import os
import sys
import traceback
import TestUtilities

def UniquePointGUIDs(pointFC,guidFieldName):
    countPointGUIDs = 0
    freqTable = os.path.join(TestUtilities.scratchGDB, "freqTable")
    arcpy.Frequency_analysis(pointFC, freqTable, guidFieldName)
    countPointGUIDs = int(arcpy.GetCount_management(freqTable).getOutput(0))
    arcpy.Delete_management(freqTable)
    return countPointGUIDs

def RunTest():
    try:
        print("Starting Test: TestRejoinTrackParts")
        print("Setting up inputs and environment...")
        inputLinesFC =  os.path.join(TestUtilities.outputGDB, "TrackLines")
        inputSeparatedPointsFC =  os.path.join(TestUtilities.outputGDB, "SeparatedGPSData")
        arcpy.env.overwriteOutput = True
        arcpy.ImportToolbox(TestUtilities.toolbox, "pdc")
        trackIDField = "TrackGUID"
        startDateTimeField = "StartDateTime"
        finishDateTimeField = "FinishDateTime"
        dateTimeField = "Date_Time"

        # How many tracks before joining?
        beforeTrackCount = int(arcpy.GetCount_management(inputLinesFC).getOutput(0))
        print("Number of tracks before joining: " + str(beforeTrackCount))
        beforePointCount = UniquePointGUIDs(inputSeparatedPointsFC,trackIDField)
        print("Number of unique track GUIDs in points before joining: " + str(beforePointCount))

        print("Selecting 4 tracks to join (OIDs: 2,3,4,5)...")
        arcpy.MakeFeatureLayer_management(inputLinesFC, "inputLinesFC")
        selectionType = "NEW_SELECTION"
        expression = "OBJECTID = 2 OR OBJECTID = 3 OR OBJECTID = 4 OR OBJECTID = 5"
        arcpy.SelectLayerByAttribute_management("inputLinesFC", selectionType, expression)

        print("Executing RejoinTrackParts_pdc...")
        ########################################################
        # Execute the Model under test:
        # RejoinTrackParts_pdc (TrackLines, SeparatedGPSData, Track_ID_Field, Start_DateTime_Field, Finish_DateTime_Field, DateTime_Field) 
        arcpy.RejoinTrackParts_pdc ("inputLinesFC", inputSeparatedPointsFC, trackIDField, startDateTimeField, finishDateTimeField, dateTimeField) 
        ########################################################

        # Verify the results
        afterTrackCount = int(arcpy.GetCount_management(inputLinesFC).getOutput(0))
        afterPointCount = UniquePointGUIDs(inputSeparatedPointsFC,trackIDField)

        if (beforeTrackCount == afterTrackCount):
            print("ERROR: Before track count (" + str(beforeTrackCount) + ") is the same as after track count (" + str(afterTrackCount) + "). No track joined.")
            raise Exception("Test Failed")
        elif (beforePointCount == afterPointCount):
            print("ERROR: Before gps point GUID count (" + str(beforePointCount) + ") is the same as afterwards (" + str(afterPointCount) + "). Expecting fewer GUIDs.")
            print("Track lines before: " + str(beforeTrackCount))
            print("Track lines after: " + str(afterTrackCount))
            raise Exception("Test Failed")
        elif (beforeTrackCount < afterTrackCount):
            print("ERROR: Found " + str(afterTrackCount) + " tracks after joining. Expected fewer than " + str(beforeTrackCount) + ".")
            raise Exception("Test Failed")
        elif (beforePointCount < afterPointCount):
            print("ERROR: Found " + str(afterPointCount) + " gps GUIDs points after joining. Expected fewer than " + str(beforePointCount) + ".")
            print("Track lines before: " + str(beforeTrackCount))
            print("Track lines after: " + str(afterTrackCount))
            raise Exception("Test Failed")
        else:
            print("Test Successful")
            print("Track lines before: " + str(beforeTrackCount))
            print("Track lines after: " + str(afterTrackCount))


    except arcpy.ExecuteError:
        # Get the tool error messages
        msgs = arcpy.GetMessages()
        arcpy.AddError(msgs)

        # return a system error code
        sys.exit(-1)

    except Exception as e:
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]

        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

        # Return python error messages for use in script tool or Python Window
        arcpy.AddError(pymsg)
        arcpy.AddError(msgs)

        # return a system error code
        sys.exit(-1)

RunTest()