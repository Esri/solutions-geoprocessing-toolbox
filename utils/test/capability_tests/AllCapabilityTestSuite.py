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
AllCapabilityTestSuite.py
--------------------------------------------------
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
* PointOfOriginToolsTestSuite.py - PENDING

==================================================
history:
10/23/2015 - MF - original writeup
==================================================
'''

import unittest
import Configuration

from . import HelicopterLandingZoneToolsTestSuite
# Getting an error on line above during run in Python 3.4:
#   File "C:\Users\<user>\Documents\GitHub\solutions-geoprocessing-toolbox\utils\test\capability_tests\AllCapabilityTestSuite.py", line 41, in <module>
#     import HelicopterLandingZoneToolsTestSuite
# ImportError: No module named 'HelicopterLandingZoneToolsTestSuite'
#FIX: instead of "import <module>" use "from . import <module>"

#from . import PointOfOriginToolsTestSuite - Doesn't Exist Yet
from . import ERGToolsTestSuite

def getCapabilityTestSuites():
    ''' This pulls together all of the toolbox test suites in this folder '''
    if Configuration.DEBUG == True:
        print("   AllCapabilityTestSuite.capabilityTestSuite")
    Configuration.Logger.info("Adding Capability Tests including:")
    testSuite = unittest.TestSuite()

    # these come from HelicopterLandingZoneToolsTestSuite.py
    testSuite.addTests(HelicopterLandingZoneToolsTestSuite.getHLZTestSuite())

    #TODO: these will come from PointOfOriginToolsTestSuite

    # these come from ERGToolsTestSuite.py
    testSuite.addTests(ERGToolsTestSuite.getERGTestSuite())
    return testSuite
