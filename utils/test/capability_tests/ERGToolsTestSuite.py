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
ERGToolsTestSuite.py
--------------------------------------------------
requirments:
* ArcGIS Desktop 10.X+ or ArcGIS Pro 1.X+
* Python 2.7 or Python 3.4
author: ArcGIS Solutions
company: Esri
==================================================
description:
Test Suite collects all of the test cases for the ERG Tools toolbox:
* ERGByPlacardTestCase.py
* ERGByChemicalTestCase.py
* ERGScriptTestCase.py

==================================================
history:
11/09/2015 - MF - placeholder
==================================================
'''

import unittest
import Configuration
from . import ERGByPlacardTestCase
from . import ERGByChemicalTestCase
from . import ERGScriptTestCase

def getERGTestSuite():
    ''' run the HLZ tests as either Pro or Desktop'''

    if Configuration.DEBUG == True:
        print("      ERGTestSuite.runERGTestSuite")

    placardTests = ['test_ERGByPlacard_001', 'test_ERGByPlacard_002']
    chemicalTests = ['test_ERGByChemical_001', 'test_ERGByChemical_002', 'test_ERGByChemical_003']
    scriptTests = ['test_LookUpERG001', 'test_LookUpERG002', 'test_LookUpERG003',
                   'test_GetProjectedPoint001', 'test_GetProjectedPoint002',
                   'test_GetProjectedPoint003', 'test_GetProjectedPoint004']
    testSuite = unittest.TestSuite()
    Configuration.Logger.info("ERG Tools tests")

    for t in chemicalTests:
        testSuite.addTest(ERGByChemicalTestCase.ERGByChemical(t))
        print("adding test: " + str(t))
        Configuration.Logger.info(t)

    for t in placardTests:
        testSuite.addTest(ERGByPlacardTestCase.ERGByPlacard(t))
        print("adding test: " + str(t))
        Configuration.Logger.info(t)

    for t in scriptTests:
        testSuite.addTest(ERGScriptTestCase.ERGTest(t))
        print("adding test: " + str(t))
        Configuration.Logger.info(t)

    return testSuite
