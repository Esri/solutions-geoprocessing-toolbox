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
#-----------------------------------------------------------------------------
# TestSunPositionAndHillshade.py
# Description: Test Sun Position Analysis Tools
# Requirements: ArcGIS Desktop Standard
# ----------------------------------------------------------------------------

import arcpy
from arcpy.sa import *
import sys
import traceback
import TestUtilities
import os
import time
import logging
import unittest

import UnitTestUtilities
import SunPositionAndHillshadeUnitTest

try:
    #logFile=os.path.join(TestUtilities.toolboxesPath, 'SunLog.log')
    logFile = "header.log"
    logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', filename=logFile, level=logging.DEBUG)
    UnitTestUtilities.setUpLogFileHeader()
    
    # one way to run the test - outputs to console only (that I know of)
    # suite = unittest.TestLoader().loadTestsFromTestCase(SunPositionAndHillshadeUnitTest.SunPositionAndHillshadeUnitTest)
    # unittest.TextTestRunner(verbosity=2).run(suite)
    
    # Call Unit Test code - output to log
    sunPosTestCase = SunPositionAndHillshadeUnitTest.SunPositionAndHillshadeUnitTest('test_sun_position_analysis')
    result = unittest.TestResult()
    sunPosTestCase.run(result)
    
    logging.info("Test success: {0}".format(str(result.wasSuccessful())))

except:
    # Get the traceback object
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]

    # Concatenate information together concerning the error into a message string
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n"\
        + str(sys.exc_info()[1])
    msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

    # Return python error messages for use in script tool or Python Window
    arcpy.AddError(pymsg)
    arcpy.AddError(msgs)

    # Print Python error messages for use in Python / Python Window
    print(pymsg + "\n")
    print(msgs)

    # return a system error code
    sys.exit(-1)
