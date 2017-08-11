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

import arcpy
import os

# Add parent folder to python path if running test case standalone
import sys
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import Configuration
import UnitTestUtilities
import DataDownload
import arcpyAssert

class AppendMilitaryFeaturesTestCase(unittest.TestCase, arcpyAssert.FeatureClassAssertMixin):

    toolboxUnderTest = None # Set to Pro or ArcMap toolbox at runtime

    loadResultsFeatureClass = None
    templateFeatureClass = None

    def setUp(self):
        if Configuration.DEBUG == True: print("         AppendMilitaryFeaturesTestCase.setUp")

        ''' Initialization needed if running Test Case standalone '''
        Configuration.GetLogger()
        Configuration.GetPlatform()
        ''' End standalone initialization '''

        self.toolboxUnderTest = Configuration.militaryFeaturesToolboxPath + \
            Configuration.GetToolboxSuffix()

        UnitTestUtilities.checkArcPy()

        DataDownload.runDataDownload(Configuration.militaryFeaturesDataPath, \
           Configuration.militaryFeaturesInputGDB, Configuration.militaryFeaturesURL)

        UnitTestUtilities.checkFilePaths([Configuration.militaryFeaturesDataPath])

        UnitTestUtilities.checkGeoObjects([self.toolboxUnderTest, \
            Configuration.militaryFeaturesInputGDB])

    def tearDown(self):
        if Configuration.DEBUG == True: print("         AppendMilitaryFeaturesTestCase.tearDown")

    def test_append_military_features(self):
        if Configuration.DEBUG == True: print(".....AppendMilitaryFeaturesTestCase.test_load_militaryFeatures")

        arcpy.ImportToolbox(self.toolboxUnderTest)


if __name__ == "__main__":
    unittest.main()        
        
