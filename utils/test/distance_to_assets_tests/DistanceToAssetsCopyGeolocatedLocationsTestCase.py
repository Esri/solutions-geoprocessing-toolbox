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

class DistanceToAssetsCopyGeolocatedLocationsTestCase(unittest.TestCase, arcpyAssert.FeatureClassAssertMixin):
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

        UnitTestUtilities.checkArcPy()
        DataDownload.runDataDownload(Configuration.distanceToAssetsDataPath, \
           Configuration.distanceToAssetsInputGDB, Configuration.distanceToAssetsURL)

        self.inputAssets = os.path.join(Configuration.distanceToAssetsInputGDB, "AssetsGeocoded")
        self.inputBases = os.path.join(Configuration.distanceToAssetsInputGDB, "BasesGeocoded")

        if (self.scratchGDB == None) or (not arcpy.Exists(self.scratchGDB)):
            self.scratchGDB = UnitTestUtilities.createScratch(Configuration.distanceToAssetsDataPath)

        self.suffix = Configuration.GetToolboxSuffix()
        UnitTestUtilities.checkFilePaths([Configuration.distanceToAssetsDataPath])

        UnitTestUtilities.checkGeoObjects([Configuration.distanceToAssetsInputGDB, self.toolboxUnderTest, self.scratchGDB, self.inputAssets, self.inputBases])

    def tearDown(self):
        if Configuration.DEBUG == True: print("         DistanceToAssets.tearDown")
        UnitTestUtilities.deleteScratch(self.scratchGDB)

    def testCopyGeolocatedLocations(self):
        if Configuration.DEBUG == True:print(".....DistanceToAssetsCopyGeolocatedLocationsTestCase.testCopyGeolocatedLocations")
        print("Importing toolbox...")
        arcpy.ImportToolbox(self.toolboxUnderTest)
        arcpy.env.overwriteOutput = True


        outputGoldAssets = os.path.join(self.scratchGDB, "GoldCopyAssets")
        outputGoldBases = os.path.join(self.scratchGDB, "GoldCopyBases")

        arcpy.CopyGeocodedLocations_DistanceToAssets(self.inputAssets, outputGoldAssets, self.inputBases, outputGoldBases)
        result1 = arcpy.GetCount_management(outputGoldAssets)
        count1 = int(result1.getOutput(0))
        result2 = arcpy.GetCount_management(outputGoldBases)
        count2 = int(result2.getOutput(0))
        self.assertGreater(count1, 0)
        self.assertGreater(count2, 0)

        goldAssetsTemplatePro = os.path.join(Configuration.distanceToAssetsInputGDB, "GoldCopyAssets_pro")
        goldBasesTemplatePro = os.path.join(Configuration.distanceToAssetsInputGDB, "GoldCopyBases_pro")
        goldAssetsTemplateAm = os.path.join(Configuration.distanceToAssetsInputGDB, "GoldCopyAssets_am")
        goldBasesTemplateAm = os.path.join(Configuration.distanceToAssetsInputGDB, "GoldCopyBases_am")

        if (self.suffix == "_pro.tbx"):
            self.assertFeatureClassEqual(outputGoldAssets, goldAssetsTemplatePro, "OBJECTID")
            self.assertFeatureClassEqual(outputGoldBases, goldBasesTemplatePro, "OBJECTID")
        else:
            self.assertFeatureClassEqual(outputGoldAssets, goldAssetsTemplateAm, "OBJECTID")
            self.assertFeatureClassEqual(outputGoldBases, goldBasesTemplateAm, "OBJECTID")

