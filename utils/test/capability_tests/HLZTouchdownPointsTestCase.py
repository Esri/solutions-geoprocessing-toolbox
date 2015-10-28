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
HLZTouchdownPointsTestCase.py
--------------------------------------------------
requirements:
author: ArcGIS Solutions
company: Esri
==================================================
Description: Unit test for the HLZ Touchdown Points tool and also the supporing tools:
Choose Field Value Script Tool, and MinimumBoundingFishnet.

Includes the following tests:
* test_MinimumBoundingFishnet
* test_Choose_Field_Value_Script_Tool
* test_HLZ_Touchdown_Points_001
* test_HLZ_Touchdown_Points_002

==================================================
history:
9/24/2015 - 10/19/2015 - MF - original test writeup
10/21/2015 - MF - removed 10.x/1.x split between test cases
==================================================
'''

import arcpy
import sys
import traceback
import datetime
import os
import unittest
import TestUtilities
import UnitTestUtilities
import UnitTestCase

#class HLZTouchdownPoints(UnitTestCase.UnitTestCase):
class HLZTouchdownPoints(unittest.TestCase):
    ''' Test all tools and methods related to the HLZ Touchdown Points tool
    in the Helicopter Landing Zones toolbox'''

    scratchGDB = None

    tbxProFolderPath = os.path.join(TestUtilities.repoPath, "capability", "toolboxes", "Helicopter Landing Zone Tools.tbx")
    tbxDesktopFolderPath = os.path.join(TestUtilities.repoPath, "capability", "toolboxes", "Helicopter Landing Zone Tools_10.3.tbx")
    testDataFolderPath = os.path.join(TestUtilities.capabilityPath, "data", "geodatabases")

    inputAirframeTable = None
    inputSuitableAreas = None
    inputSlope = None
    outputGeodatabase = None
    outputCenterpoints = None
    outputCircles = None

    def setUp(self):
        ''' set-up code '''
        print("         HLZTouchdownPoints.setUp")
        UnitTestUtilities.checkFilePaths([self.testDataFolderPath, self.tbxProFolderPath, self.tbxDesktopFolderPath])

        self.testDataGeodatabase = os.path.join(self.testDataFolderPath, r"test_hlz_tools.gdb")

        # Check the test inputs (do they exist? or not?)
        if (self.scratchGDB == None) or (not arcpy.Exists(self.scratchGDB)):
            self.scratchGDB = UnitTestUtilities.createScratch(self.testDataFolderPath)

        # Setup the test inputs
        self.inputAirframeTable = os.path.join(self.testDataGeodatabase, r"Aircraft_Specifications")
        self.inputSuitableAreas = os.path.join(self.testDataGeodatabase, r"HLZSelectionArea")
        self.inputSlope = os.path.join(self.testDataGeodatabase, r"SRTMPctSlope")
        self.outputGeodatabase = os.path.join(self.scratchGDB)
        self.outputCenterpoints = os.path.join(self.outputGeodatabase, r"centerPoints")
        self.outputCircles = os.path.join(self.outputGeodatabase, r"tdCircles")

        UnitTestUtilities.checkGeoObjects([self.testDataGeodatabase,
                                           self.outputGeodatabase,
                                           self.inputAirframeTable,
                                           self.inputSuitableAreas,
                                           self.inputSlope])

    def tearDown(self):
        ''' clean up after tests'''
        print("         HLZTouchdownPoints.tearDown")
        UnitTestUtilities.deleteScratch(self.scratchGDB)

    def test_MinimumBoundingFishnet_Pro(self):
        print("         HLZTouchdownPoints.test_MinimumBoundingFishnet_Pro")
        self.MinimumBoundingFishnet(self.tbxProFolderPath)

    def test_MinimumBoundingFishnet_Desktop(self):
        print("         HLZTouchdownPoints.test_MinimumBoundingFishnet_Desktop")
        self.MinimumBoundingFishnet(self.tbxDesktopFolderPath)

    def MinimumBoundingFishnet(self, tbxFolderPath):
        ''' Test the supporting script tool '''
        print("         HLZTouchdownPoints.test_MiniumBoundingFishnet main")
        outputFishnet = os.path.join(self.scratchGDB, "outputFishnet")
        arcpy.ImportToolbox(tbxFolderPath, "tdpoints")

        arcpy.MinimumBoundingFishnet_tdpoints(self.inputSuitableAreas, outputFishnet)
        countOutputFishnet = arcpy.GetCount_management(os.path.join(self.outputGeodatabase, outputFishnet)).getOutput(0)
        self.assertEqual(countOutputFishnet, float(1))

    def test_Choose_Field_Value_Script_Tool_Pro(self):
        print("         HLZTouchdownPoints.test_Choose_Field_Value_Script_Tool_Pro")
        self.Choose_Field_Value_Script_Tool(self.tbxProFolderPath)

    def test_Choose_Field_Value_Script_Tool_Desktop(self):
        print("         HLZTouchdownPoints.test_Choose_Field_Values_Script_Tool_Desktop")
        self.Choose_Field_Value_Script_Tool(self.tbxDesktopFolderPath)

    def Choose_Field_Value_Script_Tool(self, tbxFolderPath):
        ''' test the supporting script tool '''
        print("         HLZTouchdownPoints.test_Choose_Field_Value_Script_Tool main")
        arcpy.ImportToolbox(tbxFolderPath, "tdpoints")
        inputField = r"Model"
        inputChoice = r"UH-60"
        result = arcpy.ChooseFieldValueScriptTool_tdpoints(self.inputAirframeTable, inputField, inputChoice)
        # compare results
        self.assertEqual(result, inputChoice)

    def test_HLZ_Touchdown_Points_001_Pro(self):
        print("         HLZTouchdownPoints.test_HLZ_Touchdown_Points_001_Pro")
        self.HLZ_Touchdown_Points_001(self.tbxProFolderPath)

    def test_HLZ_Touchdown_Points_001_Desktop(self):
        print("         HLZTouchdownPoints.test_HLZ_Touchdown_Points_001_Desktop")
        self.HLZ_Touchdown_Points_001(self.tbxDesktopFolderPath)

    def HLZ_Touchdown_Points_001(self, tbxFolderPath):
        ''' This is a basic test of the HLZ Touchdown tool with all of the input defined. '''
        print("         HLZTouchdownPoints.test_HLZ_Touchdown_Points_001")
        # move TestSunPositionAndHillshade code in here
        arcpy.ImportToolbox(tbxFolderPath, "tdpoints")
        arcpy.env.overwriteOutput = True
        inputAirframeString = r"UH-60"
        arcpy.HLZTouchdownPoints_tdpoints(self.inputAirframeTable,
                                          inputAirframeString,
                                          self.inputSuitableAreas,
                                          self.inputSlope,
                                          self.outputGeodatabase,
                                          self.outputCenterpoints,
                                          self.outputCircles)

        # count output center points
        countCenterPoints = arcpy.GetCount_management(os.path.join(self.outputGeodatabase, self.outputCenterpoints)).getOutput(0)
        # count output circles
        countOutputCircles = arcpy.GetCount_management(os.path.join(self.outputGeodatabase, self.outputCircles)).getOutput(0)
        #TODO: make sure center points fall within circles
        self.assertEqual(countCenterPoints, float(934))
        self.assertEqual(countOutputCircles, float(934))

    def test_HLZ_Touchdown_Points_002_Pro(self):
        print("         HLZTouchdownPoints.test_HLZ_Touchdown_Points_002_Pro")
        self.HLZ_Touchdown_Points_002(self.tbxProFolderPath)

    def test_HLZ_Touchdown_Points_002_Desktop(self):
        print("         HLZTouchdownPoints.test_HLZ_Touchdown_Points_002_Desktop")
        self.HLZ_Touchdown_Points_002(self.tbxDesktopFolderPath)

    def HLZ_Touchdown_Points_002(self, tbxFolderPath):
        ''' This test is for some of the default values in the HLZ Touchdown tool. '''
        print("         HLZTouchdownPoints.test_HLZ_Touchdown_Points_002")
        # move TestSunPositionAndHillshade code in here
        arcpy.ImportToolbox(tbxFolderPath, "tdpoints")
        arcpy.env.overwriteOutput = True
        # Inputs

        inputAirframeTable = "#"
        inputAirframeString = "#"
        inputSuitableAreas = self.inputSuitableAreas
        inputSlope = self.inputSlope
        outputGeodatabase = self.outputGeodatabase
        outputCenterpoints = "#"
        outputCircles = "#"

        # Testing
        arcpy.HLZTouchdownPoints_tdpoints(inputAirframeTable,
                                          inputAirframeString,
                                          inputSuitableAreas,
                                          inputSlope,
                                          outputGeodatabase,
                                          outputCenterpoints,
                                          outputCircles)

        countCenterPoints = arcpy.GetCount_management(os.path.join(self.outputGeodatabase, self.outputCenterpoints)).getOutput(0)
        countOutputCircles = arcpy.GetCount_management(os.path.join(self.outputGeodatabase, self.outputCircles)).getOutput(0)
        self.assertEqual(countCenterPoints, float(934))
        self.assertEqual(countOutputCircles, float(934))
