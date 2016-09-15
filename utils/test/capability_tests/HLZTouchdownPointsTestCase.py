# coding: utf-8
'''
-----------------------------------------------------------------------------
Copyright 2016 Esri
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
Description: Unit test for the HLZ Touchdown Points tool and also the supporting tools:
Choose Field Value Script Tool, and MinimumBoundingFishnet.

Includes the following tests:
* test_MinimumBoundingFishnet
* test_Choose_Field_Value_Script_Tool
* test_HLZ_Touchdown_Points_001

==================================================
history:
9/24/2015 - 10/19/2015 - MF - original test writeup
10/21/2015 - MF - removed 10.x/1.x split between test cases
04/29/2016 - MF - fix #387 where test_hlz_tools.gdb is not created
09/12/2016 - MF - Split 10.x/1.x tests as errors are not trapped
==================================================
'''

import arcpy
import os
import unittest
import Configuration
import UnitTestUtilities
import DataDownload

class HLZTouchdownPoints(unittest.TestCase):
    ''' Test all tools and methods related to the HLZ Touchdown Points tool
    in the Helicopter Landing Zones toolbox'''

    scratchGDB = None
    testDataFolderPath = None
    #testDataFolderPath = os.path.join(Configuration.capabilityPath, "data")

    inputAirframeTable = None
    inputSuitableAreas = None
    inputSlope = None
    outputGeodatabase = None
    outputCenterpoints = None
    outputCircles = None

    def setUp(self):
        ''' set-up code '''
        if Configuration.DEBUG == True: print(".....HLZTouchdownPoints.setUp")
        UnitTestUtilities.checkArcPy()

        # Setup the test specific paths
        self.tbxProFolderPath = os.path.join(Configuration.repoPath, "capability", "toolboxes", "Helicopter Landing Zone Tools.tbx")
        self.tbxDesktopFolderPath = os.path.join(Configuration.repoPath, "capability", "toolboxes", "Helicopter Landing Zone Tools_10.4.tbx")
        self.dataDownloadURL = r"http://www.arcgis.com/sharing/content/items/eb5685e1af5d4c16b49fc8870ced036c/data"
        self.testDataFolderPath = DataDownload.createDataFolder(Configuration.capabilityPath)

        # Check the paths exist
        print("Created Capability test data folder.")
        UnitTestUtilities.checkFilePaths([self.testDataFolderPath,
                                          self.tbxProFolderPath,
                                          self.tbxDesktopFolderPath])
        # set the geodatabase
        self.testDataGeodatabase = os.path.join(self.testDataFolderPath, r"test_hlz_tools.gdb")
        
        # Download the test data from arcgis.com
        self.testDataFolderPath = DataDownload.runDataDownload(Configuration.capabilityPath,
                                                               os.path.basename(self.testDataGeodatabase),
                                                               self.dataDownloadURL)

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
        if Configuration.DEBUG == True: print(".....HLZTouchdownPoints.tearDown")
        UnitTestUtilities.deleteScratch(self.scratchGDB)
        return

    def test_MinimumBoundingFishnet_Pro(self):
        '''Test Minimum Bounding Fishnet for Pro'''
        if Configuration.DEBUG == True: print(".....HLZTouchdownPoints.test_MinimumBoundingFishnet_Pro")
        outputFishnet = os.path.join(self.scratchGDB, "outputFishnet")
        arcpy.ImportToolbox(self.tbxProFolderPath, "tdpoints")
        groupOption = r"NONE"
        groupFields = r"#"
        cellWidth = 75
        cellHeight = 75
        rows = 0
        columns = 0
        labelOption = r"NO_LABELS"
        arcpy.MinimumBoundingFishnet_tdpoints(self.inputSuitableAreas, outputFishnet,
                                              groupOption, groupFields,
                                              cellWidth, cellHeight, rows, columns, labelOption)
        countOutputFishnet = arcpy.GetCount_management(os.path.join(self.outputGeodatabase, outputFishnet)).getOutput(0)
        self.assertEqual(countOutputFishnet, str(1260))
        return

    def test_MinimumBoundingFishnet_Desktop(self):
        ''' Test Minimum Bounding Fishnet for Desktop '''
        if Configuration.DEBUG == True: print(".....HLZTouchdownPoints.test_MinimumBoundingFishnet_Desktop")
        outputFishnet = os.path.join(self.scratchGDB, "outputFishnet")
        arcpy.ImportToolbox(self.tbxDesktopFolderPath, "tdpoints")
        groupOption = r"NONE"
        groupFields = r"#"
        cellWidth = 75
        cellHeight = 75
        rows = 0
        columns = 0
        labelOption = r"NO_LABELS"
        arcpy.MinimumBoundingFishnet_tdpoints(self.inputSuitableAreas, outputFishnet,
                                              groupOption, groupFields,
                                              cellWidth, cellHeight, rows, columns, labelOption)
        countOutputFishnet = arcpy.GetCount_management(os.path.join(self.outputGeodatabase, outputFishnet)).getOutput(0)
        self.assertEqual(countOutputFishnet, str(1260))
        return


    def test_Choose_Field_Value_Script_Tool_Pro(self):
        '''Test for Choose Field Value script tool for Pro'''
        if Configuration.DEBUG == True: print(".....HLZTouchdownPoints.test_Choose_Field_Value_Script_Tool_Pro")
        arcpy.ImportToolbox(self.tbxProFolderPath, "tdpoints")
        inputField = r"Model"
        inputChoice = r"UH-60"
        result = arcpy.ChooseFieldValueScriptTool_tdpoints(self.inputAirframeTable, inputField, inputChoice)
        # compare results
        self.assertEqual(result.getOutput(0), inputChoice)
        return

    def test_Choose_Field_Value_Script_Tool_Desktop(self):
        '''Test for Choose Field Value script tool for Desktop'''
        if Configuration.DEBUG == True: print(".....HLZTouchdownPoints.test_Choose_Field_Values_Script_Tool_Desktop")
        arcpy.ImportToolbox(self.tbxDesktopFolderPath, "tdpoints")
        inputField = r"Model"
        inputChoice = r"UH-60"
        result = arcpy.ChooseFieldValueScriptTool_tdpoints(self.inputAirframeTable, inputField, inputChoice)
        # compare results
        self.assertEqual(result.getOutput(0), inputChoice)
        return


    def test_HLZ_Touchdown_Points_001_Pro(self):
        '''Test 001 for HLZ Touchdown Points for Pro'''
        if Configuration.DEBUG == True: print(".....HLZTouchdownPoints.test_HLZ_Touchdown_Points_001_Pro")
        arcpy.CheckOutExtension("Spatial")
        arcpy.ImportToolbox(self.tbxProFolderPath, "tdpoints")
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

    def test_HLZ_Touchdown_Points_001_Desktop(self):
        '''Test 001 for HLZ Touchdown Points for Pro'''
        if Configuration.DEBUG == True: print(".....HLZTouchdownPoints.test_HLZ_Touchdown_Points_001_Desktop")
        arcpy.CheckOutExtension("Spatial")
        arcpy.ImportToolbox(self.tbxDesktopFolderPath, "tdpoints")
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
