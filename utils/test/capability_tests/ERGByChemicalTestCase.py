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
ERGByChemicalTestCase.py
--------------------------------------------------
requirements:
author: ArcGIS Solutions
company: Esri
==================================================
Description: Unit test for the ERG By Placard

Includes the following tests:
* test_ERGByChemical_001
* test_ERGByChemical_002

==================================================
history:
11/09/2015 - MF - original coding
02/24/2017 - MF - update for new 2016 ERG chemical list
==================================================
'''

import arcpy
import os
import unittest
import Configuration
import UnitTestUtilities
from . import ERGTestUtils


class ERGByChemical(unittest.TestCase):
    ''' Test ERG By Chemical tool in the ERG Tools toolbox'''

    scratchGDB = None
    inputPoint = None

    tbxFolderPath = os.path.join(Configuration.repoPath, "capability", "toolboxes", "ERG Tools.pyt")
    testDataFolderPath = os.path.join(Configuration.capabilityPath, "data")

    def setUp(self):
        ''' set-up code '''
        if Configuration.DEBUG == True: print("         ERGByChemical.setUp")
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
        if Configuration.DEBUG == True: print("         ERGByChemical.tearDown")
        UnitTestUtilities.deleteScratch(self.scratchGDB)
        return

    def test_ERGByChemical_001(self):
        ''' test the tool '''
        if Configuration.DEBUG == True: print("         ERGByChemical.test_ERGByChemical_001")
        inputMaterialType = "Allylamine"
        inputWindBearing = 10
        inputDayOrNight = "Day"
        inputLargeOrSmall = "Large"
        countAreas, countLines = self.ERGByChemical(inputMaterialType, inputWindBearing,
                                                    inputDayOrNight, inputLargeOrSmall)
        self.assertEqual(countAreas, int(3))
        self.assertEqual(countLines, int(3))
        return

    def test_ERGByChemical_002(self):
        ''' test the tool '''
        if Configuration.DEBUG == True: print("         ERGByChemical.test_ERGByChemical_002")
        inputMaterialType = "Allylamine"
        inputWindBearing = 130
        inputDayOrNight = "Night"
        inputLargeOrSmall = "Small"
        countAreas, countLines = self.ERGByChemical(inputMaterialType, inputWindBearing,
                                                    inputDayOrNight, inputLargeOrSmall)
        self.assertEqual(countAreas, int(3))
        self.assertEqual(countLines, int(3))
        return

    def test_ERGByChemical_003(self):
        ''' test the tool '''
        if Configuration.DEBUG == True: print("         ERGByChemical.test_ERGByChemical_003")
        inputMaterialType = "GB (Weaponized Sarin)"
        inputWindBearing = 250
        inputDayOrNight = "Night"
        inputLargeOrSmall = "Large"
        countAreas, countLines = self.ERGByChemical(inputMaterialType, inputWindBearing,
                                                    inputDayOrNight, inputLargeOrSmall)
        self.assertEqual(countAreas, int(3))
        self.assertEqual(countLines, int(3))
        return

    def ERGByChemical(self, inputMaterialType, inputWindBearing, inputDayOrNight, inputLargeOrSmall):
        ''' Test the supporting script tool '''
        if Configuration.DEBUG == True:
            print("         ERGByChemical.test_ERGByChemical")
        else:
            print("Testing ERG By Chemical...")

        # Testing ERG By Placard
        outputERGAreas = os.path.join(self.scratchGDB, "ERGAreasChemical")
        outputERGLines = os.path.join(self.scratchGDB, "ERGLinesChemical")
        outputERGAreas, outputERGLines = arcpy.ERGByChemical_erg(self.inputPoint, inputMaterialType,
                                                                 inputWindBearing, inputDayOrNight,
                                                                 inputLargeOrSmall, outputERGAreas,
                                                                 outputERGLines)

        # Verify Results
        countAreas = int(arcpy.GetCount_management(outputERGAreas).getOutput(0))
        countLines = int(arcpy.GetCount_management(outputERGLines).getOutput(0))

        return [countAreas, countLines]
