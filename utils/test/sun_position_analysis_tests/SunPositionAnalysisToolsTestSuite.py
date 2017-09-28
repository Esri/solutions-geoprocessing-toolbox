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
07/28/2017 - CM - Refactor
==================================================
'''

import unittest
import logging
import Configuration

from . import SunPositionAndHillshadeTestCase

''' Test suite for all tools in the Sun Position Analysis Tools toolbox '''
    
def getTestSuite():
        
    if Configuration.DEBUG == True:
        print("      SunPositionAnalysisTestSuite.getSuite")
        
    testSuite = unittest.TestSuite()

    ''' Add the Sun Position tests '''
 
    loader = unittest.TestLoader()

    testSuite.addTest(loader.loadTestsFromTestCase(SunPositionAndHillshadeTestCase.SunPositionAndHillshadeTestCase))

    return testSuite
    