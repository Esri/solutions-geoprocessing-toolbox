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
import Configuration
from . import ClusterAnalysisTestCase
from . import CountIncidentsByLOCTestCase
from . import FindPercentChangeTestCase
from . import HotSpotsByAreaTestCase
from . import IncidentDensityTestCase
from . import IncidentHotSpotsTestCase
from . import IncidentTableToPointTestCase

''' Test suite for all test cases for the Incident Analysis Tools toolbox '''

def getIncidentAnalysisTestSuite():
    ''' Run the Incident Analysis tests as either Pro or Desktop'''
        
    desktopTests = ['test_cluster_analysis_desktop']
    proTests = ['test_cluster_analysis_pro']
        
    if Configuration.DEBUG == True: print("     IncidentAnalysisToolsTestSuite.getIncidentAnalysisTestSuite")
        
    suite = unittest.TestSuite()
    if Configuration.Platform == "PRO":
        Configuration.Logger.info("Incident Analysis Tools Pro tests")
        suite = addTestsToSuite(suite, proTests)
    else:
        Configuration.Logger.info("Incident Analysis Tools Desktop tests")
        suite = addTestsToSuite(suite, desktopTests)

    return suite


def addTestsToSuite(testSuite, inputTestList):
    ''' Add the list of tests to the test suite '''
    if Configuration.DEBUG == True: print("      IncidentAnalysisToolsTestSuite.addTests")
    for test in inputTestList:
        print("adding test: " + str(test))
        Configuration.Logger.info(test)
        testSuite.addTest(ClusterAnalysisTestCase.ClusterAnalysisTestCase(test))
    return testSuite
        
    