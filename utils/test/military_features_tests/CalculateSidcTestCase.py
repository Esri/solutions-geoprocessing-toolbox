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

import arcpy
import unittest
import Configuration
import UnitTestUtilities
import DataDownload
import arcpyAssert

class CalculateSidcTestCase(unittest.TestCase, arcpyAssert.FeatureClassAssertMixin):

    toolboxUnderTest = None # Set to Pro or ArcMap toolbox at runtime

    inputPointsFC = None

    def setUp(self):
        if Configuration.DEBUG == True: print("         CalculateSidcTestCase.setUp")

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

        UnitTestUtilities.checkFilePaths([Configuration.militaryFeaturesDataPath])

        UnitTestUtilities.checkGeoObjects([self.toolboxUnderTest, \
            self.inputPointsFC])

    def tearDown(self):
        if Configuration.DEBUG == True: print("         CalculateSidcTestCase.tearDown")

    def test_calculate_sidc(self):
        if Configuration.DEBUG == True: print(".....CalculateSidcTestCase.test_calculate_sidc")

        ########################################################
        # Test steps:
        # 1. Copy a known good Military Features feature class
        # 2. Clear the SIDC field for this feature class
        # 3. Run the tool to calculate the SIDC field
        # 4. Verify the SIDC values have been calculated
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

        inputCalcSidcFC = os.path.join(outputWorkspace, r"FriendlyOperations/FriendlyUnits")    

        # Copy the features of the input FC into the output GDB
        arcpy.CopyFeatures_management(self.inputPointsFC, inputCalcSidcFC)   

        # Check test feature class was created
        self.assertTrue(arcpy.Exists(inputCalcSidcFC))

        sidcField = "sic"
        standard = "2525"
        echelonField = "echelon" 
        affiliation = "FRIENDLY"
                     
        # Zero out the SIDC/SIC field first
        arcpy.CalculateField_management(inputCalcSidcFC, sidcField, '""')

        ########################################################
        # Execute tool under test               
        toolOutput = arcpy.CalcSymbolIDField_MFT(inputCalcSidcFC, sidcField, \
            standard, echelonField, affiliation)
        ########################################################

        # Verify the results:
        
        # 1: Check the expected return value
        returnedValue = toolOutput.getOutput(0)
        self.assertEqual(returnedValue, inputCalcSidcFC)     
        
        #2: Check that Output Feature class has no rows without the Rep Rule field set
        outputSidcsLayer = "SidcNull_layer"             
        
        arcpy.MakeFeatureLayer_management(inputCalcSidcFC, outputSidcsLayer)
        query = '(' + sidcField + ' is NULL)' + ' or (' + sidcField + ' = \'SUGPU----------\')'
        
        arcpy.SelectLayerByAttribute_management(outputSidcsLayer, "NEW_SELECTION", query)
        
        nullSidcCount = int(arcpy.GetCount_management(outputSidcsLayer).getOutput(0))
       
        self.assertEqual(nullSidcCount, int(0))

if __name__ == "__main__":
    unittest.main()        
