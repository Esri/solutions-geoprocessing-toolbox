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

class DefineReferenceGridFromAreaTestCase(unittest.TestCase, arcpyAssert.FeatureClassAssertMixin):
    '''
    Test cases for Define Reference Grid From Area in the Gridded Reference Graphic Tools toolbox.
    '''

    toolboxUnderTest = None # Set to Pro or ArcMap toolbox at runtime
    inputArea = None
    output = None
    scratchGDB = None

    def setUp(self):
        if Configuration.DEBUG is True: print("         DefineReferenceGridFromAreaTestCase.setUp")

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
        UnitTestUtilities.checkFilePaths([Configuration.grgPath])
        UnitTestUtilities.checkGeoObjects([Configuration.grgInputGDB,
                                           self.toolboxUnderTest,
                                           self.scratchGDB,
                                           self.inputArea])

    def tearDown(self):
        if Configuration.DEBUG is True: print("         DefineReferenceGridTestCase.tearDown")
        UnitTestUtilities.deleteScratch(self.scratchGDB)

    # TODO: GZD Test
    def testDefineReferenceGridFromArea_GZD(self):
        '''
        Testing DRGFA with Grid Zone Designator
        '''
        if Configuration.DEBUG is True: print(".....DefineReferenceGridTestCase.testDefineReferenceGridFromArea_GZD")
        print("Importing toolbox...")
        arcpy.ImportToolbox(self.toolboxUnderTest)
        arcpy.env.overwriteOutput = True

        #inputs
        grid_size = "GRID_ZONE_DESIGNATOR"
        output = os.path.join(self.scratchGDB, "outgrg_GZD")

        #Testing
        runToolMsg = "Running tool (Define Reference Grid From Area)"
        arcpy.AddMessage(runToolMsg)
        Configuration.Logger.info(runToolMsg)
        compareDataset = os.path.normpath(os.path.join(Configuration.grgInputGDB,
                                                       "CompareGZD"))

        try:
        # Calling the Create GRG From Area script tool
            arcpy.DefineReferenceGridFromArea_grg(self.inputArea,
                                                  self.ref_grid,
                                                  grid_size,
                                                  output,
                                                  self.large_grid_handling)
        except arcpy.ExecuteError:
            UnitTestUtilities.handleArcPyError()
        except:
            UnitTestUtilities.handleGeneralError()

        arcpyAssert.assertFeatureClassEqual(compareDataset,
                                            output,
                                            arcpy.Describe(output).oidFieldName)

    # TODO: 100KM Test
    # TODO: 10KM Test
    # TODO: 1000M Test
    # TODO: 100M Test
    
    # TODO: 10M Test
