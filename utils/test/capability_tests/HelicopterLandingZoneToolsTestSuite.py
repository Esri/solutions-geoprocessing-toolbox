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

import logging
import unittest
import HLZTouchdownPointsTestCase

class HelicopterLandingZoneTestSuite():
    ''' Test suite for all test cases for the Helicopter Landing Zone Tools toolbox '''

    # def runProTests(self, testSuite):
    #     ''' Set up the HLZ tests for Pro '''
    #     proTestList = ['test_Choose_Field_Value_Script_Tool_Pro',
    #                    'test_MinimumBoundingFishnet_Pro',
    #                    'test_HLZ_Touchdown_Points_001_Pro',
    #                    'test_HLZ_Touchdown_Points_002_Pro']
    #     for p in proTestList:
    #         testSuite.addTest(HLZTouchdownPointsTestCase.HLZTouchdownPoints(p))
    #     return testSuite

    # def runDesktopTests(self, testSuite):
    #     ''' Set up the HLZ tests for Desktop '''
    #     desktopTestList = ['test_Choose_Field_Value_Script_Tool_Desktop',
    #                        'test_MinimumBoundingFishnet_Desktop',
    #                        'test_HLZ_Touchdown_Points_001_Desktop',
    #                        'test_HLZ_Touchdown_Points_002_Desktop']
    #     for p in desktopTestList:
    #         testSuite.addTest(HLZTouchdownPointsTestCase.HLZTouchdownPoints(p))
    #     return testSuite

    def runHLZTestSuite(self, testSuite, logger, platform):
        ''' run the HLZ tests as either Pro or Desktop'''
        print("      HelicopterLandingZoneTestSuite.runHLZTestSuite")
        hlzTouchDown = HLZTouchdownPointsTestCase.HLZTouchdownPoints()


        if platform == "PRO":
            logger.info("Helicopter Landing Zone Tools Pro tests...")
            # testSuite.addTest(hlzTouchDown.test_Choose_Field_Value_Script_Tool_Pro(logger))
            # testSuite.addTest(hlzTouchDown.test_MinimumBoundingFishnet_Pro(logger))
            # testSuite.addTest(hlzTouchDown.test_HLZ_Touchdown_Points_001_Pro(logger))
            # testSuite.addTest(hlzTouchDown.test_HLZ_Touchdown_Points_002_Pro(logger))
            testSuite.addTest(hlzTouchDown('test_Choose_Field_Value_Script_Tool_Pro'))
            testSuite.addTest(hlzTouchDown('test_MinimumBoundingFishnet_Pro'))
            testSuite.addTest(hlzTouchDown('test_HLZ_Touchdown_Points_001_Pro'))
            testSuite.addTest(hlzTouchDown('test_HLZ_Touchdown_Points_002_Pro'))

        else:
            logger.info("Helicopter Landing Zone Tools Desktop tests...")
            #self.runDesktopTests(self, testSuite=testSuite)
            desktopTestList = ['test_Choose_Field_Value_Script_Tool_Desktop',
                               'test_MinimumBoundingFishnet_Desktop',
                               'test_HLZ_Touchdown_Points_001_Desktop',
                               'test_HLZ_Touchdown_Points_002_Desktop']
            for p in desktopTestList:
                testSuite.addTest(HLZTouchdownPointsTestCase.HLZTouchdownPoints(p))
        return testSuite
