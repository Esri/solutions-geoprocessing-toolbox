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
# TestImportPatrolRpt.py
# Description: Automatic Test of GP script/toolbox
# Requirements: ArcGIS Desktop Standard
# -----------------------------------------------------------------------------

import arcpy
import os
import sys
import traceback
import TestUtilities

def RunTest():
    try:
        print("Starting Test: TestImportPatrolRpt")
        print("Setting up inputs and environment...")
        inputLinesFC =  os.path.join(TestUtilities.outputGDB, "TrackLines")
        inputPatrolReportTable = os.path.join(TestUtilities.patrolReportTable)
        inputEnemySightingsTable = os.path.join(TestUtilities.enemySightingsTable)
        xmlPatrolReport = os.path.join(TestUtilities.xmlPatrolReport)
        arcpy.env.overwriteOutput = True
        arcpy.ImportToolbox(TestUtilities.toolbox, "pdc")

        # How many rows before joining?
        beforePRRowCount = int(arcpy.GetCount_management(inputPatrolReportTable).getOutput(0))
        print("Number of rows in Patrol Report Table before: " + str(beforePRRowCount))
        beforeESRowCount = int(arcpy.GetCount_management(inputEnemySightingsTable).getOutput(0))
        print("Number of rows in Enemy Sightings Table before: " + str(beforeESRowCount))

        print("Selecting track OBJECTID = 2 for report...")
        arcpy.MakeFeatureLayer_management(inputLinesFC, "inputLinesFC_layer")
        selectionType = "NEW_SELECTION"
        expression = "OBJECTID = 2"
        arcpy.SelectLayerByAttribute_management("inputLinesFC_layer", selectionType, expression)
        tempInputTracks = os.path.join(TestUtilities.scratchGDB,"tracks")
        arcpy.CopyFeatures_management("inputLinesFC_layer",tempInputTracks)
        print("Input features have " + str(arcpy.GetCount_management(tempInputTracks).getOutput(0)) + " rows")

        print("Checking input field type...")
        trackIDFieldName = "TrackGUID"
        trackIDField = None
        fields = arcpy.ListFields(tempInputTracks,trackIDFieldName)
        for field in fields:
            trackIDField = field


        print("Executing ImportPatrolReport_pdc...")
        import types
        print("trackIDField python type: " + str(type(trackIDField)))
        print("trackIDField.type: " + str(trackIDField.type))
        print("trackIDField.name: " + str(trackIDField.name))
        ########################################################
        # Execute the Model under test:
        # ImportPatrolReport_pdc (Track_Lines, Track_ID_Field, Infopath_Patrol_Report_XML, PatrolReport_Table, EnemySightings_Table)
        arcpy.ImportPatrolReport_pdc(tempInputTracks, trackIDField.name, xmlPatrolReport, inputPatrolReportTable, inputEnemySightingsTable)
        ########################################################

        print("Verify the results...")
        afterPRRowCount = int(arcpy.GetCount_management(inputPatrolReportTable).getOutput(0))
        afterESRowCount = int(arcpy.GetCount_management(inputEnemySightingsTable).getOutput(0))

        if not (afterPRRowCount > beforePRRowCount):
            print("ERROR: Patrol Report rows before: " + str(beforePRRowCount) + ", after: " + str(afterPRRowCount))
            raise Exception("Test Failed")
        elif not (afterESRowCount > beforeESRowCount):
            print("ERROR: Enemy Sightings rows before: " + str(beforeESRowCount) + ", after: " + str(afterESRowCount))
            raise Exception("Test Failed")
        else:
            print("Test Successful")
            print("Number of rows in Patrol Report Table after: " + str(afterPRRowCount))
            print("Number of rows in Enemy Sightings Table after: " + str(afterESRowCount))

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
        print(pymsg)
        arcpy.AddError(msgs)
        print(msgs)

        # return a system error code
        sys.exit(-1)

RunTest()