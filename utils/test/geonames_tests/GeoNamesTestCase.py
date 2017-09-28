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

class GeoNamesTestCase(unittest.TestCase, arcpyAssert.FeatureClassAssertMixin):

    toolboxUnderTest = None # Set to Pro or ArcMap toolbox at runtime
    toolboxAlias = 'defensegeonames'

    loadResultsFeatureClass = None
    templateFeatureClass = None

    def setUp(self):
        if Configuration.DEBUG == True: print("         GeoNamesTestCase.setUp")

        ''' Initialization needed if running Test Case standalone '''
        Configuration.GetLogger()
        Configuration.GetPlatform()
        ''' End standalone initialization '''

        self.toolboxUnderTest = Configuration.geonamesToolboxPath + \
            Configuration.GetToolboxSuffix()

        UnitTestUtilities.checkArcPy()

        DataDownload.runDataDownload(Configuration.geonamesDataPath, \
           Configuration.geonamesInputGDB, Configuration.geonamesURL)

        self.templateFeatureClass = os.path.join(Configuration.geonamesInputGDB, "GeonamesTemplate")
        self.loadResultsFeatureClass = os.path.join(Configuration.geonamesInputGDB, "MonacoResults")

        UnitTestUtilities.checkFilePaths([Configuration.geonamesDataPath])

        UnitTestUtilities.checkGeoObjects([self.toolboxUnderTest, \
            Configuration.geonamesInputGDB, self.loadResultsFeatureClass, \
            self.templateFeatureClass])

    def tearDown(self):
        if Configuration.DEBUG == True: print("         GeoNamesTestCase.tearDown")

    def test_load_geonames(self):
        if Configuration.DEBUG == True: print(".....GeoNamesTestCase.test_load_geonames")

        loadTextfile = os.path.join(Configuration.geonamesDataPath, "mn.txt")

        loadFeatureClass = os.path.join(Configuration.geonamesInputGDB, "LoadMonacoTest")

        countryCodes = os.path.join(Configuration.geonamesInputGDB, "CountryCodes")
        adminCodes = os.path.join(Configuration.geonamesInputGDB, "AdminCodes")
        featureCodes = os.path.join(Configuration.geonamesInputGDB, "FeatureCodes")

        # Delete the feature class used to load if already exists
        if arcpy.Exists(loadFeatureClass) :
            arcpy.Delete_management(loadFeatureClass)

        # Copy from a template feature class with required fields
        arcpy.Copy_management(self.templateFeatureClass, loadFeatureClass)

        arcpy.ImportToolbox(self.toolboxUnderTest, self.toolboxAlias)

        # Execute the Tool under test: 
        arcpy.LoadGeonamesFile_defensegeonames(loadFeatureClass, loadTextfile, \
            countryCodes, adminCodes, featureCodes)
         
        # Simple Check
        inputFeatureCount = int(arcpy.GetCount_management(loadFeatureClass).getOutput(0)) 
        self.assertGreater(inputFeatureCount, int(50))

        # Full Check
        self.assertFeatureClassEqual(self.loadResultsFeatureClass, loadFeatureClass, "OBJECTID")

    def test_create_geonames_gazetteer(self):
        if Configuration.DEBUG == True: print(".....GeoNamesTestCase.test_create_geonames_gazetteer")

        arcpy.ImportToolbox(self.toolboxUnderTest, self.toolboxAlias)

        locator = os.path.join(Configuration.geonamesDataPath, "GeoNamesLocator")

        # Does not seem to work with locators:
        # Delete if already exists
        # if arcpy.Exists(locator) :
        #    arcpy.Delete_management(locator)
        # Use this instead:
        arcpy.env.overwriteOutput = True
        
        # Just use the known good results feature class for the locator test
        locatorFeatureClass = self.loadResultsFeatureClass

        arcpy.CreateGeonamesGazetteerLocator_defensegeonames(locatorFeatureClass, locator)

        self.assertTrue(arcpy.Exists(locator))

if __name__ == "__main__":
    unittest.main()        
        
