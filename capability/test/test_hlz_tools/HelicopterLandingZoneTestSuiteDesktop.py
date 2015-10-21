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
HelicopterLandingZoneTestSuiteDesktop.py
--------------------------------------------------
requirments: ArcGIS 10.X, Python 2.7
author: ArcGIS Solutions
company: Esri
==================================================
description: This test suite runs the HLZ tools in Desktop
using the 10.x version of the toolbox.
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

def main():
    ''' main test start '''
    logger = UnitTestUtilities.initializeLogger("Base")
    UnitTestUtilities.setUpLogFileHeader(logger)
    runTestSuite()

def addHLZTouchdownPoints001(suite):
    ''' add the test_HLZ_Touchdown_Points_001 test to the test suite'''
    suite.addTest(HLZTouchdownPoints('test_HLZ_Touchdown_Points_001'))
    return suite

def addHLZTouchdownPoints002(suite):
    ''' add the test_HLZ_Touchdown_Points_002 test to the test suite'''
    suite.addTest(HLZTouchdownPoints('test_HLZ_Touchdown_Points_002'))
    return suite

def addChooseFieldValueScriptTool(suite):
    ''' add the test_Choose_Field_Value_Script_Tool test to the test suite'''
    suite.addTest(HLZTouchdownPoints('test_Choose_Field_Value_Script_Tool'))
    return suite

def addMinimumBoundingFishnet(suite):
    ''' add the test_MinimumBoundingFishnet test to the test suite'''
    suite.addTest(HLZTouchdownPoints('test_MinimumBoundingFishnet'))
    return suite

def runTestSuite():
    ''' run the HLZ tests in Desktop'''
    testSuite = unittest.TestSuite()
    result = unittest.TestResult()

    tbxFolderPath = r"../../../capability/toolboxes/Helicopter Landing Zone Tools_10.3.tbx"
    HLZTouchdownPoints.setUp(tbxFolderPath)

    addHLZTouchdownPoints001(testSuite)
    addHLZTouchdownPoints002(testSuite)
    addChooseFieldValueScriptTool(testSuite)
    addMinimumBoundingFishnet(testSuite)

    HLZTouchdownPoints.tearDown()

    testSuite.run(result)
    print("Test success: {0}".format(str(result.wasSuccessful())))

# MAIN =============================================
if __name__ == "__main__":
    sunPosPath = os.path.normpath(os.path.join(TestUtilities.currentPath, r"../../capability/test/test_hlz_tools/"))
    if sunPosPath not in sys.path:
        sys.path.insert(0, sunPosPath)

    from HLZTouchdownPointsTestCase import HLZTouchdownPoints

    main()
    