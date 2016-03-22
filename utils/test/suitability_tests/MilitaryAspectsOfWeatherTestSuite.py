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
MilitaryAspectsOfWeatherTestSuite.py
--------------------------------------------------
requirments:
* ArcGIS Desktop 10.X+
* Python 2.7
author: ArcGIS Solutions
company: Esri
==================================================
description:
This test suite collects all of the Military Aspects of Weather toolbox test cases:
* ImportWMOStationDataTestCase.py
* ImportWMOStationsTestCase.py
* ImportCRUToRasterTestCase.py
* SubsetRasterWorkspaceTestCase.py
==================================================
history:
2/9/2016 - JH - creation
==================================================
'''

import logging
import unittest
import Configuration

TestSuite = unittest.TestSuite()

def getWeatherTestSuite():
    ''' Run the Military Aspects of Weather tests (Desktop only)'''
        
    importWMODataTests = ['test_import_wmo_station_data']
    importWMOStationsTests = ['test_import_wmo_stations']
    importCRUToRasterTests = ['test_import_cru_to_raster']
    subsetRasterWorkspaceTests = ['test_subset_raster_workspace']
          
    if Configuration.DEBUG == True: print("     MilitaryAspectsOfWeatherTestSuite.getWeatherTestSuite")
        
    if Configuration.Platform == "DESKTOP":
        Configuration.Logger.info("Military Aspects of Weather Desktop tests")
        addWMOStationsTests(importWMOStationsTests)
        addWMOStationDataTests(importWMODataTests)
        addCRUToRasterTests(importCRUToRasterTests)
        addSubsetRasterWorkspaceTests(subsetRasterWorkspaceTests)

    return TestSuite


def addWMOStationDataTests(inputTestList):
    if Configuration.DEBUG == True: print("      MilitaryAspectsOfWeatherTestSuite.addWMOStationDataTests")
    from . import ImportWMOStationDataTestCase
    for test in inputTestList:
        print("adding test: " + str(test))
        Configuration.Logger.info(test)
        TestSuite.addTest(ImportWMOStationDataTestCase.ImportWMOStationDataTestCase(test))
    
def addWMOStationsTests(inputTestList):
    if Configuration.DEBUG == True: print("      MilitaryAspectsOfWeatherTestSuite.addWMOStationsTests")
    from . import ImportWMOStationsTestCase
    for test in inputTestList:
        print("adding test: " + str(test))
        Configuration.Logger.info(test)
        TestSuite.addTest(ImportWMOStationsTestCase.ImportWMOStationsTestCase(test))
    
def addCRUToRasterTests(inputTestList):
    if Configuration.DEBUG == True: print("      MilitaryAspectsOfWeatherTestSuite.addCRUToRasterTests")
    from . import ImportCRUToRasterTestCase
    for test in inputTestList:
        print("adding test: " + str(test))
        Configuration.Logger.info(test)
        TestSuite.addTest(ImportCRUToRasterTestCase.ImportCRUToRasterTestCase(test))

def addSubsetRasterWorkspaceTests(inputTestList):
    if Configuration.DEBUG == True: print("      MilitaryAspectsOfWeatherTestSuite.addSubsetRasterWorkspaceTests")
    from . import SubsetRasterWorkspaceTestCase
    for test in inputTestList:
        print("adding test: " + str(test))
        Configuration.Logger.info(test)
        TestSuite.addTest(SubsetRasterWorkspaceTestCase.SubsetRasterWorkspaceTestCase(test))
    
    