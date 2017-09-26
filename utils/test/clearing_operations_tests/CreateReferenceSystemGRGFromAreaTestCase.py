#------------------------------------------------------------------------------
# Copyright 2017 Esri
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
#------------------------------------------------------------------------------

import logging
import unittest
import traceback
import datetime
import os
import sys
# Add parent folder to python path if running test case standalone
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

import arcpy
import Configuration
import UnitTestUtilities
import DataDownload
import arcpyAssert

class CreateReferenceSystemGRGFromAreaTestCase(unittest.TestCase, arcpyAssert.FeatureClassAssertMixin):
    '''
    Test cases for Create Reference System GRG From Area in the Gridded Reference Graphic Tools toolbox.
    '''

    toolboxUnderTest = None # Set to Pro or ArcMap toolbox at runtime
    inputArea = None
    output = None
    scratchGDB = None

    def setUp(self):
        if Configuration.DEBUG is True: print("         CreateReferenceSystemGRGFromAreaTestCase.setUp")

        ''' Initialization needed if running Test Case standalone '''
        Configuration.GetLogger()
        Configuration.GetPlatform()
        ''' End standalone initialization '''
        self.toolboxUnderTest = Configuration.grgToolboxPath

        UnitTestUtilities.checkArcPy()
        DataDownload.runDataDownload(Configuration.grgPath,
                                     Configuration.grgInputGDB,
                                     Configuration.grgURL)

        if (self.scratchGDB is None) or (not arcpy.Exists(self.scratchGDB)):
            self.scratchGDB = UnitTestUtilities.createScratch(Configuration.grgPath)

        # set up inputs
        self.inputArea = os.path.join(Configuration.grgInputGDB, r"inputAO")
        self.inputArea10m = os.path.join(Configuration.grgInputGDB, r"inputAO10m")
        self.ref_grid = "MGRS"
        self.large_grid_handling = "ALLOW_LARGE_GRIDS"
        self.ignore_options = ["IGNORE_M",
                               "IGNORE_Z",
                               "IGNORE_POINTID",
                               "IGNORE_EXTENSION_PROPERTIES",
                               "IGNORE_SUBTYPES",
                               "IGNORE_RELATIONSHIPCLASSES",
                               "IGNORE_REPRESENTATIONCLASSES"]
        UnitTestUtilities.checkFilePaths([Configuration.grgPath])
        UnitTestUtilities.checkGeoObjects([Configuration.grgInputGDB,
                                           self.toolboxUnderTest,
                                           self.scratchGDB,
                                           self.inputArea])

    def tearDown(self):
        if Configuration.DEBUG is True: print("         CreateReferenceSystemGRGFromAreaTestCase.tearDown")
        UnitTestUtilities.deleteScratch(self.scratchGDB)

    # GZD Test
    def testCreateReferenceSystemGRGFromArea_GZD(self):
        '''
        Testing with Grid Zone Designator
        '''
        if Configuration.DEBUG is True: print(".....CreateReferenceSystemGRGFromAreaTestCase.testCreateReferenceSystemGRGFromArea_GZD")
        print("Importing toolbox...")
        arcpy.ImportToolbox(self.toolboxUnderTest)
        arcpy.env.overwriteOutput = True

        #inputs
        grid_size = "GRID_ZONE_DESIGNATOR"
        output = os.path.join(self.scratchGDB, "outgrg_GZD")

        #Testing
        runToolMsg = "Running tool (CreateReferenceSystemGRGFromArea)"
        arcpy.AddMessage(runToolMsg)
        Configuration.Logger.info(runToolMsg)
        compareDataset = os.path.normpath(os.path.join(Configuration.grgInputGDB,
                                                       "CompareGZD"))

        try:
            arcpy.CreateReferenceSystemGRGFromArea_grg(self.inputArea,
                                                       self.ref_grid,
                                                       grid_size,
                                                       output,
                                                       self.large_grid_handling)
            arcpy.AddSpatialIndex_management(output)
        except arcpy.ExecuteError:
            UnitTestUtilities.handleArcPyError()
        except:
            UnitTestUtilities.handleGeneralError()

        self.assertFeatureClassEqual(compareDataset,
                                     output,
                                     arcpy.Describe(output).oidFieldName,
                                     None,
                                     "ALL",
                                     self.ignore_options)

    # 100KM Test
    def testCreateReferenceSystemGRGFromArea_100KM(self):
        '''
        Testing with 100KM grid
        '''
        if Configuration.DEBUG is True: print(".....CreateReferenceSystemGRGFromAreaTestCase.testCreateReferenceSystemGRGFromArea_100KM")
        print("Importing toolbox...")
        arcpy.ImportToolbox(self.toolboxUnderTest)
        arcpy.env.overwriteOutput = True

        #inputs
        grid_size = "100000M_GRID"
        output = os.path.join(self.scratchGDB, "outgrg_100KM")

        #Testing
        runToolMsg = "Running tool (CreateReferenceSystemGRGFromArea)"
        arcpy.AddMessage(runToolMsg)
        Configuration.Logger.info(runToolMsg)
        compareDataset = os.path.normpath(os.path.join(Configuration.grgInputGDB,
                                                       "Compare100km"))

        try:
            arcpy.CreateReferenceSystemGRGFromArea_grg(self.inputArea,
                                                  self.ref_grid,
                                                  grid_size,
                                                  output,
                                                  self.large_grid_handling)
            arcpy.AddSpatialIndex_management(output)
        except arcpy.ExecuteError:
            UnitTestUtilities.handleArcPyError()
        except:
            UnitTestUtilities.handleGeneralError()

        self.assertFeatureClassEqual(compareDataset,
                                     output,
                                     arcpy.Describe(output).oidFieldName,
                                     None,
                                     "ALL",
                                     self.ignore_options)

    # 10KM Test
    def testCreateReferenceSystemGRGFromArea_10KM(self):
        '''
        Testing with 10KM grid
        '''
        if Configuration.DEBUG is True: print(".....CreateReferenceSystemGRGFromAreaTestCase.testCreateReferenceSystemGRGFromArea_10KM")
        print("Importing toolbox...")
        arcpy.ImportToolbox(self.toolboxUnderTest)
        arcpy.env.overwriteOutput = True

        #inputs
        grid_size = "10000M_GRID"
        output = os.path.join(self.scratchGDB, "outgrg_10KM")

        #Testing
        runToolMsg = "Running tool (CreateReferenceSystemGRGFromArea)"
        arcpy.AddMessage(runToolMsg)
        Configuration.Logger.info(runToolMsg)
        compareDataset = os.path.normpath(os.path.join(Configuration.grgInputGDB,
                                                       "Compare10km"))

        try:
            arcpy.CreateReferenceSystemGRGFromArea_grg(self.inputArea,
                                                       self.ref_grid,
                                                       grid_size,
                                                       output,
                                                       self.large_grid_handling)
            arcpy.AddSpatialIndex_management(output)
        except arcpy.ExecuteError:
            UnitTestUtilities.handleArcPyError()
        except:
            UnitTestUtilities.handleGeneralError()

        self.assertFeatureClassEqual(compareDataset,
                                     output,
                                     arcpy.Describe(output).oidFieldName,
                                     None,
                                     "ALL",
                                     self.ignore_options)

    # 1000M Test
    def testCreateReferenceSystemGRGFromArea_1000M(self):
        '''
        Testing with 1000M grid
        '''
        if Configuration.DEBUG is True: print(".....CreateReferenceSystemGRGFromAreaTestCase.testCreateReferenceSystemGRGFromArea_1000M")
        print("Importing toolbox...")
        arcpy.ImportToolbox(self.toolboxUnderTest)
        arcpy.env.overwriteOutput = True

        #inputs
        grid_size = "1000M_GRID"
        output = os.path.join(self.scratchGDB, "outgrg_1000M")

        #Testing
        runToolMsg = "Running tool (CreateReferenceSystemGRGFromArea)"
        arcpy.AddMessage(runToolMsg)
        Configuration.Logger.info(runToolMsg)
        compareDataset = os.path.normpath(os.path.join(Configuration.grgInputGDB,
                                                       "Compare1000m"))

        try:
            arcpy.CreateReferenceSystemGRGFromArea_grg(self.inputArea,
                                                       self.ref_grid,
                                                       grid_size,
                                                       output,
                                                       self.large_grid_handling)
            arcpy.AddSpatialIndex_management(output)
        except arcpy.ExecuteError:
            UnitTestUtilities.handleArcPyError()
        except:
            UnitTestUtilities.handleGeneralError()

        self.assertFeatureClassEqual(compareDataset,
                                     output,
                                     arcpy.Describe(output).oidFieldName,
                                     None,
                                     "ALL",
                                     self.ignore_options)

    # 100M Test
    def testCreateReferenceSystemGRGFromArea_100M(self):
        '''
        Testing with 100M grid
        '''
        if Configuration.DEBUG is True: print(".....CreateReferenceSystemGRGFromAreaTestCase.testCreateReferenceSystemGRGFromArea_100M")
        print("Importing toolbox...")
        arcpy.ImportToolbox(self.toolboxUnderTest)
        arcpy.env.overwriteOutput = True

        #inputs
        grid_size = "100M_GRID"
        output = os.path.join(self.scratchGDB, "outgrg_100M")

        #Testing
        runToolMsg = "Running tool (CreateReferenceSystemGRGFromArea)"
        arcpy.AddMessage(runToolMsg)
        Configuration.Logger.info(runToolMsg)
        compareDataset = os.path.normpath(os.path.join(Configuration.grgInputGDB,
                                                       "Compare100m"))

        try:
            arcpy.CreateReferenceSystemGRGFromArea_grg(self.inputArea,
                                                       self.ref_grid,
                                                       grid_size,
                                                       output,
                                                       self.large_grid_handling)
            arcpy.AddSpatialIndex_management(output)
        except arcpy.ExecuteError:
            UnitTestUtilities.handleArcPyError()
        except:
            UnitTestUtilities.handleGeneralError()

        self.assertFeatureClassEqual(compareDataset,
                                     output,
                                     arcpy.Describe(output).oidFieldName,
                                     None,
                                     "ALL",
                                     self.ignore_options)

    # 10M Test
    def testCreateReferenceSystemGRGFromArea_10M(self):
        '''
        Testing DRGFA with 10M grid
        '''
        if Configuration.DEBUG is True: print(".....CreateReferenceSystemGRGFromAreaTestCase.testCreateReferenceSystemGRGFromArea_10M")
        print("Importing toolbox...")
        arcpy.ImportToolbox(self.toolboxUnderTest)
        arcpy.env.overwriteOutput = True

        #inputs
        grid_size = "10M_GRID"
        output = os.path.join(self.scratchGDB, "outgrg_10M")

        #Testing
        runToolMsg = "Running tool (CreateReferenceSystemGRGFromArea)"
        arcpy.AddMessage(runToolMsg)
        Configuration.Logger.info(runToolMsg)
        compareDataset = os.path.normpath(os.path.join(Configuration.grgInputGDB,
                                                       "Compare10m"))

        try:
            arcpy.CreateReferenceSystemGRGFromArea_grg(self.inputArea10m,
                                                       self.ref_grid,
                                                       grid_size,
                                                       output,
                                                       self.large_grid_handling)
            arcpy.AddSpatialIndex_management(output)
        except arcpy.ExecuteError:
            UnitTestUtilities.handleArcPyError()
        except:
            UnitTestUtilities.handleGeneralError()

        self.assertFeatureClassEqual(compareDataset,
                                     output,
                                     arcpy.Describe(output).oidFieldName,
                                     None,
                                     "ALL",
                                     self.ignore_options)

    # Check that no large grids created for 10m
    def testCreateReferenceSystemGRGFromArea_10mNoLargeGrids(self):
        '''
        Testing tool will raise error with NO_LARGE_GRIDS option.
        '''
        if Configuration.DEBUG is True: print(".....CreateReferenceSystemGRGFromAreaTestCase.testCreateReferenceSystemGRGFromArea_10mNoLargeGrids")
        print("Importing toolbox...")
        arcpy.ImportToolbox(self.toolboxUnderTest)
        arcpy.env.overwriteOutput = True

        #inputs
        grid_size = "10M_GRID"
        output = os.path.join(self.scratchGDB, "outgrg_10M_fail")

        #Testing
        runToolMsg = "Running tool (CreateReferenceSystemGRGFromArea)"
        arcpy.AddMessage(runToolMsg)
        Configuration.Logger.info(runToolMsg)

        with self.assertRaises(arcpy.ExecuteError) as manage_raise:
            arcpy.CreateReferenceSystemGRGFromArea_grg(self.inputArea10m,
                                                       self.ref_grid,
                                                       grid_size,
                                                       output,
                                                       "NO_LARGE_GRIDS")
        self.assertTrue('exceeds large grid value for' in str(manage_raise.exception))
