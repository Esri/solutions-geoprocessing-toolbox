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
11/23/2015 - MF - add Incident Analysis tools test suite
==================================================
'''

import unittest
import TestUtilities
from . import IncidentAnalysisToolsTestSuite

def getPatternsTestSuites(logger, platform):
    ''' This pulls together all of the toolbox test suites in this folder '''
    logger.info("Adding Patterns Tests including:")
    testSuite = unittest.TestSuite()

    # these come from IncidentAnalysisToolsTestSuite.py
    testSuite.addTests(IncidentAnalysisToolsTestSuite.getIncidentTestSuite(logger, platform))

    #TODO: Add tests for Movement Analysis Tools.tbx (Pro only)

    return testSuite
