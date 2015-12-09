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
import os
import unittest
import Configuration
import UnitTestUtilities

class HLZTouchdownPoints(unittest.TestCase):
    ''' Test all tools and methods related to the HLZ Touchdown Points tool
    in the Helicopter Landing Zones toolbox'''

    scratchGDB = None

    tbxProFolderPath = os.path.join(Configuration.repoPath, "capability", "toolboxes", "Helicopter Landing Zone Tools.tbx")
    tbxDesktopFolderPath = os.path.join(Configuration.repoPath, "capability", "toolboxes", "Helicopter Landing Zone Tools_10.3.tbx")
    testDataFolderPath = os.path.join(Configuration.capabilityPath, "data")

    inputAirframeTable = None
    inputSuitableAreas = None
    inputSlope = None
    outputGeodatabase = None
    outputCenterpoints = None
    outputCircles = None

    def setUp(self):
        ''' set-up code '''
        if Configuration.DEBUG == True: print("         HLZTouchdownPoints.setUp")
        UnitTestUtilities.checkArcPy()
        UnitTestUtilities.checkFilePaths([self.testDataFolderPath,
                                          self.tbxProFolderPath,
                                          self.tbxDesktopFolderPath])

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
        return

    def tearDown(self):
        ''' clean up after tests'''
        if Configuration.DEBUG == True: print("         HLZTouchdownPoints.tearDown")
        UnitTestUtilities.deleteScratch(self.scratchGDB)
        return

    def test_MinimumBoundingFishnet_Pro(self):
        if Configuration.DEBUG == True: print("         HLZTouchdownPoints.test_MinimumBoundingFishnet_Pro")
        # check that the tool exists:
        #self.assertTrue(arcpy.Exists(os.path.join(self.tbxProFolderPath, r"MinimumBoundingFishnet")))
        self.MinimumBoundingFishnet(self.tbxProFolderPath)
        return

    def test_MinimumBoundingFishnet_Desktop(self):
        if Configuration.DEBUG == True: print("         HLZTouchdownPoints.test_MinimumBoundingFishnet_Desktop")
        # check that the tool exists:
        #self.assertTrue(arcpy.Exists(os.path.join(self.tbxDesktopFolderPath, r"MinimumBoundingFishnet")))
        self.MinimumBoundingFishnet(self.tbxDesktopFolderPath)
        return

    def MinimumBoundingFishnet(self, tbxFolderPath):
        ''' Test the supporting script tool '''
        if Configuration.DEBUG == True:
            print("         HLZTouchdownPoints.test_MiniumBoundingFishnet main")
        else:
            print("Testing Minimum Bounding Fishnet...")
        outputFishnet = os.path.join(self.scratchGDB, "outputFishnet")
        arcpy.ImportToolbox(tbxFolderPath, "tdpoints")
        groupOption = r"NONE"
        groupFields = r"#"
        cellWidth = 75
        cellHeight = 75
        rows = 0
        columns = 0
        labelOption = r"NO_LABELS"
        '''
        MinimumBoundingFishnet_ (Input_Features, Output_Fishnet, Group_Option, {Group_Fields},
                                 Cell_Width, Cell_Height, Number_of_Rows, Number_of_Columns, Labels)


        Executing (MinimumBoundingFishnet): MinimumBoundingFishnet HLZSelectionArea C:\Workspace\solutions-geoprocessing-toolbox\Test_HLZ_unittest_NOV2015\TestForHLZ\TestForHLZ.gdb\HLZSelectionArea_
        MinimumBoun NONE # 75 75 0 0 NO_LABELS
        '''
        arcpy.MinimumBoundingFishnet_tdpoints(self.inputSuitableAreas, outputFishnet,
                                              groupOption, groupFields,
                                              cellWidth, cellHeight, rows, columns, labelOption)
        countOutputFishnet = arcpy.GetCount_management(os.path.join(self.outputGeodatabase, outputFishnet)).getOutput(0)
        self.assertEqual(countOutputFishnet, str(1260))
        return

    def test_Choose_Field_Value_Script_Tool_Pro(self):
        if Configuration.DEBUG == True: print("         HLZTouchdownPoints.test_Choose_Field_Value_Script_Tool_Pro")
        self.Choose_Field_Value_Script_Tool(self.tbxProFolderPath)
        return

    def test_Choose_Field_Value_Script_Tool_Desktop(self):
        if Configuration.DEBUG == True: print("         HLZTouchdownPoints.test_Choose_Field_Values_Script_Tool_Desktop")
        self.Choose_Field_Value_Script_Tool(self.tbxDesktopFolderPath)
        return

    def Choose_Field_Value_Script_Tool(self, tbxFolderPath):
        ''' test the supporting script tool '''
        if Configuration.DEBUG == True:
            print("         HLZTouchdownPoints.test_Choose_Field_Value_Script_Tool main")
        else:
            print("Testing Choose Field Value Script Tool...")
        arcpy.ImportToolbox(tbxFolderPath, "tdpoints")
        inputField = r"Model"
        inputChoice = r"UH-60"
        result = arcpy.ChooseFieldValueScriptTool_tdpoints(self.inputAirframeTable, inputField, inputChoice)
        # compare results
        self.assertEqual(result.getOutput(0), inputChoice)
        return

    def test_HLZ_Touchdown_Points_001_Pro(self):
        if Configuration.DEBUG == True: print("         HLZTouchdownPoints.test_HLZ_Touchdown_Points_001_Pro")
        self.HLZ_Touchdown_Points_001(self.tbxProFolderPath)
        return

    def test_HLZ_Touchdown_Points_001_Desktop(self):
        if Configuration.DEBUG == True: print("         HLZTouchdownPoints.test_HLZ_Touchdown_Points_001_Desktop")
        self.HLZ_Touchdown_Points_001(self.tbxDesktopFolderPath)
        return

    def HLZ_Touchdown_Points_001(self, tbxFolderPath):
        ''' This is a basic test of the HLZ Touchdown tool with all of the input defined. '''
        if Configuration.DEBUG == True:
            print("         HLZTouchdownPoints.test_HLZ_Touchdown_Points_001")
        else:
            print("Testing HLZ Touchdown Points 001...")

        arcpy.CheckOutExtension("Spatial")

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

        arcpy.CheckInExtension("Spatial")
        # count output center points

        if Configuration.DEBUG == True: print("self.scratch.GDB: " + self.scratchGDB)
        if Configuration.DEBUG == True: print("self.outputGeodatabase: " + self.outputGeodatabase)
        if Configuration.DEBUG == True: print("self.outputCenterPoints: " + self.outputCenterpoints)

        countCenterPoints = float(arcpy.GetCount_management(self.outputCenterpoints).getOutput(0))
        # count output circles
        countOutputCircles = float(arcpy.GetCount_management(self.outputCircles).getOutput(0))
        #TODO: make sure center points fall within circles
        self.assertEqual(countCenterPoints, float(972))
        self.assertEqual(countOutputCircles, float(972))
        return