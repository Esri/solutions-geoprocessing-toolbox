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
# TestAppendTrackstoDB.py
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
        print("Starting Test: TestAppendTrackstoDB")
        print("Setting up inputs and environment...")
        inputLinesFC =  os.path.join(TestUtilities.outputGDB, "TrackLines")
        inputPointsFC = os.path.join(TestUtilities.outputGDB, "SeparatedGPSData")
        print("Setting up targetPoints...")
        arcpy.env.overwriteOutput = True
        arcpy.ImportToolbox(TestUtilities.toolbox, "pdc")
        targetTrackPoints = os.path.join(TestUtilities.scratchGDB, "targetPoints")
        arcpy.CreateFeatureclass_management(TestUtilities.scratchGDB, os.path.basename(targetTrackPoints), "POINT",
                                                                inputPointsFC, "SAME_AS_TEMPLATE", "SAME_AS_TEMPLATE",
                                                                arcpy.Describe(inputPointsFC).spatialReference)
        print("Setting up targetLines...")
        targetTrackLines = os.path.join(TestUtilities.scratchGDB, "targetLines")
        arcpy.CreateFeatureclass_management(TestUtilities.scratchGDB, os.path.basename(targetTrackLines), "POLYLINE",
                                                                inputLinesFC, "SAME_AS_TEMPLATE", "SAME_AS_TEMPLATE",
                                                                arcpy.Describe(inputLinesFC).spatialReference)

        # How many rows before joining?
        beforeSourcePointRowCount = int(arcpy.GetCount_management(inputPointsFC).getOutput(0))
        print("Number of rows in source points before: " + str(beforeSourcePointRowCount))
        beforeSourceLineRowCount = int(arcpy.GetCount_management(inputLinesFC).getOutput(0))
        print("Number of rows in source lines before: " + str(beforeSourceLineRowCount))
        beforeTargetPointRowCount = int(arcpy.GetCount_management(targetTrackPoints).getOutput(0))
        print("Number of rows in target points before: " + str(beforeTargetPointRowCount))
        beforeTargetLineRowCount = int(arcpy.GetCount_management(targetTrackLines).getOutput(0))
        print("Number of rows in target lines before: " + str(beforeTargetLineRowCount))

        print("running AppendTrackstoDB_pdc...")
        ########################################################
        # Execute the Model under test:
        # AppendTrackstoDB_pdc (SeparatedGPSData, TrackLines, Patrol_Track_Points, PatrolTracks) 
        arcpy.AppendTrackstoDB_pdc(inputPointsFC, inputLinesFC, targetTrackPoints, targetTrackLines) 
        ########################################################

        print("Verify the results...")
        afterTargetPointRowCount = int(arcpy.GetCount_management(targetTrackPoints).getOutput(0))
        afterTargetLineRowCount = int(arcpy.GetCount_management(targetTrackLines).getOutput(0))

        if not (afterTargetPointRowCount == beforeSourcePointRowCount):
            print("ERROR: Target point rows don't match source point rows:  source " + \
                  str(beforeSourcePointRowCount) + ", target: " + str(afterTargetPointRowCount))
            raise Exception("Test Failed")
        elif not (afterTargetLineRowCount == beforeSourceLineRowCount):
            print("ERROR: Target line rows don't match source line rows: source" + \
                  str(beforeSourceLineRowCount) + ", target: " + str(afterTargetLineRowCount))
            raise Exception("Test Failed")
        else:
            print("Test Successful")
            print("Number of rows in target points after: " + str(afterTargetPointRowCount))
            print("Number of rows in target lines after: " + str(afterTargetLineRowCount))
            print("Deleteing target datasets...")
            arcpy.Delete_management(targetTrackPoints)
            arcpy.Delete_management(targetTrackLines)

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