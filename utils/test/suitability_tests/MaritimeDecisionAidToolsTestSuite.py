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
MaritimeDecisionAidToolsTestSuite.py
--------------------------------------------------
requirments:
* ArcGIS Desktop 10.X+ or ArcGIS Pro 1.X+
* Python 2.7 or Python 3.4
author: ArcGIS Solutions
company: Esri
==================================================
description:
This test suite collects all of the Maritime Decision Aid Tools toolbox test cases:
* FindSubmarinesTestCase.py
* FarthestOnCircleTestCase.py
* SubDepthRestrictionSuitabilityTestCase.py
* SubSpecificationsTestCase.py
* VisibilityRangeAtSeaTestCase.py
==================================================
history:
2/29/2016 - JH - creation
==================================================
'''

import logging
import unittest
import Configuration

TestSuite = unittest.TestSuite()

def getMaritimeTestSuite():
    ''' Run the Maritime Decision Aid Tools tests (Desktop and Pro)'''
        
    findSubmarineProTests = ['test_find_submarine_pro']
    findSubmarineDesktopTests = ['test_find_submarine_desktop']
    subDepthRestrictionSuitabilityProTests = ['test_sub_depth_restriction_suitability_pro']
    subDepthRestribtionSuitabilityDesktopTests = ['test_sub_depth_restriction_suitability_desktop']
    subSpecificationsProTests = ['test_sub_specifications_pro']
    subSpecificationsDesktopTests = ['test_sub_specifications_desktop']
    visibilityRangeAtSeaProTests = ['test_visibility_range_at_sea_pro']
    visibilityRangeAtSeaDesktopTests = ['test_visibility_range_at_sea_desktop']
    farthestOnCircleProTests = ['test_farthest_on_circle_pro']
    farthestOnCircleDesktopTests = ['test_farthest_on_circle_desktop']
    
    if Configuration.DEBUG == True: print("     MaritimeDecisionAidToolsTestSuite.getMaritimeTestSuite")
        
    if Configuration.Platform == "DESKTOP":
        Configuration.Logger.info("Maritime Decision Aid Tools Desktop tests")
        addFindSubmarineTests(findSubmarineDesktopTests)
        addSubDepthRestrictionTests(subDepthRestribtionSuitabilityDesktopTests)
        addSubSpecificationsTests(subSpecificationsDesktopTests)
        addVisibilityRangeTests(visibilityRangeAtSeaDesktopTests)
        addFarthestOnCircleTests(farthestOnCircleDesktopTests)
    
    else:
        Configuration.Logger.info("Maritime Decision Aid Tools Pro tests")
        addFindSubmarineTests(findSubmarineProTests)
        addSubDepthRestrictionTests(subDepthRestrictionSuitabilityProTests)
        addSubSpecificationsTests(subSpecificationsProTests)
        addVisibilityRangeTests(visibilityRangeAtSeaProTests)
        addFarthestOnCircleTests(farthestOnCircleProTests)

    return TestSuite


def addFindSubmarineTests(inputTestList):
    if Configuration.DEBUG == True: print("      MaritimeDecisionAidToolsTestSuite.addFindSubmarineTests")
    from . import FindSubmarinesTestCase
    for test in inputTestList:
        print("adding test: " + str(test))
        Configuration.Logger.info(test)
        TestSuite.addTest(FindSubmarinesTestCase.FindSubmarinesTestCase(test))
    
def addSubDepthRestrictionTests(inputTestList):
    if Configuration.DEBUG == True: print("      MaritimeDecisionAidToolsTestSuite.addSubDepthRestrictionTests")
    from . import SubDepthRestrictionSuitabilityTestCase
    for test in inputTestList:
        print("adding test: " + str(test))
        Configuration.Logger.info(test)
        TestSuite.addTest(SubDepthRestrictionSuitabilityTestCase.SubDepthRestrictionSuitabilityTestCase(test))
    
def addSubSpecificationsTests(inputTestList):
    if Configuration.DEBUG == True: print("      MaritimeDecisionAidToolsTestSuite.addSubSpecificationsTests")
    from . import SubSpecificationsTestCase
    for test in inputTestList:
        print("adding test: " + str(test))
        Configuration.Logger.info(test)
        TestSuite.addTest(SubSpecificationsTestCase.SubSpecificationsTestCase(test))

def addVisibilityRangeTests(inputTestList):
    if Configuration.DEBUG == True: print("      MaritimeDecisionAidToolsTestSuite.addVisibilityRangeTests")
    from . import VisibilityRangeAtSeaTestCase
    for test in inputTestList:
        print("adding test: " + str(test))
        Configuration.Logger.info(test)
        TestSuite.addTest(VisibilityRangeAtSeaTestCase.VisibilityRangeAtSeaTestCase(test))
        
def addFarthestOnCircleTests(inputTestList):
    if Configuration.DEBUG == True: print("      MaritimeDecisionAidToolsTestSuite.addFarthestOnCircleTests")
    from . import FarthestOnCircleTestCase
    for test in inputTestList:
        print("adding test: " + str(test))
        Configuration.Logger.info(test)
        TestSuite.addTest(FarthestOnCircleTestCase.FarthestOnCircleTestCase(test))
        
    
    