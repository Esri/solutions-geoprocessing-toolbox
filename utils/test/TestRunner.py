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
import TestUtilities
import UnitTestUtilities

    
def main():
    logger = UnitTestUtilities.initializeLogger("Base")
    UnitTestUtilities.setUpLogFileHeader(logger)
    runTestSuite()

# def addPatternsTests(suite):
    # #suite.addTest(PatternToolOneTestCase('test_name'))
    # return suite
    
def addVisibilityTests(suite):
    suite.addTest(SunPositionAndHillshadeTestCase('test_sun_position_analysis'))
    suite.addTest(FindLocalPeaksTestCase('test_local_peaks'))
    return suite
    
def runTestSuite():
    testSuite = unittest.TestSuite()
    result = unittest.TestResult()
    addVisibilityTests(testSuite)
    testSuite.run(result)
    print("Test success: {0}".format(str(result.wasSuccessful())))
    
# MAIN =============================================
if __name__ == "__main__":
    sunPosPath = os.path.normpath(os.path.join(TestUtilities.currentPath, r"../../visibility/test/test_sun_position/"))
    visRangePath = os.path.normpath(os.path.join(TestUtilities.currentPath, r"../../visibility/test/test_viz_and_range/"))
    sys.path.insert(0, sunPosPath)
    sys.path.insert(0, visRangePath)
    from SunPositionAndHillshadeTestCase import SunPositionAndHillshadeTestCase
    from FindLocalPeaksTestCase import FindLocalPeaksTestCase
    main()
