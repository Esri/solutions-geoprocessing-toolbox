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
# requirments: ArcGIS 10.3.1, ArcGIS Pro 1.2, Python 2.7 or Python 3.4
# author: ArcGIS Solutions
# contact: ArcGISTeam<Solution>@esri.com
# company: Esri
# ==================================================
# description: Unit test for the HLZ Touchdown Points tool
# ==================================================
#TODO: update history
# history:
# 9/24/2015 - MF - original test writeup
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

class HLZTouchdownPointsUnitTest(unittest.TestCase):
    def setUp(self):
        ''' set-up code '''
        arcpy.AddMessage("Setting up for HLZ Touchdown Points...")
        UnitTestUtilities.checkArcPy()

        # WORKAROUND: delete scratch db (having problems with scratch read-only "scheme lock" errors
        # print "Deleting Scratch Workspace (Workaround)"
        # TestUtilities.deleteScratch()
        if not arcpy.Exists(TestUtilities.scratchGDB):
            UnitTestUtilities.createScratch()
        UnitTestUtilities.checkFilePaths()
        UnitTestUtilities.checkGeoObjects()

    # def tearDown(self):
        # # tear-down code
        # arcpy.AddMessage("Tearing down the SunPositionAndHillshadeUnitTest.")

    def test_MinimumBoundingFishnet(self):
        ''' Test the supporting script tool '''
        try:
            #TODO: write a test
            arcpy.AddMessage("Testing MinimumBoundingFishnet (unit)...")
            pass
                except arcpy.ExecuteError:
            # Get the arcpy error messages
            msgs = arcpy.GetMessages()
            #TODO: need to add 'msgs' to logger
            arcpy.AddError(msgs)
            print(msgs)

            # return a system error code
            sys.exit(-1)

        except arcpy.ExecuteError:
            # Get the arcpy error messages
            msgs = arcpy.GetMessages()
            #TODO: need to add 'msgs' to logger
            arcpy.AddError(msgs)
            print(msgs)

            # return a system error code
            sys.exit(-1)

        except:
            # Get the traceback object
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]

            # Concatenate information together concerning the error into a message string
            pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n"\
                + str(sys.exc_info()[1])
            msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

            #TODO: need to add 'msgs' and 'pymsg' to logger

            # Return python error messages for use in script tool or Python Window
            arcpy.AddError(pymsg)
            arcpy.AddError(msgs)

            # Print Python error messages for use in Python / Python Window
            print(pymsg + "\n")
            print(msgs)

            # return a system error code
            sys.exit(-1)

        finally:
            pass

    def test_Choose_Field_Value_Script_Tool(self):
        ''' test the supporting script tool '''
        try:
            #TODO: write a test
            arcpy.AddMessage("Testing Choose Field Value Script Tool (unit)...")
            pass
                except arcpy.ExecuteError:
            # Get the arcpy error messages
            msgs = arcpy.GetMessages()
            #TODO: need to add 'msgs' to logger
            arcpy.AddError(msgs)
            print(msgs)

            # return a system error code
            sys.exit(-1)

        except arcpy.ExecuteError:
            # Get the arcpy error messages
            msgs = arcpy.GetMessages()
            #TODO: need to add 'msgs' to logger
            arcpy.AddError(msgs)
            print(msgs)

            # return a system error code
            sys.exit(-1)

        except:
            # Get the traceback object
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]

            # Concatenate information together concerning the error into a message string
            pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n"\
                + str(sys.exc_info()[1])
            msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

            #TODO: need to add 'msgs' and 'pymsg' to logger

            # Return python error messages for use in script tool or Python Window
            arcpy.AddError(pymsg)
            arcpy.AddError(msgs)

            # Print Python error messages for use in Python / Python Window
            print(pymsg + "\n")
            print(msgs)

            # return a system error code
            sys.exit(-1)

        finally:
            pass

    def test_HLZ_Touchdown_Points(self):
        ''' Test the GP tool '''
        try:
            arcpy.AddMessage("Testing HLZ Touchdown Points (unit)...")
            # move TestSunPositionAndHillshade code in here
            print("Importing toolbox... ")
            arcpy.ImportToolbox(TestUtilities.toolbox, "tdpoints")
            arcpy.env.overwriteOutput = True

            # Inputs
            print("Setting up inputs... ")
            inputAirframeTable = ""
            inputAirframeString = ""
            inputSuitableAreas = ""
            inputSlope = ""
            outputGeodatabase = ""
            outputCenterpoints = ""
            outputCircles = ""

            # Testing
            arcpy.AddMessage("Running tool (HLZ Touchdown Points) ...")
            arcpy.HLZTouchdownPoints_tdpoints(inputAirframeTable,
                                              inputAirframeString,
                                              inputSuitableAreas,
                                              inputSlope,
                                              outputGeodatabase,
                                              outputCenterpoints,
                                              outputCircles)

            print("Comparing expected results...")
            #TODO: count output center points
            #TODO: count output circles
            #TODO: make sure center points fall within circles
            self.assertEqual(rasMaximum, float(0))
            self.assertEqual(rasMinimum, float(0))
            self.assertEqual(rasUnique, int(1))

        except arcpy.ExecuteError:
            # Get the arcpy error messages
            msgs = arcpy.GetMessages()
            #TODO: need to add 'msgs' to logger
            arcpy.AddError(msgs)
            print(msgs)

            # return a system error code
            sys.exit(-1)

        except:
            # Get the traceback object
            tb = sys.exc_info()[2]
            tbinfo = traceback.format_tb(tb)[0]

            # Concatenate information together concerning the error into a message string
            pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n"\
                + str(sys.exc_info()[1])
            msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

            #TODO: need to add 'msgs' and 'pymsg' to logger

            # Return python error messages for use in script tool or Python Window
            arcpy.AddError(pymsg)
            arcpy.AddError(msgs)

            # Print Python error messages for use in Python / Python Window
            print(pymsg + "\n")
            print(msgs)

            # return a system error code
            sys.exit(-1)

        finally:
            pass
