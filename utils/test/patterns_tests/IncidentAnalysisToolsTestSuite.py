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

class IncidentAnalysisToolsTestSuite(unittest.TestSuite):
    ''' Test suite for all test cases for the Incident Analysis Tools toolbox '''

    def runProTests(self, suite):
        ''' Set up the Incident test for Pro'''
        # suite.addTest(HLZTouchdownPointsTestCase.HLZTouchdownPoints('test_Choose_Field_Value_Script_Tool_Pro'))
        return suite

    def runDesktopTests(self, suite):
        ''' Set up the Incident tests for Desktop'''
        # suite.addTest(HLZTouchdownPointsTestCase.HLZTouchdownPoints('test_Choose_Field_Value_Script_Tool_Desktop'))
        return suite

    def runIncidentTests(self, testSuite, platform):
        ''' run the Incident Analysis tests as either Pro or Desktop'''
        result = unittest.TestResult()

        if platform == "PRO":
            self.runProTests(testSuite)
        else:
            self.runDesktopTests(testSuite)

        testSuite.run(result)
        print("Test success: {0}".format(str(result.wasSuccessful())))

        return result
