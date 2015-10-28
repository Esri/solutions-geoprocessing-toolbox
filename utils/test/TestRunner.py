# coding: utf-8
#------------------------------------------------------------------------------
# Copyright 2015 Esri
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#------------------------------------------------------------------------------
# TestRunner.py
#------------------------------------------------------------------------------

import os
import sys
import datetime
import logging
import unittest
import arcpy
import TestUtilities
import UnitTestUtilities

def main():
    print("TestRunner.py - main")
    logger = UnitTestUtilities.initializeLogger("Base")
    UnitTestUtilities.setUpLogFileHeader(logger)
    runTestSuite(logger)

def runTestSuite(logger):
    print("TestRunner.py - runTestSuite")
    testSuite = unittest.TestSuite()
    result = unittest.TestResult()

    #What are we working with?
    platform = "DESKTOP"
    if arcpy.GetInstallInfo()['ProductName'] == 'ArcGISPro':
        platform = "PRO"

    testSuite.addTests(addCapabilitySuite(testSuite, logger, platform))
    #addDataManagementTests(testSuite, logger, platform)
    #addOperationalGraphicsTests(testSuite, logger, platform)
    #addPatternsTests(testSuite, logger, platform)
    #addSuitabilityTests(testSuite, logger, platform)
    #addVisibilityTests(testSuite, logger, platform)

    print("running testSuite...")
    testSuite.run(result)
    print("Test success: {0}".format(str(result.wasSuccessful())))


def addCapabilitySuite(testSuite, logger, platform):
    ''' Add all Capability tests in the ./capability_tests folder'''
    print("TestRunner.py - addCapabilitySuite")
    sys.path.insert(0, TestUtilities.capabilityPath)
    import AllCapabilityTestSuite
    capability = AllCapabilityTestSuite
    tests = capability.AllCapabilityTestSuite.capabilityTestSuite(capability, testSuite, logger, platform)
    return tests

# def addPatternsTests(suite):
    # #suite.addTest(PatternToolOneTestCase('test_name'))
    # return suite

def addVisibilityTests(suite):
    print("TestRunner.py - addVisibilityTests")
    suite.addTest(SunPositionAndHillshadeTestCase('test_sun_position_analysis'))
    suite.addTest(FindLocalPeaksTestCase('test_local_peaks'))
    return suite

# MAIN =============================================
if __name__ == "__main__":
    print("TestRunner.py")
    # sunPosPath = os.path.normpath(os.path.join(TestUtilities.currentPath, r"../../visibility/test/test_sun_position/"))
    # visRangePath = os.path.normpath(os.path.join(TestUtilities.currentPath, r"../../visibility/test/test_viz_and_range/"))
    # sys.path.insert(0, sunPosPath)
    # sys.path.insert(0, visRangePath)
    # from SunPositionAndHillshadeTestCase import SunPositionAndHillshadeTestCase
    # from FindLocalPeaksTestCase import FindLocalPeaksTestCase

    main()
