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

import logging
import arcpy
from arcpy.sa import *
import sys
import traceback
import os

sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import Configuration
import UnitTestUtilities
import DataDownload
import arcpyAssert

class DistanceToAssetsCodeAssetsToBasesTestCase(unittest.TestCase):
    toolboxUnderTest = None # Set to Pro or ArcMap toolbox at runtime

    scratchGDB = None
    def setUp(self):
        if Configuration.DEBUG == True: print("         DistanceToAssetsTestCase.setUp")

        ''' Initialization needed if running Test Case standalone '''
        Configuration.GetLogger()
        Configuration.GetPlatform()
        ''' End standalone initialization '''
        self.toolboxUnderTest = Configuration.distancetoAssetsToolboxPath + \
            Configuration.GetToolboxSuffix()

        self.suffix = Configuration.GetToolboxSuffix()
        UnitTestUtilities.checkArcPy()
        DataDownload.runDataDownload(Configuration.distanceToAssetsDataPath, \
           Configuration.distanceToAssetsInputGDB, Configuration.distanceToAssetsURL)

        self.inputLocator = os.path.join(Configuration.distanceToAssetsDataPath, r"DistanceToAssetsTestData\Sample Locations\arcgisonline\World.GeocodeServer")


        if (self.scratchGDB == None) or (not arcpy.Exists(self.scratchGDB)):
            self.scratchGDB = UnitTestUtilities.createScratch(Configuration.distanceToAssetsDataPath)


        UnitTestUtilities.checkFilePaths([Configuration.distanceToAssetsDataPath])

        UnitTestUtilities.checkGeoObjects([Configuration.distanceToAssetsInputGDB, self.toolboxUnderTest, self.scratchGDB, self.inputLocator])

    def tearDown(self):
        if Configuration.DEBUG == True: print("         DistanceToAssets.tearDown")
        UnitTestUtilities.deleteScratch(self.scratchGDB)

    def testCodeAssetsToBases(self):
        if Configuration.DEBUG == True:print(".....DistanceToAssetsCodeAssetsToBasesTestCase.testCodeAssetsToBases")
        print("Importing toolbox...")
        arcpy.ImportToolbox(self.toolboxUnderTest)
        arcpy.env.overwriteOutput = True

        #arcpy.SignInToPortal_server("PatrickHSolutions", "IlmbgK!1", "http://www.arcgis.com")


        newAssets = os.path.join(Configuration.distanceToAssetsDataPath, "DistanceToAssetsTestData/Sample Locations/Assets_SF.csv")
        assetMapping = "Address Street VISIBLE NONE;Address2 <None> VISIBLE NONE;Address3 <None> VISIBLE NONE;Neighborhood <None> VISIBLE NONE;City City VISIBLE NONE;Subregion City VISIBLE NONE;Region State VISIBLE NONE;Postal ZIP VISIBLE NONE;'Postal Extension' <None> VISIBLE NONE;Country Country VISIBLE NONE"
        newBases = os.path.join(Configuration.distanceToAssetsDataPath, "DistanceToAssetsTestData/Sample Locations/Bases_SF.csv")
        baseMapping = "Address Street VISIBLE NONE;Address2 <None> VISIBLE NONE;Address3 <None> VISIBLE NONE;Neighborhood <None> VISIBLE NONE;City City VISIBLE NONE;Subregion City VISIBLE NONE;Region State VISIBLE NONE;Postal ZIP VISIBLE NONE;'Postal Extension' <None> VISIBLE NONE;Country <None> VISIBLE NONE"
        outAssets = os.path.join(self.scratchGDB, "geocodedassets")
        outBases = os.path.join(self.scratchGDB, "geocodedbases")


        arcpy.GeocodeAssetsAndBases_DistanceToAssets(self.inputLocator,newAssets,assetMapping,newBases,baseMapping,outAssets,outBases)

        result1 = arcpy.GetCount_management(outAssets)
        count1 = int(result1.getOutput(0))
        result2 = arcpy.GetCount_management(outBases)
        count2 = int(result2.getOutput(0))

        self.assertGreater(count1, 0)
        self.assertGreater(count2, 0)

        assetsNotGeocoded = os.path.join(Configuration.distanceToAssetsDataPath, "DistanceToAssetsTestData/Sample Locations/AssetsNotGeocoded.shp")
        basesNotGeocoded = os.path.join(Configuration.distanceToAssetsDataPath, "DistanceToAssetsTestData/Sample Locations/BasesNotGeocoded.shp")

        if(self.suffix == "_pro.tbx"):
            arcpy.Delete_management(assetsNotGeocoded)
            arcpy.Delete_management(basesNotGeocoded)

