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
IncidentAnalysisToolsTestSuite.py
--------------------------------------------------
requirments:
* ArcGIS Desktop 10.X+ or ArcGIS Pro 1.X+
* Python 2.7 or Python 3.4
author: ArcGIS Solutions
company: Esri
==================================================
description:
This test suite collects all of the Incident Analysis Tools toolbox test cases:
* ClusterAnalysisTestCase.py
* CountIncidentsByLOCTestCase.py
* FindPercentChangeTestCase.py
* HotSpotsByAreaTestCase.py
* IncidentDensityTestCase.py
* IncidentHotSpotsTestCase.py
* IncidentTableToPointTestCase.py

==================================================
history:
10/23/2015 - MF - intial coding started
==================================================
'''

import logging
import unittest
import ClusterAnalysisTestCase
import CountIncidentsByLOCTestCase
import FindPercentChangeTestCase
import HotSpotsByAreaTestCase
import IncidentDensityTestCase
import IncidentHotSpotsTestCase
import IncidentTableToPointTestCase

def getIncidentTestSuite(logger, platform):
    ''' run the Incident Analysis tests as either Pro or Desktop'''
    testSuite = unittest.TestSuite()

    if platform == "PRO":
        logger.info("Incident Analysis Tools Pro tests")
        testSuite = addTestFromList(testSuite, logger)

    else:
        logger.info("Incident Analysis Tools Desktop tests...")
        testSuite = addTestFromList(testSuite, logger)

    return result

def addTestFromList(testSuite, logger):
    ''' add tests from CountIncidentsByLOCTestCase'''

    proTests = []
    desktopTests = []

    for p in inputTestList:

        print("adding test: " + str(p))
        logger.info(p)
        #testSuite.addTest(HLZTouchdownPointsTestCase.HLZTouchdownPoints(p))
        testSuite.addTest(CountIncidentsByLOCTestCase.CountIncidentsByLOC(p))

    return testSuite
