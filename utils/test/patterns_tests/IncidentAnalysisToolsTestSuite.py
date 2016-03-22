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
IncidentAnalysisToolsTestSuite.py
--------------------------------------------------
requirements:
* ArcGIS Desktop 10.X+ or ArcGIS Pro 1.X+
* Python 2.7 or Python 3.4
author: ArcGIS Solutions
company: Esri
==================================================
description:
This test suite collects all of the Incident Analysis Tools toolbox test cases:
* ClusterAnalysisTestCase.py
* CountIncidentsByLOCTestCase.py
* FindPercentChangeTestCase.py
* HotSpotsByAreaTestCase.py
* IncidentDensityTestCase.py
* IncidentHotSpotsTestCase.py
* IncidentTableToPointTestCase.py

==================================================
history:
10/23/2015 - MF - intial coding started
==================================================
'''

import logging
import unittest
import Configuration

''' Test suite for all test cases for the Incident Analysis Tools toolbox '''
TestSuite = unittest.TestSuite()

def getIncidentAnalysisTestSuite():
    ''' Run the Incident Analysis tests as either Pro or Desktop'''
        
    cluster_desktopTests = ['test_cluster_analysis_desktop']
    cluster_proTests = ['test_cluster_analysis_pro']
    count_desktopTests = ['test_count_incidents_desktop']
    count_proTests = ['test_count_incidents_pro']
    density_desktopTests = ['test_incident_density_desktop']
    density_proTests = ['test_incident_density_pro']
    hotSpots_desktopTests = ['test_hot_spots_by_area_desktop']
    hotSpots_proTests = ['test_hot_spots_by_area_pro']
    incidentHotSpots_desktopTests = ['test_incident_hot_spots_desktop']
    incidentHotSpots_proTests = ['test_incident_hot_spots_pro']
    tabletoPoint_desktopTests = ['test_incident_table_to_point_desktop']
    tabletoPoint_proTests = ['test_incident_table_to_point_pro']
    percentChange_desktopTests = ['test_percent_change_desktop']
    percentChange_proTests = ['test_percent_change_pro']
        
    if Configuration.DEBUG == True: print("     IncidentAnalysisToolsTestSuite.getIncidentAnalysisTestSuite")
        
    if Configuration.Platform == "PRO":
        Configuration.Logger.info("Incident Analysis Tools Pro tests")
        addClusterTests(cluster_proTests)
        addCountIncidentTests(count_proTests)
        addIncidentDensityTests(density_proTests)
        addHotSpotsByAreaTests(hotSpots_proTests)
        addIncidentHotSpotsTests(incidentHotSpots_proTests)
        addIncidentTableToPointTests(tabletoPoint_proTests)
        addFindPercentChangeTests(percentChange_proTests)
    else:
        Configuration.Logger.info("Incident Analysis Tools Desktop tests")
        addClusterTests(cluster_desktopTests)
        addCountIncidentTests(count_desktopTests)
        addIncidentDensityTests(density_desktopTests)
        addHotSpotsByAreaTests(hotSpots_desktopTests)
        addIncidentHotSpotsTests(incidentHotSpots_desktopTests)
        addIncidentTableToPointTests(tabletoPoint_desktopTests)
        addFindPercentChangeTests(percentChange_desktopTests)

    return TestSuite


def addClusterTests(inputTestList):
    if Configuration.DEBUG == True: print("      IncidentAnalysisToolsTestSuite.addClusterTests")
    from . import ClusterAnalysisTestCase
    for test in inputTestList:
        print("adding test: " + str(test))
        Configuration.Logger.info(test)
        TestSuite.addTest(ClusterAnalysisTestCase.ClusterAnalysisTestCase(test))
    
def addCountIncidentTests(inputTestList):
    if Configuration.DEBUG == True: print("      IncidentAnalysisToolsTestSuite.addCountIncidentTests")
    from . import CountIncidentsByLOCTestCase
    for test in inputTestList:
        print("adding test: " + str(test))
        Configuration.Logger.info(test)
        TestSuite.addTest(CountIncidentsByLOCTestCase.CountIncidentsByLOCTestCase(test))
    
def addIncidentDensityTests(inputTestList):
    if Configuration.DEBUG == True: print("      IncidentAnalysisToolsTestSuite.addIncidentDensityTests")
    from . import IncidentDensityTestCase
    for test in inputTestList:
        print("adding test: " + str(test))
        Configuration.Logger.info(test)
        TestSuite.addTest(IncidentDensityTestCase.IncidentDensityTestCase(test))

def addHotSpotsByAreaTests(inputTestList):
    if Configuration.DEBUG == True: print("      IncidentAnalysisToolsTestSuite.addHotSpotsByAreaTests")
    from . import HotSpotsByAreaTestCase
    for test in inputTestList:
        print("adding test: " + str(test))
        Configuration.Logger.info(test)
        TestSuite.addTest(HotSpotsByAreaTestCase.HotSpotsByAreaTestCase(test))
     
def addIncidentHotSpotsTests(inputTestList):
    if Configuration.DEBUG == True: print("      IncidentAnalysisToolsTestSuite.addIncidentHotSpotsTests")
    from . import IncidentHotSpotsTestCase
    for test in inputTestList:
        print("adding test: " + str(test))
        Configuration.Logger.info(test)
        TestSuite.addTest(IncidentHotSpotsTestCase.IncidentHotSpotsTestCase(test))
        
def addIncidentTableToPointTests(inputTestList):
    if Configuration.DEBUG == True: print("      IncidentAnalysisToolsTestSuite.addIncidentTableToPointTests")
    from . import IncidentTableToPointTestCase
    for test in inputTestList:
        print("adding test: " + str(test))
        Configuration.Logger.info(test)
        TestSuite.addTest(IncidentTableToPointTestCase.IncidentTableToPointTestCase(test))

def addFindPercentChangeTests(inputTestList):
    if Configuration.DEBUG == True: print("      IncidentAnalysisToolsTestSuite.addFindPercentChangeTests")
    from . import FindPercentChangeTestCase
    for test in inputTestList:
        print("adding test: " + str(test))
        Configuration.Logger.info(test)
        TestSuite.addTest(FindPercentChangeTestCase.FindPercentChangeTestCase(test))
        
    