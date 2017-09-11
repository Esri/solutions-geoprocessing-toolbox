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

class DistanceToAssetsSummarizeTestCase(unittest.TestCase):
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


        if (self.scratchGDB == None) or (not arcpy.Exists(self.scratchGDB)):
            self.scratchGDB = UnitTestUtilities.createScratch(Configuration.distanceToAssetsDataPath)


        UnitTestUtilities.checkFilePaths([Configuration.distanceToAssetsDataPath])

        UnitTestUtilities.checkGeoObjects([Configuration.distanceToAssetsInputGDB, self.toolboxUnderTest, self.scratchGDB])

    def tearDown(self):
        if Configuration.DEBUG == True: print("         DistanceToAssets.tearDown")
        UnitTestUtilities.deleteScratch(self.scratchGDB)

    def testSummarize(self):
        if Configuration.DEBUG == True:print(".....DistanceToAssetsSummarizeTestCase.testSummarize")
        print("Importing toolbox...")
        arcpy.ImportToolbox(self.toolboxUnderTest)
        arcpy.env.overwriteOutput = True

        mergedRoutesOut = os.path.join(self.scratchGDB, "Assets_To_Base_All")
        distStatsOut = os.path.join(self.scratchGDB, "Distances_by_Base")

        arcpy.Model1_DistanceToAssets(mergedRoutesOut, distStatsOut, Configuration.distanceToAssetsInputGDB)

        result1 = arcpy.GetCount_management(mergedRoutesOut)
        count1 = int(result1.getOutput(0))
        self.assertGreater(count1, 0)