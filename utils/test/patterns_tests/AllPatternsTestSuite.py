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
AllPatternsTestSuite.py
--------------------------------------------------
requirments:
* ArcGIS Desktop 10.X+ or ArcGIS Pro 1.X+
* Python 2.7 or Python 3.4
author: ArcGIS Solutions
company: Esri
==================================================
description:
This test suite collects all of the patterns toolbox test suites:
* IncidentAnalysisToolsTestSuite.py

==================================================
history:
10/23/2015 - MF - placeholder
==================================================
'''

import logging
import unittest
import Configuration
from . import IncidentAnalysisToolsTestSuite


def getPatternsTestSuites():
    ''' This pulls together all of the toolbox test suites in this folder '''
    if Configuration.DEBUG == True:
        print("   AllPatternsTestSuite.getPatternsTestSuites")
    Configuration.Logger.info("Adding Patterns Tests including: ")
    testSuite = unittest.TestSuite()
    
    testSuite.addTests(IncidentAnalysisToolsTestSuite.getIncidentAnalysisTestSuite())
    return testSuite
    