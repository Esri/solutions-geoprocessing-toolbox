# coding: utf-8
'''
------------------------------------------------------------------------------
 Copyright 2015 - 2017 Esri
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
------------------------------------------------------------------------------
 TestRunner.py
------------------------------------------------------------------------------
 requirements:
 * ArcGIS Desktop 10.X+ or ArcGIS Pro 1.X+
 * Python 2.7 or Python 3.4
 author: ArcGIS Solutions
 company: Esri
==================================================
 description:
 Runs Individual Test Suite
==================================================
'''

import datetime
import logging
import os
import sys
import unittest

import arcpy

import Configuration
import UnitTestUtilities
import DataDownload
import TestRunner

logFileFromBAT = None
if len(sys.argv) > 1:
    logFileFromBAT = sys.argv[1] #if we have an explicit log file name passed in
    
def main():
    ''' main test logic '''
    print("TestRunner.py - main")

    if Configuration.DEBUG == True:
        print("Debug messaging is ON")
        logLevel = logging.DEBUG
    else:
        print("Debug messaging is OFF")
        logLevel = logging.INFO

    # setup logger
    if not logFileFromBAT == None:
        Configuration.Logger = UnitTestUtilities.initializeLogger(logFileFromBAT, logLevel)
    else:
        Configuration.GetLogger(logLevel)

    print("Logging results to: " + str(Configuration.LoggerFile))
    UnitTestUtilities.setUpLogFileHeader()

    result = runTestSuite()

    TestRunner.logTestResults(result)

    return result.wasSuccessful()
    
def runTestSuite():
    ''' collect all test suites before running them '''
    if Configuration.DEBUG == True: print("TestRunner.py - runTestSuite")
    testSuite = unittest.TestSuite()
    result = unittest.TestResult()

    #What Platform are we running on?
    Configuration.GetPlatform()
    Configuration.Logger.info('Running on Platform: ' + Configuration.Platform)

    testSuite.addTests(addMilitaryFeaturesSuite())

    Configuration.Logger.info("running " + str(testSuite.countTestCases()) + " tests...")

    # Run all of the tests added above
    testSuite.run(result)

    Configuration.Logger.info("Test success: {0}".format(str(result.wasSuccessful())))

    return result
    
def addMilitaryFeaturesSuite():
    ''' Add all MilitaryFeatures tests '''
    Configuration.Logger.debug("TestRunner.py - addMilitaryFeaturesSuite")
    from military_features_tests import MilitaryFeaturesToolsTestSuite
    suite = MilitaryFeaturesToolsTestSuite.getTestSuite()
    return suite

# MAIN =============================================
if __name__ == "__main__":
    if Configuration.DEBUG == True:
        print("Starting TestRunner.py")

    exitAsBoolean = main()

    exitAsCode = 0 if exitAsBoolean else 1

    sys.exit(exitAsCode)
