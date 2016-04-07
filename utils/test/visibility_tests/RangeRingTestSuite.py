# coding: utf-8
'''
-----------------------------------------------------------------------------
Copyright 2016 Esri
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
RangeRingTestSuite.py
--------------------------------------------------
requirments:
* ArcGIS Desktop 10.X+ or ArcGIS Pro 1.X+
* Python 2.7 or Python 3.4
author: ArcGIS Solutions
company: Esri
==================================================
description:
This test suite collects all of the @@@@@@@ toolbox test suites:


==================================================
history:
3/30/2016 - mf - original coding
==================================================
'''

import unittest
import Configuration
import RangeRingUtilsTestCase


def getRangeRingTestSuite():
    ''' Range Rings test suite '''

    desktopTestList = ['test_RingMaker_init',
                       'test_RingMaker_sortList_empty',
                       'test_RingMaker_sortList_isSorted',
                       'test_RingMaker_addFieldsToTable',
                       'test_RingMaker_makeTempTable',
                       'test_RingMaker_makeRingsFromDistances',
                       'test_RingMaker_saveRingsAsFeatures',
                       'test_RingMaker_makeRadials',
                       'test_RingMaker_saveRadialsAsFeatures',
                       'test_rangeRingsFromMinMax',
                       'test_rangeRingsFromList',
                       'test_rangeRingsFromInterval']

    proTestList = ['test_RingMaker_init',
                   'test_RingMaker_sortList_empty',
                   'test_RingMaker_sortList_isSorted',
                   'test_RingMaker_addFieldsToTable',
                   'test_RingMaker_makeTempTable',
                   'test_RingMaker_makeRingsFromDistances',
                   'test_RingMaker_saveRingsAsFeatures',
                   'test_RingMaker_makeRadials',
                   'test_RingMaker_saveRadialsAsFeatures',
                   'test_rangeRingsFromMinMax',
                   'test_rangeRingsFromList',
                   'test_rangeRingsFromInterval']

    if Configuration.DEBUG == True:
        print("      RangerRingTestSuite.getRangeRingTestSuite")

    suite = unittest.TestSuite()
    if Configuration.Platform == "PRO":
        Configuration.Logger.info("Range Rings Pro tests")
        suite = addTests(suite, proTestList)
    else:
        Configuration.Logger.info("Range Rings Desktop tests")
        suite = addTests(suite, desktopTestList)
    return suite


def addTests(suite, inputTestList):
    ''' Add the list of tests to the test suite '''
    if Configuration.DEBUG == True:
            print("      RangeRingTestSuite.addTests")
    for test in inputTestList:
        print("adding test: " + str(test))
        Configuration.Logger.info(test)
        suite.addTest(RangeRingUtilsTestCase.RangeRingUtilsTestCase(test))
    return suite
