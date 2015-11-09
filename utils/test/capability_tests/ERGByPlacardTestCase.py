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


class ERGByPlacard(unittest.TestCase):
    ''' Test ERG By Placard tool in the ERG Tools toolbox'''

    scratchGDB = None

    tbxFolderPath = os.path.join(TestUtilities.repoPath, "capability", "toolboxes", "ERG Tools.pyt")
    testDataFolderPath = os.path.join(TestUtilities.capabilityPath, "data")

    # inputAirframeTable = None
    # inputSuitableAreas = None
    # inputSlope = None
    # outputGeodatabase = None
    # outputCenterpoints = None
    # outputCircles = None

    def setUp(self):
        ''' set-up code '''
        if TestUtilities.DEBUG == True: print("         ERGByPlacard.setUp")
        UnitTestUtilities.checkArcPy()
        UnitTestUtilities.checkFilePaths([self.testDataFolderPath,
                                          self.tbxFolderPath])

        self.testDataGeodatabase = os.path.join(self.testDataFolderPath, r"test_hlz_tools.gdb")

        # Check the test inputs (do they exist? or not?)
        if (self.scratchGDB == None) or (not arcpy.Exists(self.scratchGDB)):
            self.scratchGDB = UnitTestUtilities.createScratch(self.testDataFolderPath)

        # Setup the test inputs
        # self.inputAirframeTable = os.path.join(self.testDataGeodatabase, r"Aircraft_Specifications")
        # self.inputSuitableAreas = os.path.join(self.testDataGeodatabase, r"HLZSelectionArea")
        # self.inputSlope = os.path.join(self.testDataGeodatabase, r"SRTMPctSlope")
        # self.outputGeodatabase = os.path.join(self.scratchGDB)
        # self.outputCenterpoints = os.path.join(self.outputGeodatabase, r"centerPoints")
        # self.outputCircles = os.path.join(self.outputGeodatabase, r"tdCircles")
        
        

        UnitTestUtilities.checkGeoObjects([self.testDataGeodatabase,
                                           self.outputGeodatabase,
                                           self.inputAirframeTable,
                                           self.inputSuitableAreas,
                                           self.inputSlope])
        return

    def tearDown(self):
        ''' clean up after tests'''
        if TestUtilities.DEBUG == True: print("         ERGByPlacard.tearDown")
        UnitTestUtilities.deleteScratch(self.scratchGDB)
        return

    def test_ERGByPlacard(self):
        ''' test the tool '''
        if TestUtilities.DEBUG == True: print("         ERGByPlacard.test_ERGByPlacard")
        # check that the tool exists:
        #self.assertTrue(arcpy.Exists(os.path.join(self.tbxProFolderPath, r"MinimumBoundingFishnet")))
        self.MinimumBoundingFishnet(self.tbxProFolderPath)
        return


    def ERGByPlacard(self, tbxFolderPath):
        ''' Test the supporting script tool '''
        if TestUtilities.DEBUG == True:
            print("         ERGByPlacard.ERGByPlacard")
        else:
            print("Testing ERG By Placard...")

        # outputFishnet = os.path.join(self.scratchGDB, "outputFishnet")
        # arcpy.ImportToolbox(tbxFolderPath, "tdpoints")
        # groupOption = r"NONE"
        # groupFields = r"#"
        # cellWidth = 75
        # cellHeight = 75
        # rows = 0
        # columns = 0
        # labelOption = r"NO_LABELS"

        arcpy.MinimumBoundingFishnet_tdpoints(self.inputSuitableAreas, outputFishnet,
                                              groupOption, groupFields,
                                              cellWidth, cellHeight, rows, columns, labelOption)
        countOutputFishnet = arcpy.GetCount_management(os.path.join(self.outputGeodatabase, outputFishnet)).getOutput(0)
        self.assertEqual(countOutputFishnet, str(1260))
        return
