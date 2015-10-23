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
HelicopterLandingZonesTestSuitePro.py
--------------------------------------------------
requirments: ArcGIS 1.X, Python 3.4
author: ArcGIS Solutions
company: Esri
==================================================
description: This test suite runs the HLZ tools in ArcGIS Pro
using the 1.x version of the toolbox.
==================================================
history:
<date> - <initals> - <modifications>
==================================================
'''

import os
import sys
import datetime
import logging
import unittest
import TestUtilities
import UnitTestUtilities
import HLZTouchdownPointsTestCase


class HelicopterLandingZoneTestSuiteDesktop(unittest.TestSuite):
    ''' Test suite for all HLZ test for Desktop '''
    def addHLZTouchdownPoints001(self, suite):
        ''' add the test_HLZ_Touchdown_Points_001 test to the test suite'''
        suite.addTest(HLZTouchdownPointsTestCase.HLZTouchdownPoints('test_HLZ_Touchdown_Points_001'))
        return suite

    def addHLZTouchdownPoints002(self, suite):
        ''' add the test_HLZ_Touchdown_Points_002 test to the test suite'''
        suite.addTest(HLZTouchdownPointsTestCase.HLZTouchdownPoints('test_HLZ_Touchdown_Points_002'))
        return suite

    def addChooseFieldValueScriptTool(self, suite):
        ''' add the test_Choose_Field_Value_Script_Tool test to the test suite'''
        suite.addTest(HLZTouchdownPointsTestCase.HLZTouchdownPoints('test_Choose_Field_Value_Script_Tool'))
        return suite

    def addMinimumBoundingFishnet(self, suite):
        ''' add the test_MinimumBoundingFishnet test to the test suite'''
        suite.addTest(HLZTouchdownPointsTestCase.HLZTouchdownPoints('test_MinimumBoundingFishnet'))
        return suite

    def runHLZTestSuite(self, testSuite, logger):
        ''' run the HLZ tests in Desktop'''
        result = unittest.TestResult()
        sunPosPath = os.path.normpath(os.path.join(TestUtilities.currentPath, r"../../capability/test/test_hlz_tools/"))
        if sunPosPath not in sys.path:
            sys.path.insert(0, sunPosPath)
        from HLZTouchdownPointsTestCase import HLZTouchdownPoints
        tbxFolderPath = r"../../../capability/toolboxes/Helicopter Landing Zone Tools.tbx"

        # Setup the tests
        HLZTouchdownPoints.setUp(tbxFolderPath)
        # Add the tests in this test suite
        self.addHLZTouchdownPoints001(testSuite)
        self.addHLZTouchdownPoints002(testSuite)
        self.addChooseFieldValueScriptTool(testSuite)
        self.addMinimumBoundingFishnet(testSuite)
        # Cleanup after tests are run

        testSuite.run(result)
        print("Test success: {0}".format(str(result.wasSuccessful())))

        HLZTouchdownPoints.tearDown()

        return result
    