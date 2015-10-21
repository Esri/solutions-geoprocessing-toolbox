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

import logging
import arcpy
import sys
import traceback
import datetime
import os
import unittest
import TestUtilities
import UnitTestUtilities
import UnitTestCase

class HLZTouchdownPoints(UnitTestCase.UnitTestCase):
    ''' Test all tools and methods related to the HLZ Touchdown Points tool
    in the Helicopter Landing Zones toolbox'''

    def setUp(self, tbxFolderPath):
        ''' set-up code '''

        try:
            # Set up paths
            self.testDataFolderPath = r"../../../capability/data/geodatabases/"
            UnitTestUtilities.checkFilePaths([self.testDataFolderPath, tbxFolderPath])

            #TODO: Where is the test data? Does the test data exist?
            self.testDataGeodatabase = os.path.join(self.testDataFolderPath, r"test_hlz_tools.gdb")

            # Check the test inputs (do they exist? or not?)
            if not arcpy.Exists(self.scratchGDB):
                self.scratchGDB = UnitTestUtilities.createScratch(testDataFolderPath)

            # Set up the toolbox
            self.toolbox = arcpy.ImportToolbox(tbxFolderPath, "tdpoints")

            # Setup the test inputs
            self.inputAirframeTable = os.path.join(self.testDataGeodatabase, r"Aircraft_Specifications")
            self.inputSuitableAreas = os.path.join(self.testDataGeodatabase, r"HLZSelectionArea")
            self.inputSlope = os.path.join(self.testDataGeodatabase, r"SRTMPctSlope")
            self.outputGeodatabase = os.path.join(self.scratchGDB)
            self.outputCenterpoints = os.path.join(self.outputGeodatabase, r"centerPoints")
            self.outputCircles = os.path.join(self.outputGeodatabase, r"tdCircles")

            UnitTestUtilities.checkGeoObjects([self.testDataGeodatabase,
                                               self.toolbox,
                                               self.inputAirframeTable,
                                               self.inputSuitableAreas])
        except:
            # Get the traceback object
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]

            # Concatenate information together concerning the error into a message string
            pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n"\
                + str(sys.exc_info()[1])
            msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

            #TODO: need to add 'msgs' and 'pymsg' to logger

            # Print Python error messages for use in Python / Python Window
            print(pymsg + "\n")
            print(msgs)

    def tearDown(self):
        ''' clean up after tests'''
        UnitTestUtilities.deleteScratch(self.scratchGDB)

    def test_MinimumBoundingFishnet(self):
        ''' Test the supporting script tool '''
        try:
            #TODO: Finish writing a test
            print("test_MinimumBoundingFishnet")
            outputFishnet = os.path.join(self.scratchGDB, "outputFishnet")

            arcpy.MinimumBoundingFishnet_tdPoints(self.inputSuitableAreas, outputFishnet)
            countOutputFishnet = arcpy.GetCount_management(os.path.join(self.outputGeodatabase, outputFishnet)).getOutput(0)
            self.assertEqual(countOutputFishnet, float(1))

        except arcpy.ExecuteError:
            # Get the arcpy error messages
            msgs = arcpy.GetMessages()
            #TODO: need to add 'msgs' to logger
            print(msgs)

        except:
            # Get the traceback object
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]

            # Concatenate information together concerning the error into a message string
            pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n"\
                + str(sys.exc_info()[1])
            msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

            #TODO: need to add 'msgs' and 'pymsg' to logger

            # Print Python error messages for use in Python / Python Window
            print(pymsg + "\n")
            print(msgs)

    def test_Choose_Field_Value_Script_Tool(self):
        ''' test the supporting script tool '''
        try:
            #TODO: write a test
            print("test_Choose_Field_Value_Script_Tool")
            inputField = r"Model"
            inputChoice = r"UH-60"
            result = arcpy.ChooseFieldValueScriptTool_tdpoints(self.inputAirframeTable,inputField,inputChoice)

            # compare results
            self.assertEqual(result,inputChoice)

        except arcpy.ExecuteError:
            # Get the arcpy error messages
            msgs = arcpy.GetMessages()
            #TODO: need to add 'msgs' to logger
            print(msgs)

        except:
            # Get the traceback object
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]

            # Concatenate information together concerning the error into a message string
            pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n"\
                + str(sys.exc_info()[1])
            msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

            #TODO: need to add 'msgs' and 'pymsg' to logger

            # Print Python error messages for use in Python / Python Window
            print(pymsg + "\n")
            print(msgs)

    def test_HLZ_Touchdown_Points_001(self):
        ''' This is a basic test of the HLZ Touchdown tool with all of the input defined. '''
        try:
            print("test_HLZ_Touchdown_Points_001")
            # move TestSunPositionAndHillshade code in here
            print("Importing toolbox... ")
            arcpy.ImportToolbox(TestUtilities.toolbox, "tdpoints")
            arcpy.env.overwriteOutput = True

            # Inputs
            print("Setting up inputs... ")
            inputAirframeString = r"UH-60"

            # Testing
            print("Running tool (HLZ Touchdown Points) ...")
            arcpy.HLZTouchdownPoints_tdpoints(self.inputAirframeTable,
                                              inputAirframeString,
                                              self.inputSuitableAreas,
                                              self.inputSlope,
                                              self.outputGeodatabase,
                                              self.outputCenterpoints,
                                              self.outputCircles)

            print("Comparing expected results...")
            # count output center points
            countCenterPoints = arcpy.GetCount_management(os.path.join(self.outputGeodatabase, self.outputCenterpoints)).getOutput(0)
            # count output circles
            countOutputCircles = arcpy.GetCount_management(os.path.join(self.outputGeodatabase, self.outputCircles)).getOutput(0)
            #TODO: make sure center points fall within circles
            self.assertEqual(countCenterPoints, float(934))
            self.assertEqual(countOutputCircles, float(934))

        except arcpy.ExecuteError:
            # Get the arcpy error messages
            msgs = arcpy.GetMessages()
            #TODO: need to add 'msgs' to logger
            print(msgs)

        except:
            # Get the traceback object
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]

            # Concatenate information together concerning the error into a message string
            pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n"\
                + str(sys.exc_info()[1])
            msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

            #TODO: need to add 'msgs' and 'pymsg' to logger

            # Print Python error messages for use in Python / Python Window
            print(pymsg + "\n")
            print(msgs)

    def test_HLZ_Touchdown_Points_002(self):
        ''' This test is for some of the default values in the HLZ Touchdown tool. '''
        try:
            arcpy.AddMessage("test_HLZ_Touchdown_Points_002")
            # move TestSunPositionAndHillshade code in here
            print("Importing toolbox... ")
            arcpy.ImportToolbox(TestUtilities.toolbox, "tdpoints")
            arcpy.env.overwriteOutput = True

            # Inputs
            print("Setting up inputs... ")
            inputAirframeTable = "#"
            inputAirframeString = "#"
            inputSuitableAreas = self.inputSuitableAreas
            inputSlope = self.inputSlope
            outputGeodatabase = self.outputGeodatabase
            outputCenterpoints = "#"
            outputCircles = "#"

            # Testing
            print("Running tool (HLZ Touchdown Points) ...")
            arcpy.HLZTouchdownPoints_tdpoints(inputAirframeTable,
                                              inputAirframeString,
                                              inputSuitableAreas,
                                              inputSlope,
                                              outputGeodatabase,
                                              outputCenterpoints,
                                              outputCircles)

            print("Comparing expected results...")
            # count output center points
            countCenterPoints = arcpy.GetCount_management(os.path.join(self.outputGeodatabase, self.outputCenterpoints)).getOutput(0)
            # count output circles
            countOutputCircles = arcpy.GetCount_management(os.path.join(self.outputGeodatabase, self.outputCircles)).getOutput(0)

            self.assertEqual(countCenterPoints, float(934))
            self.assertEqual(countOutputCircles, float(934))

            #TODO: make sure center points fall within circles

        except arcpy.ExecuteError:
            # Get the arcpy error messages
            msgs = arcpy.GetMessages()
            #TODO: need to add 'msgs' to logger
            print(msgs)

        except:
            # Get the traceback object
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]

            # Concatenate information together concerning the error into a message string
            pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n"\
                + str(sys.exc_info()[1])
            msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

            #TODO: need to add 'msgs' and 'pymsg' to logger

            # Print Python error messages for use in Python / Python Window
            print(pymsg + "\n")
            print(msgs)
