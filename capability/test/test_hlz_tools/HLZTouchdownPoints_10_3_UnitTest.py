# coding: utf-8
# -----------------------------------------------------------------------------
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
# -----------------------------------------------------------------------------

# ==================================================
# HLZTouchdownPointsUnitTest.py
# --------------------------------------------------
# requirments: ArcGIS 10.3.1 and Python 2.7
# author: ArcGIS Solutions
# company: Esri
# ==================================================
# Description: Unit test for the HLZ Touchdown Points tool and also the supporing tools:
# Choose Field Value Script Tool, and MinimumBoundingFishnet.
#
# Includes the following tests:
# * test_MinimumBoundingFishnet
# * test_Choose_Field_Value_Script_Tool
# * test_HLZ_Touchdown_Points_001
# * test_HLZ_Touchdown_Points_002
#
# ==================================================
#TODO: update history
# history:
# 9/24/2015 - 10/1/2015 - MF - original test writeup
# ==================================================

import unittest
import logging
import arcpy
import sys
import traceback
import datetime
import os
import TestUtilities
import UnitTestUtilities

class HLZTouchdownPointsDesktop(unittest.TestCase):

    def setUp(self):
        ''' set-up code '''
        # Make sure we can get to ArcPy
        UnitTestUtilities.checkArcPy()

        # Set up paths
        self.testDataFolderPath = r"../../../capability/data/geodatabases/"
        tbxFolderPath = r"../../../capability/toolboxes/Helicopter Landing Zone Tools_10.3.tbx"
        UnitTestUtilities.checkFilePaths([self.testDataFolderPath, tbxFolderPath])

        #TODO: Where is the test data? Does the test data exist?
        self.testDataGeodatabase = os.path.join(self.testDataFolderPath, r"test_hlz_tools.gdb")

        # Check the test inputs (do they exist? or not?)
        if not arcpy.Exists(self.scratchGDB):
            self.scratchGDB = UnitTestUtilities.createScratch(testDataFolderPath)

        # Set up the toolbox
        self.toolbox = arcpy.ImportToolbox(tbxFolderPath, "tdpoints")

        # Setup the test inputs
        self.inputAirframeTable = os.path.join(self.testDataGeodatabase)
        self.inputSuitableAreas = os.path.join(self.testDataGeodatabase)
        self.inputSlope = os.path.join(self.testDataGeodatabase)
        self.outputGeodatabase = os.path.join(self.scratchGDB)
        self.outputCenterpoints = "centerPoints"
        self.outputCircles = "tdCircles"

        UnitTestUtilities.checkGeoObjects([self.testDataGeodatabase,
                                           self.toolbox,
                                           self.inputAirframeTable,
                                           self.inputSuitableAreas])

    def tearDown(self):
        ''' clean up after tests'''
        UnitTestUtilities.deleteScratch(self.scratchGDB)

    def test_MinimumBoundingFishnet(self):
        ''' Test the supporting script tool '''
        try:
            #TODO: write a test
            print("test_MinimumBoundingFishnet")
            outputFishnet = os.path.join(self.scratchGDB, "outputFishnet")

            arcpy.MinimumBoundingFishnet_tdPoints(self.inputSuitableAreas, outputFishnet)

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
            self.assertEqual(countCenterPoints, float(3))
            self.assertEqual(countOutputCircles, float(3))

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
            #TODO: make sure center points fall within circles
            self.assertEqual(countCenterPoints, float(3))
            self.assertEqual(countOutputCircles, float(3))

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
