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
# TestPointOfOrigin.py
# Description: Test Point Of Origin Toolbox
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
    inputImpactPoints = os.path.join(TestUtilities.testDataGDB,r"impacts")
    inputWeaponsTable = os.path.join(TestUtilities.toolDataGDB,r"Weapons")
    inputWeaponsAsString = "82mm Soviet Mortar; 88mm American Mortar; 120mm American Mortar"
    inputWeaponsAsList = inputWeaponsAsString.split(";")
    outputWorkspace = arcpy.env.scratchGDB
    outImpactPrefix = r"imp"
    outPooPrefix = r"poo"
    outRangePrefix = r"rng"
    sr = arcpy.spatialReference(32642) #WGS_1984_UTM_Zone_42N using factoryCode
    
    #Testing Point Of Origin Site Detection
    arcpy.AddMessage("Starting Test: Point of Origin Site Detection")
    results = arcpy.PointOfOriginSiteDetection_ptorigin(inputImpactPoints, InputWeaponsTable,
                                              inputWeaponsAsString, outputWorkspace,
                                              outImpactPrefix,outPooPrefix,
                                              outRangePrefix,sr)
    outImpactFeatures = results.getOutput[0]
    outPOOFeatures = results.getOutput[1].split(";")
    outRangeFeatures = results.getOutput[2].split(";")
    
    #Verify Results
    countInputImpactPoints = int(arcpy.GetCount_management(inputImpactPoints).getOutput(0))
    countOutputImpactPoints = int(arcpy.GetCount_management(outImpactFeatures).getOutput(0))
    if (countInputImpactPoints != countOutputImpactPOints):
        print("Error: Impact points are not the same. In: " + str(countInputImpactPoints) + ", Out: " + str(countOutputImpactPoints))
        raise Exception("Test Failed")
    
    countPOOFeatureClasses = int(len(outPOOFeatures))
    if (countInputImpactPoints != countPOOFeatureClasses):
        print("Error: Output Point Of Origin features are not the same as impact points. Impacts: " + str(countInputImpactPoints) + ", POO: " + str(countPOOFeatureClasses))
        raise Exception("Test Failed")
    
    countImpactXWeapons = int(countInputImpactPoints * len(inputWeaponsAsList))
    countRangeFeatureClasses = int(len(outRangeFeatures))
    if (countImpactXWeapons != countRangeFeatureClasses):
        print("Error: Number of Range feature classes does not match Impact Points x Weapon Models. ImpxWeap: " + str(countImpactXWeapons) + ", Ranges:" + str(countRangeFeatureClasses))
        raise Exception("Test Failed")
    
    print("Test Passed")


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