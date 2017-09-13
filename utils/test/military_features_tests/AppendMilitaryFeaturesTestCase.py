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

class AppendMilitaryFeaturesTestCase(unittest.TestCase, arcpyAssert.FeatureClassAssertMixin):

    toolboxUnderTest = None # Set to Pro or ArcMap toolbox at runtime

    inputPointsFC = None

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

        self.inputPointsFC = os.path.join(Configuration.militaryFeaturesInputGDBNonMilitaryFeatures, \
            r"FriendlyForces")

        UnitTestUtilities.checkFilePaths([Configuration.militaryFeaturesDataPath])

        UnitTestUtilities.checkGeoObjects([self.toolboxUnderTest, \
            self.inputPointsFC,
            Configuration.militaryFeaturesInputGDBNonMilitaryFeatures,
            Configuration.militaryFeaturesBlankMilFeaturesGDB])

    def tearDown(self):
        if Configuration.DEBUG == True: print("         AppendMilitaryFeaturesTestCase.tearDown")

    def test_append_military_features(self):
        if Configuration.DEBUG == True: print(".....AppendMilitaryFeaturesTestCase.test_load_militaryFeatures")

        ########################################################
        # Test steps:
        # 1. Create a blank Military Features Workspace from a blank template
        # 2. Import/Append *Non-Military Features* (feature with just a SIC but no symbology) into this workspace
        # 3. Check that the workspace has the expected imported features
        ########################################################

        arcpy.env.overwriteOutput = True
        arcpy.ImportToolbox(self.toolboxUnderTest)

        outputWorkspace = os.path.join(Configuration.militaryFeaturesGeodatabasesPath, \
            "test_outputs_temp.gdb")

        # Delete the output temp GDB if already exists (from prior run)
        if arcpy.Exists(outputWorkspace) :
            arcpy.Delete_management(outputWorkspace)

        # Copy Blank Workspace to Temp GDB
        arcpy.Copy_management(Configuration.militaryFeaturesBlankMilFeaturesGDB, \
            outputWorkspace)
                        
        symbolIdField = "Symbol_ID"
        standard = "2525"

        ########################################################
        # Execute the tool under test               
        toolOutput = arcpy.AppendMilitaryFeatures_MFT(self.inputPointsFC, \
            outputWorkspace, symbolIdField, standard)
        ########################################################

        # Verify the results:

        # 1: Check the expected return value (the output workspace)
        returnedValue = toolOutput.getOutput(0)        
        self.assertEqual(returnedValue, outputWorkspace) 
      
        # 2: Check that the output feature class contains the expected number of rows
        outputPointsFC = os.path.join(outputWorkspace, \
            r"FriendlyOperations/FriendlyUnits")                  
        outputFeatureCount = int(arcpy.GetCount_management(outputPointsFC).getOutput(0))
        self.assertGreater(outputFeatureCount, int(50)) 

if __name__ == "__main__":
    unittest.main()        
        
