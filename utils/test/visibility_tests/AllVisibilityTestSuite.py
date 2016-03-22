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
AllVisibilityTestSuite.py
--------------------------------------------------
requirments:
* ArcGIS Desktop 10.X+ or ArcGIS Pro 1.X+
* Python 2.7 or Python 3.4
author: ArcGIS Solutions
company: Esri
==================================================
description:
This test suite collects all of the visibility toolbox test suites:
* VisibilityAndRangeToolsTestSuite.py
* SunPositionAnalysisToolsTestSuite.py
* VisibilityDataPrepToolsTestSuite.py

==================================================
history:
12/4/2015 - JH - original writeup
==================================================
'''

import unittest
import Configuration
from . import SunPositionAnalysisToolsTestSuite

def getVisibilityTestSuites():
    ''' This pulls together all of the toolbox test suites in this folder '''
    if Configuration.DEBUG == True:
        print("   AllVisibilityTestSuite.getVisibilityTestSuites")
    Configuration.Logger.info("Adding Visibility Tests including: ")
    testSuite = unittest.TestSuite()
    
    testSuite.addTests(SunPositionAnalysisToolsTestSuite.getSunPositionTestSuite())
    return testSuite
    
