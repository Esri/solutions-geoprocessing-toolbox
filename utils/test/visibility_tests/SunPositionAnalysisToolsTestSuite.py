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
SunPositionAnalysisToolsTestSuite.py
--------------------------------------------------
requirments:
* ArcGIS Desktop 10.X+ or ArcGIS Pro 1.X+
* Python 2.7 or Python 3.4
author: ArcGIS Solutions
company: Esri
==================================================
description:
This test suite collects all of the test cases for the
Sun Position Analysis Tools toolboxes:
* SunPositionAndHillshadeTestCase.py

==================================================
history:
10/29/2015 - JH - wired up SunPositionAnalysisToolsTestSuite to run SunPositionAndHillshadeTestCase in Pro or Desktop
==================================================
'''

import os
import unittest
import logging
from . import SunPositionAndHillshadeTestCase
import Configuration

''' Test suite for all tools in the Sun Position Analysis Tools toolbox '''
    
def getSunPositionTestSuite():
        
    desktopTestList = ["test_sun_position_analysis_desktop"]
        
    proTestList = ["test_sun_position_analysis_pro"]
        
    if Configuration.DEBUG == True:
        print("      SunPositionAnalysisTestSuite.getSunPositionTestSuite")
        
    suite = unittest.TestSuite()
    if Configuration.Platform == "PRO":
        Configuration.Logger.info("Sun Position Analysis Tools Pro tests")
        suite = addTests(suite, proTestList)
    else:
        Configuration.Logger.info("Sun Position Analysis Tools Desktop tests")
        suite = addTests(suite, desktopTestList)
    return suite
    
def addTests(suite, inputTestList):
    ''' Add the list of tests to the test suite '''
    if Configuration.DEBUG == True:
            print("      SunPositionAnalysisTestSuite.addTests")
    for test in inputTestList: 
        print("adding test: " + str(test))
        Configuration.Logger.info(test)
        suite.addTest(SunPositionAndHillshadeTestCase.SunPositionAndHillshadeTestCase(test))
    return suite
    