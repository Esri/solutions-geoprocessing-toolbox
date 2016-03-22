
# -----------------------------------------------------------------------------
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
# ----------------------------------------------------------------------------
# TestERGTools.py
# Description: Test ERG Tools Toolbox
# Requirements: ArcGIS Desktop Standard
# ----------------------------------------------------------------------------
# history:
# 4/2/2015 - mf - updates for coding standards and making tests as modules
# ==================================================



import arcpy
import sys
import traceback
import TestUtilities
import os


class LicenseError(Exception):
    pass


def testERGByChemical(inFS, inMatTy, inWB, inDN, inLS, outAreas, outLines):
    '''Testing ERG By Chemical'''
    arcpy.AddMessage("Starting Test: ERG Tools - ERG By Chemical")
    arcpy.ERGByChemical_erg(inFS, inMatTy, inWB, inDN, inLS, outAreas, outLines)
    return [outAreas, outLines]


def testERGByPlacard(inFS, inPID, inWB, inDN, inLS, outAreas, outLines):
    '''Testing ERG By Chemical'''
    arcpy.AddMessage("Starting Test: ERG Tools - ERG By Placard")
    arcpy.ERGByPlacard_erg(inFS, inPID, inWB, inDN, inLS, outAreas, outLines)
    return [outAreas, outLines]


def main():
    ''' Tool main code '''
    try:

        arcpy.ImportToolbox(TestUtilities.toolbox)
        arcpy.env.overwriteOutput = True

        # Set tool param variables
        inPoint = arcpy.Point(77.0, 38.9)
        inWGS84Point = arcpy.PointGeometry(inPoint)
        sr = arcpy.SpatialReference(4326) #GCS_WGS_1984
        inWGS84Point.spatial_reference = sr
        # create an in_memory feature class to initially contain the input point
        fc = arcpy.CreateFeatureclass_management("in_memory", "tempfc", "POINT",
                                                 None, "DISABLED", "DISABLED",
                                                 sr)[0]
        # open and insert cursor
        with arcpy.da.InsertCursor(fc, ["SHAPE@"]) as cursor:
            cursor.insertRow([inWGS84Point])
        # create a featureset object and load the fc
        inputFeatureSet = arcpy.FeatureSet()
        inputFeatureSet.load(fc)
        # set the remaining tool parameters
        inputMaterialType = "Allylamine"
        inputPlacardID = 1560
        inputWindBearing = 10
        inputDayOrNight = "Day"
        inputLargeOrSmall = "Large"
        outputERGAreas = os.path.join(arcpy.env.scratchGDB, "ERGAreas")
        outputERGLines = os.path.join(arcpy.env.scratchGDB, "ERGLines")

        # Testing ERG By Chemical
        outputERGAreas, outputERGLines = testERGByChemical(inputFeatureSet,
                                                           inputMaterialType,
                                                           inputWindBearing,
                                                           inputDayOrNight,
                                                           inputLargeOrSmall,
                                                           outputERGAreas,
                                                           outputERGLines)

        # Verify Results
        countAreas = int(arcpy.GetCount_management(outputERGAreas).getOutput(0))
        print("ERG Area count: " + str(countAreas))
        countLines = int(arcpy.GetCount_management(outputERGLines).getOutput(0))
        print("ERG Line count: " + str(countLines))
        if (countAreas != 3) or (countLines != 3):
            print("Invalid output count (there should be 3 areas and 3 lines)!")
            raise Exception("Test Failed")
        print("Test Passed")

        # Testing ERG By Placard
        outputERGAreas, outputERGLines = testERGByPlacard(inputFeatureSet,
                                                          inputPlacardID,
                                                          inputWindBearing,
                                                          inputDayOrNight,
                                                          inputLargeOrSmall,
                                                          outputERGAreas,
                                                          outputERGLines)

        # Verify Results
        countAreas = int(arcpy.GetCount_management(outputERGAreas).getOutput(0))
        print("ERG Area count: " + str(countAreas))
        countLines = int(arcpy.GetCount_management(outputERGLines).getOutput(0))
        print("ERG Line count: " + str(countLines))
        if (countAreas != 3) or (countLines != 3):
            print("Invalid output count (there should be 3 areas and 3 lines)!")
            raise Exception("Test Failed")
        print("Test Passed")

    except arcpy.ExecuteError:
        # Get the arcpy error messages
        msgs = arcpy.GetMessages()
        arcpy.AddError(msgs)
        print(msgs)

        # return a system error code
        sys.exit(-1)

    except:
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]

        # Concatenate information together concerning the error into a message string
        pymsg = ("PYTHON ERRORS:\nTraceback info:\n" + tbinfo +
                 "\nError Info:\n" + str(sys.exc_info()[1]))
        msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

        # Return python error messages for use in script tool or Python Window
        arcpy.AddError(pymsg)
        arcpy.AddError(msgs)

        # Print Python error messages for use in Python / Python Window
        print(pymsg + "\n")
        print(msgs)

        # return a system error code
        sys.exit(-1)


# MAIN =============================================
if __name__ == "__main__":
    main()
