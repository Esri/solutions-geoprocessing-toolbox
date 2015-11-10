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
ERGScriptTestCase.py
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


class ERGTest(unittest.TestCase):
    ''' Test ERG source script for the ERG Tools toolbox'''

    scratchGDB = None

    #tbxFolderPath = os.path.join(TestUtilities.repoPath, "capability", "toolboxes", "ERG Tools.pyt")
    #testDataFolderPath = os.path.join(TestUtilities.capabilityPath, "data")

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

        #TODO: write test for LookUpERG
        #LookUpERG(pChemical, pPlacardID, pSpillSize, pTimeOfDay, pERGdbf)

        #TODO: write test for GetProjectedPoint
        #GetProjectedPoint(pPointFeatureRecordSet)

        #TODO: write test for MakeERGFeatures
        #MakeERGFeatures(pProjectedPointGeometry, pWindBlowingToDirection, pInitialIsolationDistance, pProtectiveActionDistance,
        #            pMaterials, pGuideNum, pSpillSize, pTimeOfDay, pOutAreas, pOutLines, pTemplateLoc)

        return
