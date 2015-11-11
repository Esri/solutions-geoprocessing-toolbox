# coding: utf-8
'''
-----------------------------------------------------------------------------
Copyright 2015 Esri
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-----------------------------------------------------------------------------

==================================================
ERGByPlacardTestCase.py
--------------------------------------------------
requirements:
author: ArcGIS Solutions
company: Esri
==================================================
Description: Unit test for the ERG By Placard

Includes the following tests:


==================================================
history:
11/09/2015 - MF - original coding
==================================================
'''

import arcpy
import os
import unittest
import TestUtilities
import UnitTestUtilities
from . import ERGTestUtils


class ERGByPlacard(unittest.TestCase):
    ''' Test ERG By Placard tool in the ERG Tools toolbox'''

    scratchGDB = None
    inputPoint = None

    tbxFolderPath = os.path.join(TestUtilities.repoPath, "capability", "toolboxes", "ERG Tools.pyt")
    testDataFolderPath = os.path.join(TestUtilities.capabilityPath, "data")

    def setUp(self):
        ''' set-up code '''
        if TestUtilities.DEBUG == True: print("         ERGByPlacard.setUp")
        UnitTestUtilities.checkArcPy()
        UnitTestUtilities.checkFilePaths([self.testDataFolderPath,
                                          self.tbxFolderPath])

        # Import the toolbox
        arcpy.ImportToolbox(self.tbxFolderPath, "erg")

        # Check the test inputs (do they exist? or not?)
        if (self.scratchGDB == None) or (not arcpy.Exists(self.scratchGDB)):
            self.scratchGDB = UnitTestUtilities.createScratch(self.testDataFolderPath)

        # Setup the test inputs
        self.inputPoint = ERGTestUtils.getInputPointFC()
        UnitTestUtilities.checkGeoObjects([self.inputPoint])

        return

    def tearDown(self):
        ''' clean up after tests'''
        if TestUtilities.DEBUG == True: print("         ERGByPlacard.tearDown")
        UnitTestUtilities.deleteScratch(self.scratchGDB)
        return

    def test_ERGByPlacard_001(self):
        ''' test the tool with basic inputs'''
        if TestUtilities.DEBUG == True: print("         ERGByPlacard.test_ERGByPlacard_001")
        inputPlacardID = 1560
        inputWindBearing = 10
        inputDayOrNight = "Day"
        inputLargeOrSmall = "Large"
        countAreas, countLines = self.ERGByPlacard(inputPlacardID,
                                                   inputWindBearing,
                                                   inputDayOrNight,
                                                   inputLargeOrSmall)

        self.assertEqual(countAreas, int(3))
        self.assertEqual(countLines, int(3))
        return

    def test_ERGByPlacard_002(self):
        ''' test the tool with basic inputs'''
        if TestUtilities.DEBUG == True: print("         ERGByPlacard.test_ERGByPlacard_002")
        inputPlacardID = 1560
        inputWindBearing = 130
        inputDayOrNight = "Night"
        inputLargeOrSmall = "Small"
        countAreas, countLines = self.ERGByPlacard(inputPlacardID,
                                                   inputWindBearing,
                                                   inputDayOrNight,
                                                   inputLargeOrSmall)

        self.assertEqual(countAreas, int(3))
        self.assertEqual(countLines, int(3))
        return

    def ERGByPlacard(self, inputPlacardID, inputWindBearing, inputDayOrNight, inputLargeOrSmall):
        ''' Main ERG By Placard test '''
        if TestUtilities.DEBUG == True:
            print("         ERGByPlacard.ERGByPlacard")
        else:
            print("Testing ERG By Placard...")

        # Testing ERG By Placard
        outputERGAreas = os.path.join(self.scratchGDB, "ERGAreasPlacard")
        outputERGLines = os.path.join(self.scratchGDB, "ERGLinesPlacard")
        outputERGAreas, outputERGLines = arcpy.ERGByPlacard_erg(self.inputPoint, inputPlacardID,
                                                                inputWindBearing, inputDayOrNight,
                                                                inputLargeOrSmall, outputERGAreas,
                                                                outputERGLines)

        # Verify Results
        countAreas = int(arcpy.GetCount_management(outputERGAreas).getOutput(0))
        countLines = int(arcpy.GetCount_management(outputERGLines).getOutput(0))

        return [countAreas, countLines]
