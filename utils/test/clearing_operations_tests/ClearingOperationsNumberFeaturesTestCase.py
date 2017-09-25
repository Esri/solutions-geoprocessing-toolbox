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
import arcpy
from arcpy.sa import *
import sys
import traceback
import datetime
import os

# Add parent folder to python path if running test case standalone
import sys
sys.path.append(os.path.normpath(os.path.join(os.path.dirname(__file__), '..')))

import unittest
import Configuration
import UnitTestUtilities
import DataDownload

class ClearingOperationsNumberFeaturesTestCase(unittest.TestCase):

    toolboxUnderTest = None # Set to Pro or ArcMap toolbox at runtime

    inputArea = None
    pointFeatures = None
    output = None
    scratchGDB = None

    def setUp(self):
        if Configuration.DEBUG == True: print("         ClearingOperationsNumberFeaturesTestCase.setUp")

        ''' Initialization needed if running Test Case standalone '''
        Configuration.GetLogger()
        Configuration.GetPlatform()
        ''' End standalone initialization '''
        self.toolboxUnderTest = Configuration.clearingOperationsToolboxPath

        UnitTestUtilities.checkArcPy()
        DataDownload.runDataDownload(Configuration.clearingOperationsPath, \
           Configuration.clearingOperationsInputGDB, Configuration.clearingOperationsURL)

        if (self.scratchGDB == None) or (not arcpy.Exists(self.scratchGDB)):
            self.scratchGDB = UnitTestUtilities.createScratch(Configuration.clearingOperationsPath)

        # set up inputs
        self.inputArea = os.path.join(Configuration.clearingOperationsInputGDB, r"AO")
        self.pointFeatures = os.path.join(Configuration.clearingOperationsInputGDB, r"Structures")

        UnitTestUtilities.checkFilePaths([Configuration.clearingOperationsPath])

        UnitTestUtilities.checkGeoObjects([Configuration.clearingOperationsInputGDB, self.toolboxUnderTest, self.scratchGDB, self.inputArea, self.pointFeatures])

    def tearDown(self):
        if Configuration.DEBUG == True: print("         ClearingOperationsNumberFeaturesTestCase.tearDown")
        UnitTestUtilities.deleteScratch(self.scratchGDB)

    def testClearingOperationsNumberFeatures(self):
        if Configuration.DEBUG == True:print(".....ClearingOperationsNumberFeaturesTestCase.testClearingOperationsNumberFeatures")
        print("Importing toolbox...")
        arcpy.ImportToolbox(self.toolboxUnderTest)
        arcpy.env.overwriteOutput = True

        #inputs
        fieldToNumber = "Number"
        output = os.path.join(self.scratchGDB, "numFields")

        # Start Test
        runToolMsg="Running tool (Number Features)"
        arcpy.AddMessage(runToolMsg)
        Configuration.Logger.info(runToolMsg)

        toolOutput = None

        try:
            #Calling the NumberFeatures_ClearingOperations Script Tool
            toolOutput = arcpy.NumberFeatures_clrops(self.inputArea, self.pointFeatures, fieldToNumber, output)
        except arcpy.ExecuteError:
            UnitTestUtilities.handleArcPyError()
        except:
            UnitTestUtilities.handleGeneralError()

        # 1: Check the expected return value (output feature class)
        if toolOutput is None:
            returnedValue = "BAD"
        else:
            returnedValue = toolOutput.getOutput(0)
        self.assertEqual(returnedValue, output)  

        # 2: Check the number of records
        result = arcpy.GetCount_management(output)
        count = int(result.getOutput(0))
        # print("number features: " + str(count))
        # Important only 90 of 120 records are in the area of interest
        self.assertEqual(count, 90)

        # 3: Check that the "number" field was created/updated for each row
        cursor = arcpy.SearchCursor(output)
        row = cursor.next()
        while row is not None:
            val = row.getValue(fieldToNumber)
            # Debug: print("Field number first row: " + str(val) + " should not be null")
            self.assertIsNotNone(val)
            row = cursor.next()

    def testClearingOperationsNumberFeatures_NoField(self):
        if Configuration.DEBUG == True:print(".....ClearingOperationsNumberFeaturesTestCase.testClearingOperationsNumberFeatures_NoField")
        print("Importing toolbox...")
        arcpy.ImportToolbox(self.toolboxUnderTest)
        arcpy.env.overwriteOutput = True

        ########################################################
        # Test steps:
        # 1. Copy a known feature class in the AOI to the scratch GDB
        # 2. Delete the "Number" field
        # 3. Run the NumberFeatures tool
        # 4. Verify the output
        ########################################################

        #inputs
        inputPoints = os.path.join(self.scratchGDB, 'numFieldsInput_NoField')
        inputFieldToNumber = 'Number'

        # Copy the features of the original input FC into the scratch GDB
        arcpy.CopyFeatures_management(self.pointFeatures, inputPoints)   

        # Delete the "fieldToNumber" field (so we can see if it gets set later)
        arcpy.DeleteField_management(inputPoints, inputFieldToNumber)

        fieldToNumber = None
        output = os.path.join(self.scratchGDB, "numFieldsOutput_NoField")

        # Start Test
        runToolMsg="Running tool (Number Features)"
        arcpy.AddMessage(runToolMsg)
        Configuration.Logger.info(runToolMsg)

        toolOutput = None

        try:
            #Calling the NumberFeatures_ClearingOperations Script Tool
            toolOutput = arcpy.NumberFeatures_clrops(self.inputArea, inputPoints, \
                fieldToNumber, output)
        except arcpy.ExecuteError:
            UnitTestUtilities.handleArcPyError()
        except:
            UnitTestUtilities.handleGeneralError()

        # 1: Check the expected return value (output feature class)
        if toolOutput is None:
            returnedValue = "BAD"
        else:
            returnedValue = toolOutput.getOutput(0)
        self.assertEqual(returnedValue, output)  

        # 2 Check the number of records
        result = arcpy.GetCount_management(output)
        count = int(result.getOutput(0))
        print("Number features: " + str(count))
        # Important only 90 of 120 records are in the area of interest
        self.assertEqual(count, 90)

        # 3: Check that the "number" field was created/updated for each row
        cursor = arcpy.SearchCursor(output)
        row = cursor.next()
        while row is not None:
            val = row.getValue("Number") #default field will still be 'Number'
            # Debug: print("Field number first row: " + str(val) + " should not be null")
            self.assertIsNotNone(val)
            row = cursor.next()

    # Added to test for: https://github.com/Esri/solutions-geoprocessing-toolbox/issues/607
    def testClearingOperationsNumberFeatures_NoOutputParam(self):
        if Configuration.DEBUG == True:print(".....ClearingOperationsNumberFeaturesTestCase.testClearingOperationsNumberFeatures_NoOutputParam")
        print("Importing toolbox...")
        arcpy.ImportToolbox(self.toolboxUnderTest)
        arcpy.env.overwriteOutput = True

        ########################################################
        # Test steps:
        # 1. Copy a known feature class in the AOI to the scratch GDB
        # 2. Add a new "Number" field (so will be blank)
        # 3. Run the NumberFeatures tool
        # 4. Verify the output
        ########################################################

        #inputs
        fieldToNumber = "NumberNewField"

        inputPoints = os.path.join(self.scratchGDB, 'numFieldsInput_NoOutput')

        # Copy the features of the original input FC into the scratch GDB
        arcpy.CopyFeatures_management(self.pointFeatures, inputPoints)   

        arcpy.AddField_management(inputPoints, fieldToNumber, "LONG")   

        # Start Test
        runToolMsg="Running tool (Number Features)"
        arcpy.AddMessage(runToolMsg)
        Configuration.Logger.info(runToolMsg)

        toolOutput = None

        try:
            #Calling the NumberFeatures_ClearingOperations Script Tool
            #No output parameter 
            toolOutput = arcpy.NumberFeatures_clrops(self.inputArea, inputPoints, \
                fieldToNumber)
        except arcpy.ExecuteError:
            UnitTestUtilities.handleArcPyError()
        except:
            UnitTestUtilities.handleGeneralError()

        # 1: Check the expected return value (output feature class)
        # TODO: this return value may change in the future, and this check may need updated
        expectedOutput = ""
        if toolOutput is None:
            returnedValue = "BAD"
        else:
            returnedValue = toolOutput.getOutput(0)
        self.assertEqual(returnedValue, expectedOutput)  

        #2: Check the Output Feature class has no rows without a null Number
        outputLayer = "Number_NoOutput"       
        arcpy.MakeFeatureLayer_management(inputPoints, outputLayer)
        query = '(' + fieldToNumber + ' is NOT NULL)'
        
        arcpy.SelectLayerByAttribute_management(outputLayer, "NEW_SELECTION", query)
        recordCount = int(arcpy.GetCount_management(outputLayer).getOutput(0))

        # Important only 90 of 120 records are in the area of interest
        self.assertEqual(recordCount, int(90))

if __name__ == "__main__":
    unittest.main()       