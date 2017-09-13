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

import shutil
import arcpy
import unittest
import Configuration
import UnitTestUtilities
import DataDownload
import arcpyAssert

class AppendMessageFileTestCase(unittest.TestCase, arcpyAssert.FeatureClassAssertMixin):

    toolboxUnderTest = None # Set to Pro or ArcMap toolbox at runtime

    inputPointsFC = None

    def setUp(self):
        if Configuration.DEBUG == True: print("         AppendMessageFileTestCase.setUp")

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
        if Configuration.DEBUG == True: print("         AppendMessageFileTestCase.tearDown")

    def test_append_military_features(self):
        if Configuration.DEBUG == True: print(".....AppendMessageFileTestCase.test_load_militaryFeatures")

        ########################################################
        # Test steps:
        # 1. Copy a file with sample messages to a new output file
        # 2. Import/Append Military Features into this new output file
        # 3. Check that the output file is valid and size has increased
        ########################################################

        arcpy.env.overwriteOutput = True
        arcpy.ImportToolbox(self.toolboxUnderTest)

        sampleMessageFile = os.path.join(Configuration.militaryFeaturesMessagesPath, \
            r"GeoMessageSmall.xml")                   

        outputMessageFile =  os.path.join(Configuration.militaryFeaturesMessagesPath, \
            r"Test-AppendMessageFileFromMilitaryFeatures.xml")    

        shutil.copyfile(sampleMessageFile, outputMessageFile)

        # Check file exists
        self.assertTrue(os.path.isfile(outputMessageFile))
        
        startOutputFileSize= os.path.getsize(outputMessageFile)

        standard = "2525"

        ########################################################
        # Execute tool under test               
        toolOutput = arcpy.AppendMessageFileFromMilitaryFeatures_MFT(self.inputPointsFC, \
            outputMessageFile, standard)
        ########################################################

        # Verify the results:
        
        # 1: Check the expected return value
        returnedValue = toolOutput.getOutput(0)
        self.assertEqual(returnedValue, outputMessageFile)     
        
        #2: Check that Output File is larger that the previous version
        #   ie. that it did get appended to
        finishOutputFileSize = os.path.getsize(outputMessageFile)
        self.assertGreater(finishOutputFileSize, startOutputFileSize) 

if __name__ == "__main__":
    unittest.main()        
        
