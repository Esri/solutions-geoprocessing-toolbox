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
requirements:
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

==================================================
history:
10/23/2015 - MF - intial coding started
04/25/2017 - EL - removed IncidentTableToPointTestCase.py
07/28/2017 - CM - Refactor
==================================================
'''

import unittest
import logging
import Configuration

from . import ClusterAnalysisTestCase
from . import CountIncidentsByLOCTestCase
from . import IncidentDensityTestCase
from . import HotSpotsByAreaTestCase
from . import IncidentHotSpotsTestCase
from . import FindPercentChangeTestCase

def getTestSuite():

    if Configuration.DEBUG == True: print("     IncidentAnalysisToolsTestSuite.getTestSuite")

    ''' Test suite for all test cases for the Incident Analysis Tools toolbox '''
    testSuite = unittest.TestSuite()

    ''' Add the Incident Analysis tests '''
 
    loader = unittest.TestLoader()

    testSuite.addTest(loader.loadTestsFromTestCase(ClusterAnalysisTestCase.ClusterAnalysisTestCase))
    testSuite.addTest(loader.loadTestsFromTestCase(CountIncidentsByLOCTestCase.CountIncidentsByLOCTestCase))
    testSuite.addTest(loader.loadTestsFromTestCase(IncidentDensityTestCase.IncidentDensityTestCase))
    testSuite.addTest(loader.loadTestsFromTestCase(HotSpotsByAreaTestCase.HotSpotsByAreaTestCase))
    testSuite.addTest(loader.loadTestsFromTestCase(IncidentHotSpotsTestCase.IncidentHotSpotsTestCase))
    testSuite.addTest(loader.loadTestsFromTestCase(FindPercentChangeTestCase.FindPercentChangeTestCase))

    return testSuite
        
    
