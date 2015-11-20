# coding: utf-8
'''
-----------------------------------------------------------------------------
Copyright 2015 Esri
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
-----------------------------------------------------------------------------

==================================================
ERGScriptTestCase.py
--------------------------------------------------
requirements:
author: ArcGIS Solutions
company: Esri
==================================================
Description: Unit test for the ERG Script that drives the ERG By Placard and ERG By Chemical
tools.
The tool is based on the Emergency Response Guidebook (ERG) 2012 ed.:
http://phmsa.dot.gov/pv_obj_cache/pv_obj_id_7410989F4294AE44A2EBF6A80ADB640BCA8E4200/filename/ERG2012.pdf
(retrieved 11/11/2015)
References to page numbers in the tests below are from this book.

Includes the following tests:
* test_LookUpERG001
* 

==================================================
history:
11/09/2015 - MF - original coding
==================================================
'''

import arcpy
import os
import sys
import unittest
import TestUtilities
import UnitTestUtilities
from . import ERGTestUtils

#from . import ERG
sys.path.append(os.path.relpath(r'.\..\..\capability\toolboxes\scripts'))
#print('sys.path' + str(sys.path))
import ERG

class ERGTest(unittest.TestCase):
    ''' Test ERG source script for the ERG Tools toolbox'''

    scratchGDB = None
    scriptFolderPath = os.path.join(TestUtilities.repoPath, "capability",
                                    "toolboxes", "scripts", "ERG.py")
    dbfFolderPath = os.path.join(TestUtilities.repoPath, "capability",
                                 "toolboxes", "tooldata", "ERG2012LookupTable.dbf")
    testDataFolderPath = os.path.join(TestUtilities.capabilityPath, "data")

    def setUp(self):
        ''' set-up code '''
        if TestUtilities.DEBUG:
            print("         ERGScript.setUp")
        UnitTestUtilities.checkArcPy()
        UnitTestUtilities.checkFilePaths([self.scriptFolderPath,
                                          self.testDataFolderPath])

        # Check the test inputs (do they exist? or not?)
        if (self.scratchGDB == None) or (not arcpy.Exists(self.scratchGDB)):
            self.scratchGDB = UnitTestUtilities.createScratch(self.testDataFolderPath)
        UnitTestUtilities.checkGeoObjects([self.scratchGDB, self.dbfFolderPath])
        return

    def tearDown(self):
        ''' clean up after tests'''
        if TestUtilities.DEBUG:
            print("         ERGScript.tearDown")
        UnitTestUtilities.deleteScratch(self.scratchGDB)
        return

    ergDict = {
        '001': [1017, 124, 'Chlorine', 'Large', 'Day', 500.0, 3000.0],
        '002': [1076, 125, 'Phosgene', 'Small', 'Day', 100.0, 600.0],
        '003': [2810, 153, 'Sarin (when used as a weapon)', 'Large', 'Night', 400.0, 4900.0]
        }

    def test_LookUpERG001(self):
        '''
        test case one
        ERG Table 1, p292: ID No. 1017 Chlorine
        '''
        if TestUtilities.DEBUG:
            print("         ERGScript.test_LookUpERG001")
        inChemical = 'Chlorine'
        inPlacardID = 1017
        inSpillSize = 'Large' #'Large' or 'Small'
        inTimeOfDay = 'Day' #'Day' or 'Night'
        outResult = self.LookUpERG(inChemical, inPlacardID, inSpillSize, inTimeOfDay, self.dbfFolderPath)
        self.assertEqual(outResult[0], 500.0) # Initial Isolation Distance
        self.assertEqual(outResult[1], 3000.0) # Protective Action Distance
        self.assertEqual(outResult[2], 'Chlorine') # Materials
        self.assertEqual(outResult[3], 124) # GuideNum
        return

    def test_LookUpERG002(self):
        '''
        test case two
        ERG Table 1, p293: ID No. 1076 Phosgene
        '''
        if TestUtilities.DEBUG:
            print("         ERGScript.test_LookUpERG002")
        inChemical = 'Phosgene'
        inPlacardID = 1076
        inSpillSize = 'Small' #'Large' or 'Small'
        inTimeOfDay = 'Day' #'Day' or 'Night'
        outResult = self.LookUpERG(inChemical, inPlacardID, inSpillSize, inTimeOfDay, self.dbfFolderPath)
        self.assertEqual(outResult[0], 100.0) # Initial Isolation Distance
        self.assertEqual(outResult[1], 600.0) # Protective Action Distance
        self.assertEqual(outResult[2], 'Phosgene') # Materials
        self.assertEqual(outResult[3], 125) # GuideNum
        return

    def test_LookUpERG003(self):
        '''
        test case three
        ERG Table 1, p316: ID No. 2810 Sarin
        '''
        if TestUtilities.DEBUG == True: print("         ERGScript.test_LookUpERG003")
        inChemical = 'Sarin (when used as a weapon)'
        inPlacardID = 2810
        inSpillSize = 'Large' #'Large' or 'Small'
        inTimeOfDay = 'Night' #'Day' or 'Night'
        outResult = self.LookUpERG(inChemical, inPlacardID, inSpillSize, inTimeOfDay, self.dbfFolderPath)
        if TestUtilities.DEBUG == True: print("outResult: " + str(outResult))
        self.assertEqual(outResult[0], 400.0) # Initial Isolation Distance
        self.assertEqual(outResult[1], 4900.0) # Protective Action Distance
        #self.assertEqual(outResult[2], 'Sarin (when used as a weapon)') # Materials
        self.assertEqual(outResult[3], 153) # GuideNum
        return

    def LookUpERG(self, pChemical, pPlacardID, pSpillSize, pTimeOfDay, pERGdbf):
        ''' test ERG.py's LookUpERG submodule '''
        if TestUtilities.DEBUG:
            print("         ERGScript.LookUpERG: " + str(pChemical))
        outLookUpERGTuple = ERG.LookUpERG(pChemical, pPlacardID, pSpillSize, pTimeOfDay, pERGdbf)
        return outLookUpERGTuple

    def test_GetProjectedPoint001(self):
        ''' test case one '''
        inputPoint = ERGTestUtils.getInputPointFC()
        outputPoint = self.GetProjectedPoint(inputPoint)
        # desc = arcpy.Describe(outputPoint)
        # sr = desc.spatialReference
        sr = outputPoint.spatialReference
        self.assertEqual(sr.factoryCode, int(32643))
        return

    def test_GetProjectedPoint002(self):
        ''' test case two '''
        inputPoint = ERGTestUtils.getInputPointFCFromXY(-121.844234,36.586438) 
        outputPoint = self.GetProjectedPoint(inputPoint)
        # desc = arcpy.Describe(outputPoint)
        # sr = desc.spatialReference
        sr = outputPoint.spatialReference
        self.assertEqual(sr.factoryCode, int(32610))
        return

    def test_GetProjectedPoint003(self):
        ''' test case three '''
        inputPoint = ERGTestUtils.getInputPointFCFromXY(-68.609535, 46.178194) 
        outputPoint = self.GetProjectedPoint(inputPoint)
        # desc = arcpy.Describe(outputPoint)
        # sr = desc.spatialReference
        sr = outputPoint.spatialReference
        self.assertEqual(sr.factoryCode, int(32619))
        return

    def test_GetProjectedPoint004(self):
        ''' test case four '''
        inputPoint = ERGTestUtils.getInputPointFCFromXY(-98.233824, 26.654716) 
        outputPoint = self.GetProjectedPoint(inputPoint)
        # desc = arcpy.Describe(outputPoint)
        # sr = desc.spatialReference
        sr = outputPoint.spatialReference
        self.assertEqual(sr.factoryCode, int(32614))
        return

    def GetProjectedPoint(self, inputPoint):
        ''' test ERG.py's GetProjectedPoint submodule '''
        if TestUtilities.DEBUG == True: print("         ERGScript.GetProjectedPoint")
        #ERG.GetProjectedPoint(pPointFeatureRecordSet)
        outputPoint = ERG.GetProjectedPoint(inputPoint)
        return outputPoint

    # def test_MakeERGFeatures(self):
    #     ''' test ERG.py's MakeERGFeatures submodule '''
    #     #TODO: write test for MakeERGFeatures
    #     #ERG.MakeERGFeatures(pProjectedPointGeometry, pWindBlowingToDirection, pInitialIsolationDistance, pProtectiveActionDistance,
    #     #            pMaterials, pGuideNum, pSpillSize, pTimeOfDay, pOutAreas, pOutLines, pTemplateLoc)
    #     return
