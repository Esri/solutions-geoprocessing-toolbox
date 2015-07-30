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
# -----------------------------------------------------------------------------
# TestPointOfOrigin.py
# Description: Test Point Of Origin Toolbox
# Requirements: ArcGIS Desktop Standard
# ----------------------------------------------------------------------------
# history:
# 4/2/2015 - mf - update for Python 3 coding standards
# ==================================================


import arcpy
import sys
import traceback
import TestUtilities
import os

class LicenseError(Exception):
    pass


def main():
    ''' main test method '''
    try:        
        arcpy.ImportToolbox(TestUtilities.toolbox)
        arcpy.env.overwriteOutput = True

        # Set tool param variables
        inputImpactPoints = os.path.join(TestUtilities.testDataGDB, "impact_pts_monterey_UTM10N")
        inputWeaponsTable = os.path.join(TestUtilities.toolDataGDB, r"Weapons")
        inModelField = 'Model'
        inMinRangeField = 'Minimum_range'
        inMaxRangeField = 'Maximum_range'
        
        inputWeaponsAsString = ("'M120/121 120-mm American Mortar';'M224 60-mm American Mortar';'M252 81-mm American Mortar'")
        print("inputWeaponsAsString: " + str(inputWeaponsAsString))
        inputWeaponsAsList = inputWeaponsAsString.split(";")
        print("inputWeaponsAsList: " + str(inputWeaponsAsList))
        outputWorkspace = arcpy.env.scratchGDB
        outImpactPrefix = r"imp"
        outPooPrefix = r"poo"
        outRangePrefix = r"rng"

        # WGS_1984_UTM_Zone_10N using factoryCode
        sr = arcpy.SpatialReference(32610)

        # Testing Point Of Origin Site Detection
        arcpy.AddMessage("Starting Test: Point of Origin Site Detection")
        results = arcpy.PointOfOriginSiteDetection_ptorigin(inputImpactPoints, inputWeaponsTable,
                                                            inModelField, inMinRangeField, inMaxRangeField,
                                                            inputWeaponsAsString, outputWorkspace,
                                                            outImpactPrefix, outPooPrefix,
                                                            outRangePrefix, sr)

        # print("results.outputCount: " + str(results.outputCount))
        # for i in range(0,results.outputCount):
        #     print("output " + str(i) + ": " + str(results.getOutput(i)))

        # Verify Results
        print("Checking results...")
        outImpactFeatures = results.getOutput(0)
        outPOOFeatures = results.getOutput(1).split(";")
        outRangeFeatures = results.getOutput(2).split(";")

        # check that the same number of impact points between the input and output
        countInputImpactPoints = int(arcpy.GetCount_management(inputImpactPoints).getOutput(0))
        countOutputImpactPoints = int(arcpy.GetCount_management(outImpactFeatures).getOutput(0))
        if countInputImpactPoints != countOutputImpactPoints:
            print("Error: Impact points are not the same. In: " +
                  str(countInputImpactPoints) + ", Out: " +
                  str(countOutputImpactPoints))
            raise Exception("Test Failed")
        print("Number of input and output impact points match.")

        # check the number of combined POO feature classes returned by the tool
        countPOOFeatureClasses = int(len(outPOOFeatures))
        if len(inputWeaponsAsList) != countPOOFeatureClasses:
            print("""Error: Number of Output Point of Origin features do not match
                  number of selected weapon systems. # weaopns: """ +
                  str(len(inputWeaponsAsList)) + ", POO: " +
                  str(countPOOFeatureClasses))
            raise Exception("Test Failed")
        print("Number of selected weapons match number of output Point Of Origin features.")

        # check the number of range feature classes returned by the tool
        countImpactXWeapons = int(countInputImpactPoints * len(inputWeaponsAsList))
        countRangeFeatureClasses = int(len(outRangeFeatures))
        if countImpactXWeapons != countRangeFeatureClasses:
            print("""Error: Number of Range feature classes does not match Impact Points
                  x Weapon Models. ImpxWeap: """ +
                  str(countImpactXWeapons) + ", Ranges:" +
                  str(countRangeFeatureClasses))
            raise Exception("Test Failed")
        print("Number of Impacts x Weapons match output range features.")

        print("All tests passed.")


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

        # Concatenate information together concerning the error
        # into a message string
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
