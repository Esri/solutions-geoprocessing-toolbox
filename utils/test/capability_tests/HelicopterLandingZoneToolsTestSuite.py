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
10/23/2015 - MF - initial coding started
==================================================
'''

import unittest
import Configuration
from . import HLZTouchdownPointsTestCase

def getHLZTestSuite(logger, platform):
    ''' run the HLZ tests as either Pro or Desktop'''

    desktopTestList = ['test_Choose_Field_Value_Script_Tool_Desktop',
                       'test_MinimumBoundingFishnet_Desktop',
                       'test_HLZ_Touchdown_Points_001_Desktop']
    proTestList = ['test_Choose_Field_Value_Script_Tool_Pro',
                   'test_MinimumBoundingFishnet_Pro',
                   'test_HLZ_Touchdown_Points_001_Pro']

    if Configuration.DEBUG == True:
        print("      HelicopterLandingZoneTestSuite.runHLZTestSuite")
    testSuite = unittest.TestSuite()
    if platform == "PRO":
        logger.info("Helicopter Landing Zone Tools Pro tests")
        testSuite = addTestFromList(testSuite, logger, proTestList)
    else:
        logger.info("Helicopter Landing Zone Tools Desktop tests...")
        testSuite = addTestFromList(testSuite, logger, desktopTestList)
    return testSuite

def addTestFromList(testSuite, logger, inputTestList):
    ''' add tests from list'''
    for p in inputTestList:
        if Configuration.DEBUG == True:
            print("      HelicopterLandingZoneTestSuite.addTestFromList")
        print("adding test: " + str(p))
        logger.info(p)
        testSuite.addTest(HLZTouchdownPointsTestCase.HLZTouchdownPoints(p))
    return testSuite
