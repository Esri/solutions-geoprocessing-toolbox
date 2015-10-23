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
HelicopterLandingZoneTestSuite.py
--------------------------------------------------
requirments:
* ArcGIS Desktop 10.X+ or ArcGIS Pro 1.X+
* Python 2.7 or Python 3.4
author: ArcGIS Solutions
company: Esri
==================================================
description:
This test suite collects all of the test cases for the
Helicopter Landing Zone Tools toolboxes:
* HLZTouchdownPointsTestCase.py

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


class HelicopterLandingZoneTestSuite(unittest.TestSuite):
    ''' Test suite for all tools in the Helicopter Landing Zone Tools toolbox '''


    def runProTests(self, suite):
        suite.addTest(HLZTouchdownPointsTestCase.HLZTouchdownPoints('test_Choose_Field_Value_Script_Tool_Pro'))
        suite.addTest(HLZTouchdownPointsTestCase.HLZTouchdownPoints('test_MinimumBoundingFishnet_Pro'))
        suite.addTest(HLZTouchdownPointsTestCase.HLZTouchdownPoints('test_HLZ_Touchdown_Points_001_Pro'))
        suite.addTest(HLZTouchdownPointsTestCase.HLZTouchdownPoints('test_HLZ_Touchdown_Points_002_Pro'))
        return suite

    def runDesktopTests(self, suite):
        suite.addTest(HLZTouchdownPointsTestCase.HLZTouchdownPoints('test_Choose_Field_Value_Script_Tool_Desktop'))
        suite.addTest(HLZTouchdownPointsTestCase.HLZTouchdownPoints('test_MinimumBoundingFishnet_Desktop'))
        suite.addTest(HLZTouchdownPointsTestCase.HLZTouchdownPoints('test_HLZ_Touchdown_Points_001_Desktop'))
        suite.addTest(HLZTouchdownPointsTestCase.HLZTouchdownPoints('test_HLZ_Touchdown_Points_002_Desktop'))
        return suite

    def runHLZTestSuite(self, testSuite, platform):
        ''' run the HLZ tests in Desktop'''
        result = unittest.TestResult()
        sunPosPath = os.path.normpath(os.path.join(TestUtilities.currentPath, r"../../capability/test/test_hlz_tools/"))
        if sunPosPath not in sys.path:
            sys.path.insert(0, sunPosPath)

        from HLZTouchdownPointsTestCase import HLZTouchdownPoints

        if platform == "PRO":
            self.runProTests(testSuite)
        else:
            self.runDesktopTests(testSuite)

        testSuite.run(result)
        print("Test success: {0}".format(str(result.wasSuccessful())))

        return result
