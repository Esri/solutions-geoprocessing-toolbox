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

class WriteMilitaryFeatureFromMessageTestCase(unittest.TestCase, arcpyAssert.FeatureClassAssertMixin):

    toolboxUnderTest = None # Set to Pro or ArcMap toolbox at runtime

    outputPointsFC = None

    def setUp(self):
        if Configuration.DEBUG == True: print("         WriteMilitaryFeatureFromMessageTestCase.setUp")

        ''' Initialization needed if running Test Case standalone '''
        Configuration.GetLogger()
        Configuration.GetPlatform()
        ''' End standalone initialization '''

        self.toolboxUnderTest = Configuration.militaryFeaturesToolboxPath + \
            Configuration.GetToolboxSuffix()

        UnitTestUtilities.checkArcPy()

        DataDownload.runDataDownload(Configuration.militaryFeaturesDataPath, \
           Configuration.militaryFeaturesInputGDB, Configuration.militaryFeaturesURL)

        outputWorkspace = os.path.join(Configuration.militaryFeaturesGeodatabasesPath, \
            "test_outputs.gdb")
        self.outputPointsFC = os.path.normpath(os.path.join(outputWorkspace, \
                                          r"FriendlyOperations/FriendlyEquipment"))

        UnitTestUtilities.checkFilePaths([Configuration.militaryFeaturesDataPath, \
                                          Configuration.militaryFeaturesMessagesPath])

        UnitTestUtilities.checkGeoObjects([self.toolboxUnderTest, \
                                           self.outputPointsFC])

    def tearDown(self):
        if Configuration.DEBUG == True: print("         WriteMilitaryFeatureFromMessageTestCase.tearDown")

    def test_write_military_feature_from_message_file(self):
        if Configuration.DEBUG == True: print(".....WriteMilitaryFeatureFromMessageTestCase.test_write_military_feature_from_message_file")

        ########################################################
        # Test steps:
        # 1. Use a Military Features feature class to create an XML message file
        # 2. Check that the output message file was create and is valid(size > 0)
        ########################################################

        arcpy.env.overwriteOutput = True
        arcpy.ImportToolbox(self.toolboxUnderTest)

        inputMessageFile = os.path.normpath(os.path.join(Configuration.militaryFeaturesMessagesPath, \
            r"GeoMessageSmall.xml"))
        self.assertTrue(os.path.isfile(inputMessageFile))

        startRecordCount = int(arcpy.GetCount_management(self.outputPointsFC).getOutput(0))
                
        standard = "2525"
                     
        ########################################################
        # Execute the Model under test:   
        # Test 1: (Runtime Message Output)
        toolOutput = arcpy.WriteMilitaryFeatureFromMessageFile_MFT(inputMessageFile, \
            self.outputPointsFC, standard)
        ########################################################

        # Verify the results:
        
        # 1: Check the expected return value
        returnedValue = toolOutput.getOutput(0)
        self.assertEqual(returnedValue, self.outputPointsFC)     
        
        # 2: Check that Output Files got created and are valid
        endRecordCount = int(arcpy.GetCount_management(self.outputPointsFC).getOutput(0))
        self.assertGreater(endRecordCount, startRecordCount)

if __name__ == "__main__":
    unittest.main()
