# coding: utf-8
'''
------------------------------------------------------------------------------
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
 This test suite collects all of the capability toolbox test suites:
 * HelicopterLandingZoneToolsTestSuite.py
 * ERGToolsTestSuite.py
 * PointOfOriginToolsTestSuite.py

==================================================
 history:
 10/06/2015 - MF - placeholder
 10/30/2015 - MF - tests running
==================================================
'''

import os
import sys
import datetime
import logging
import unittest
import arcpy
import Configuration
import UnitTestUtilities
import DataDownload


logFileFromBAT = None
if len(sys.argv) > 1:
    logFileFromBAT = sys.argv[1] #if we have an explicit log file name passed in

def main():
    ''' main test logic '''
    testStartDateTime = datetime.datetime.now()
    if Configuration.DEBUG == True:
        print("TestRunner.py - main")
    else:
        print("Debug messaging is OFF")

    # setup logger
    logName = None
    logger = None
    if not logFileFromBAT == None:
        logName = logFileFromBAT
        logger = UnitTestUtilities.initializeLogger(logFileFromBAT)
    else:
        logName = UnitTestUtilities.getLoggerName()
        logger = UnitTestUtilities.initializeLogger(logName)
    print("Logging results to: " + str(logName))
    UnitTestUtilities.setUpLogFileHeader(logger)
    
    # download the data
    # didDownload = DataDownload.runDataDownload(Configuration.visibilityPaths, "test_sun_position.gdb", DataDownload.sunPosUrl)
    # print("Downloaded data? " + str(didDownload))
    
    # run the tests
    result = runTestSuite(logger)
    # send to log file
    testEndDateTime = datetime.datetime.now()
    primaryLogFile(result, logger)
    print("END OF TEST =========================================\n")

    del logger
    return

def primaryLogFile(result, logger):
    ''' Write the log file '''
    resultHead = resultsHeader(result)
    print(resultHead)
    logger.info(resultHead)
    if len(result.errors) > 0:
        rError = resultsErrors(result)
        print(rError)
        logger.error(rError)
    if len(result.failures) > 0:
        rFail = resultsFailures(result)
        print(rFail)
        logger.error(rFail)
    logger.info("END OF TEST =========================================\n")

    return

def resultsHeader(result):
    ''' Generic header for the results in the log file '''
    msg = "RESULTS =================================================\n\n"
    msg += "Number of tests run: " + str(result.testsRun) + "\n"
    msg += "Number of errors: " + str(len(result.errors)) + "\n"
    msg += "Number of failures: " + str(len(result.failures)) + "\n"
    return msg

def resultsErrors(result):
    ''' Error results formatting '''
    msg = "ERRORS =================================================\n\n"
    for i in result.errors:
        for j in i:
            msg += str(j)
        msg += "\n"
    return msg

def resultsFailures(result):
    ''' Assert failures formatting '''
    msg = "FAILURES ===============================================\n\n"
    for i in result.failures:
        for j in i:
            msg += str(j)
        msg += "\n"
    return msg
   

def runTestSuite(logger):
    ''' collect all test suites before running them '''
    if Configuration.DEBUG == True: print("TestRunner.py - runTestSuite")
    testSuite = unittest.TestSuite()
    result = unittest.TestResult()

    #What are we working with?
    platform = "DESKTOP"
    if arcpy.GetInstallInfo()['ProductName'] == 'ArcGISPro':
        platform = "PRO"
    logger.info(platform + " =======================================")

    testSuite.addTests(addVisibilitySuite(logger, platform))
    testSuite.addTests(addCapabilitySuite(logger, platform))
    #addDataManagementTests(logger, platform)
    #addOperationalGraphicsTests(logger, platform)
    #addPatternsTests(logger, platform)
    #addSuitabilityTests(logger, platform)
    #testSuite.addTests(addVisibilityTests(logger, platform))

    print("running " + str(testSuite.countTestCases()) + " tests...")
    testSuite.run(result)
    print("Test success: {0}".format(str(result.wasSuccessful())))
    return result


def addCapabilitySuite(logger, platform):
    ''' Add all Capability tests in the ./capability_tests folder '''
    if Configuration.DEBUG == True: print("TestRunner.py - addCapabilitySuite")
    from capability_tests import AllCapabilityTestSuite
    testSuite = unittest.TestSuite()
    testSuite.addTests(AllCapabilityTestSuite.getCapabilityTestSuites(logger, platform))
    return testSuite

# def addPatternsTests(suite):
    # #suite.addTest(PatternToolOneTestCase('test_name'))
    # return suite

def addVisibilitySuite(logger, platform):
    ''' Add all Visibility tests in the ./visibility_tests folder '''
    if Configuration.DEBUG == True: print("TestRunner.py - addVisibilitySuite")
    from visibility_tests import AllVisibilityTestSuite    
    suite = unittest.TestSuite()
    suite.addTests(AllVisibilityTestSuite.getVisibilityTestSuites(logger, platform))
    # suite.addTest(SunPositionAndHillshadeTestCase('test_sun_position_analysis'))
    # suite.addTest(FindLocalPeaksTestCase('test_local_peaks'))
    return suite

# MAIN =============================================
if __name__ == "__main__":
    if Configuration.DEBUG == True:
        print("TestRunner.py")
    main()
