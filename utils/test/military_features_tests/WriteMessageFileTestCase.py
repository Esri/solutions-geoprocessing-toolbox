# coding: utf-8
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

import os

# Add parent folder to python path if running test case standalone
import sys
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import arcpy
import Configuration
import UnitTestUtilities
import DataDownload
import arcpyAssert

class WriteMessageFileTestCase(unittest.TestCase, arcpyAssert.FeatureClassAssertMixin):

    toolboxUnderTest = None # Set to Pro or ArcMap toolbox at runtime

    inputPointsFC = None

    def setUp(self):
        if Configuration.DEBUG == True: print("         WriteMessageFileTestCase.setUp")

        ''' Initialization needed if running Test Case standalone '''
        Configuration.GetLogger()
        Configuration.GetPlatform()
        ''' End standalone initialization '''

        self.toolboxUnderTest = Configuration.militaryFeaturesToolboxPath + \
            Configuration.GetToolboxSuffix()

        UnitTestUtilities.checkArcPy()

        DataDownload.runDataDownload(Configuration.militaryFeaturesDataPath, \
           Configuration.militaryFeaturesInputGDB, Configuration.militaryFeaturesURL)

        self.inputPointsFC = os.path.join(Configuration.militaryFeaturesInputGDB, \
                                          r"FriendlyOperations/FriendlyUnits")

        UnitTestUtilities.checkFilePaths([Configuration.militaryFeaturesDataPath, \
                                          Configuration.militaryFeaturesMessagesPath])

        UnitTestUtilities.checkGeoObjects([self.toolboxUnderTest, \
            self.inputPointsFC])

    def tearDown(self):
        if Configuration.DEBUG == True: print("         WriteMessageFileTestCase.tearDown")

    def test_write_military_message_file(self):
        if Configuration.DEBUG == True: print(".....WriteMessageFileTestCase.test_write_military_message_file")

        ########################################################
        # Test steps:
        # 1. Use a Military Features feature class to create an XML message file
        # 2. Check that the output message file was create and is valid(size > 0)
        ########################################################

        arcpy.env.overwriteOutput = True
        arcpy.ImportToolbox(self.toolboxUnderTest)

        outputMessageFile = os.path.normpath(os.path.join(Configuration.militaryFeaturesMessagesPath, r"Test-WriteMessageFileFromMilitaryFeatures.xml"))
        outputMessageFileDebugFormat = outputMessageFile.replace('.xml', '-Debug.xml')

        standard = "2525"              
        messageTypeField = "#"
        orderBy = "#"
        disableGeoTransform = "#"

        ########################################################
        # Execute tool under test               
        toolOutput = arcpy.WriteMessageFileFromMilitaryFeatures_MFT(self.inputPointsFC, \
            outputMessageFile, standard, messageTypeField, orderBy, disableGeoTransform)
        
        # Also run the "Debug Format" tool (that maps everything to unknown , doesn't translate points)
        disableGeoTransform = "True"
        arcpy.WriteMessageFileFromMilitaryFeatures_MFT(self.inputPointsFC, \
            outputMessageFileDebugFormat, standard, messageTypeField, orderBy, \
            disableGeoTransform)
        ########################################################

        # Verify the results:
        
        # 1: Check the expected return value
        returnedValue = toolOutput.getOutput(0)
        self.assertEqual(returnedValue, outputMessageFile)     
        
        # 2: Check that Output Files got created and are valid
        self.assertTrue(os.path.isfile(outputMessageFile))
        outputFileSize = os.path.getsize(outputMessageFile)
        self.assertGreater(outputFileSize, int(35000))

        outputFileSizeDebug = os.path.getsize(outputMessageFileDebugFormat)
        self.assertGreater(outputFileSize, int(40000)) # will be larger (more points)

if __name__ == "__main__":
    unittest.main()
