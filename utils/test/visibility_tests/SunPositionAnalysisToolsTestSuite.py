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
    
def getSunPositionTestSuite(log, platform):
        
    desktopTestList = ["test_sun_position_analysis_desktop"]
        
    proTestList = ["test_sun_position_analysis_pro"]
        
    if Configuration.DEBUG == True:
        print("      SunPositionAnalysisTestSuite.getSunPositionTestSuite")
        
    suite = unittest.TestSuite()
    if platform == "PRO":
        log.info("Sun Position Analysis Tools Pro tests")
        suite = addTests(suite, log, proTestList)
    else:
        log.info("Sun Position Analysis Tools Desktop tests")
        suite = addTests(suite, log, desktopTestList)
    return suite
    
def addTests(suite, logger, inputTestList):
    for test in inputTestList:
        if Configuration.DEBUG == True:
            print("      SunPositionAnalysisTestSuite.addTests")
        print("adding test: " + str(test))
        logger.info(test)
        suite.addTest(SunPositionAndHillshadeTestCase.SunPositionAndHillshadeTestCase(test))
    return suite
        
    # def runDesktopTests(self, suite):
        # suite.addTest(SunPositionAndHillshadeTestCase.SunPositionAndHillshadeTestCase('test_sun_position_analysis_desktop'))
        # return suite
        
    # def runProTests(self, suite):
        # suite.addTest(SunPositionAndHillshadeTestCase.SunPositionAndHillshadeTestCase('test_sun_position_analysis_pro'))
        # return suite
        
    # def runSunPosAnalysisTestSuite(self, suite, platform):
        # result = unittest.TestResult()
        
        # if platform == "Pro":
            # Configuration.logger.info("Running Sun Position Analysis Test Suite for Pro...")
            # self.runProTests(suite)
        # elif platform == "Desktop":
            # Configuration.logger.info("Running Sun Position Analysis Test Suite for Desktop...")
            # self.runDesktopTests(suite)
            
        # suite.run(result)
        # print("Test success: {0}".format(str(result.wasSuccessful())))
        # Configuration.logger.debug("Test success: {0}".format(str(result.wasSuccessful())))
        # return result