#------------------------------------------------------------------------------
# Copyright 2015-2017 Esri
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

import datetime
import os
import sys
import traceback

import arcpy
from arcpy.sa import * #IMPORTANT: requires Spatial Analyst for raster diff below

# Add parent folder to python path if running test case standalone
import sys
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import Configuration
import UnitTestUtilities
import DataDownload

class SunPositionAndHillshadeTestCase(unittest.TestCase):

    toolboxUnderTest = None # Set to Pro or ArcMap toolbox at runtime

    inputArea = None
    inputSurface = None
    compareResults = None

    scratchGDB = None

    def setUp(self):
        if Configuration.DEBUG == True: print("         SunPositionAndHillshadeTestCase.setUp")

        ''' Initialization needed if running Test Case standalone '''
        Configuration.GetLogger()
        Configuration.GetPlatform()
        ''' End standalone initialization '''

        self.toolboxUnderTest = Configuration.sunPositionAnalysisToolboxPath + \
            Configuration.GetToolboxSuffix()

        UnitTestUtilities.checkArcPy()

        DataDownload.runDataDownload(Configuration.sunPositionAnalysisDataPath, \
           Configuration.sunPositionInputGDB, Configuration.sunPositionAnalysisURL)

        if (self.scratchGDB == None) or (not arcpy.Exists(self.scratchGDB)):
            self.scratchGDB = UnitTestUtilities.createScratch(Configuration.sunPositionAnalysisDataPath)

        # set up inputs
        self.inputArea = os.path.join(Configuration.sunPositionInputGDB, r"inputArea")
        self.inputSurface = os.path.join(Configuration.sunPositionInputGDB, r"Jbad_SRTM_USGS_EROS")
        self.compareResults = os.path.join(Configuration.sunPositionInputGDB, r"compareResults_2017_8_10_16_30_00")

        UnitTestUtilities.checkFilePaths([Configuration.sunPositionAnalysisDataPath])

        UnitTestUtilities.checkGeoObjects([Configuration.sunPositionInputGDB, \
            self.toolboxUnderTest, self.scratchGDB, \
            self.inputArea, self.inputSurface, \
            self.compareResults])

    def tearDown(self):
        if Configuration.DEBUG == True: print("         SunPositionAndHillshadeTestCase.tearDown")
        UnitTestUtilities.deleteScratch(self.scratchGDB)

    def test_sun_position_analysis(self):
        if Configuration.DEBUG == True: print(".....SunPositionAndHillshadeTestCase.test_sun_position_analysis")

        print("Importing toolbox... ")
        arcpy.ImportToolbox(self.toolboxUnderTest)

        arcpy.env.overwriteOutput = True

        # Inputs
        print("Setting up inputs... ")
        # '''
        # Tool comparison is based on static dataset in Web Mercator
        # over Afghanistan, for 8/10/2017 at 16:30
        # '''
        dtCompare = datetime.datetime(2017, 8, 10, 16, 30, 30)
        print("Set date...")
        utcAfghanistan = r'(UTC+4:30) Afghanistan'
        print("Set UTCAfg...")

        outHillshade = os.path.join(self.scratchGDB, "outputHS")
        print("Set output hillshade...")

        # Testing
        runToolMsg = "Running tool (Sun Position and Hillshade)"
        arcpy.AddMessage(runToolMsg)
        Configuration.Logger.info(runToolMsg)

        try:
            arcpy.SunPositionAnalysis_sunpos(self.inputArea, self.inputSurface, \
                dtCompare, utcAfghanistan, outHillshade)
        except arcpy.ExecuteError:
            UnitTestUtilities.handleArcPyError()
        except:
            UnitTestUtilities.handleGeneralError()

        compareMessage = "Comparing expected values with tool results from " + str(dtCompare) + " in " + str(utcAfghanistan)
        Configuration.Logger.info(compareMessage)
        compareResults = self.compareResults

        # Diff requires Spatial Analyst extension
        requiredExtension = "Spatial"
        if arcpy.CheckExtension(requiredExtension) == "Available":
            arcpy.CheckOutExtension(requiredExtension)
        else:
            raise Exception(requiredExtension + " license is not available.")

        # Results Testing Method:
        # Run a diff on the result surface above and a known good previous run
        # There should be no differences between the raster datasets
        # No differences -> max diff = min diff = 0, unique values = 1
        diff = Minus(Raster(outHillshade),Raster(compareResults))
        diff.save(os.path.join(self.scratchGDB, "diff"))
        arcpy.CalculateStatistics_management(diff)
        rasMinimum = abs(float(arcpy.GetRasterProperties_management(diff,"MINIMUM").getOutput(0)))
        rasMaximum = abs(float(arcpy.GetRasterProperties_management(diff,"MAXIMUM").getOutput(0)))
        rasMean = float(arcpy.GetRasterProperties_management(diff,"MEAN").getOutput(0))
        rasSTD = float(arcpy.GetRasterProperties_management(diff,"STD").getOutput(0))
        rasUnique = int(arcpy.GetRasterProperties_management(diff,"UNIQUEVALUECOUNT").getOutput(0))

        arcpy.CheckInExtension(requiredExtension)

        tolerance = 3 # allow this much variation in the outputs (ArcMap and Pro vary a tiny bit) 
        if (rasMaximum <= float(tolerance)) and (rasMinimum <= float(tolerance)) and (rasUnique <= int(tolerance)):
            Configuration.Logger.info("No differences between tool output and expected results.")
        else:
             msg = "ERROR IN TOOL RESULTS: \n"\
                 + "Difference between tool output and expected results found:\n"\
                 + "Difference Minimum: " + str(rasMinimum) + "\n"\
                 + "Difference Maximum: " + str(rasMaximum) + "\n"\
                 + "Difference Mean: " + str(rasMean) + "\n"\
                 + "Difference Std. Deviation: " + str(rasSTD) + "\n"\
                 + "Difference Number of Unique Values: " + str(rasUnique) + "\n"
             Configuration.Logger.error(msg)

        self.assertLessEqual(rasMaximum, float(tolerance))
        self.assertLessEqual(rasMinimum, float(tolerance))
        self.assertLessEqual(rasUnique, int(tolerance))

if __name__ == "__main__":
    unittest.main()        
        
