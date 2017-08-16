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

class DistanceToAssetsRouteAssetsToBasesAGOLTestCase(unittest.TestCase, arcpyAssert.FeatureClassAssertMixin):
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

        self.suffix = Configuration.GetToolboxSuffix()

        self.inputAssets = os.path.join(Configuration.distanceToAssetsInputGDB, "AssetsGeocoded")
        self.inputBases = os.path.join(Configuration.distanceToAssetsInputGDB, "BasesGeocoded")
        self.inputAssetsPro = os.path.join(Configuration.distanceToAssetsInputGDB, "AssetsGeocoded_pro")
        self.inputBasesPro = os.path.join(Configuration.distanceToAssetsInputGDB, "BasesGeocoded_pro")

        if (self.scratchGDB == None) or (not arcpy.Exists(self.scratchGDB)):
            self.scratchGDB = UnitTestUtilities.createScratch(Configuration.distanceToAssetsDataPath)


        UnitTestUtilities.checkFilePaths([Configuration.distanceToAssetsDataPath])

        UnitTestUtilities.checkGeoObjects([Configuration.distanceToAssetsInputGDB, self.toolboxUnderTest, self.scratchGDB, self.inputAssets, self.inputBases])

    def tearDown(self):
        if Configuration.DEBUG == True: print("         DistanceToAssets.tearDown")
        UnitTestUtilities.deleteScratch(self.scratchGDB)

    def testRouteAssetsToBasesAGOL(self):
        if Configuration.DEBUG == True:print(".....DistanceToAssetsRouteAssetsToBasesAGOLTestCase.testRouteAssetsToBasesAGOL")
        print("Importing toolbox...")
        arcpy.ImportToolbox(self.toolboxUnderTest)
        arcpy.env.overwriteOutput = True

        if(self.suffix == "_pro.tbx"):
            arcpy.DistanceFromAssetToBase222_DistanceToAssets(self.inputAssetsPro, self.inputBasesPro)
        else:
            arcpy.DistanceFromAssetToBase222_DistanceToAssets(self.inputAssets, self.inputBases)

        assetsToBase1pro = os.path.join(Configuration.distanceToAssetsInputGDB, "Assets_to_Base_1" )
        assetsToBase2pro = os.path.join(Configuration.distanceToAssetsInputGDB, "Assets_to_Base_2" )
        assetsToBase1am = os.path.join(Configuration.distanceToAssetsOutputGDB, "Assets_to_Base_1" )
        assetsToBase2am = os.path.join(Configuration.distanceToAssetsOutputGDB, "Assets_to_Base_2" )

        if(self.suffix=="_pro.tbx"):

            result1 = arcpy.GetCount_management(assetsToBase1pro)
            count1 = int(result1.getOutput(0))
            result2 = arcpy.GetCount_management(assetsToBase2pro)
            count2 = int(result1.getOutput(0))
        else:
            result1 = arcpy.GetCount_management(assetsToBase1am)
            count1 = int(result1.getOutput(0))
            result2 = arcpy.GetCount_management(assetsToBase2am)
            count2 = int(result1.getOutput(0))

        self.assertEqual(count1, 1)
        self.assertEqual(count2, 1)

        assetsToBaseTemplate1am = os.path.join(Configuration.distanceToAssetsInputGDB, "Assets_to_Base_1_am")
        assetsToBaseTemplate1pro = os.path.join(Configuration.distanceToAssetsInputGDB, "Assets_to_Base_1_pro")

        if(self.suffix == "_pro.tbx"):
            self.assertFeatureClassEqual(assetsToBase1pro, assetsToBaseTemplate1pro, "OBJECTID")
        else:
            self.assertFeatureClassEqual(assetsToBase1am, assetsToBaseTemplate1am, "OBJECTID")