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

import unittest
import logging
import Configuration

from . import DistanceToAssetsCodeAssetsToBasesTestCase
from . import DistanceToAssetsCopyGeolocatedLocationsTestCase
from . import DistanceToAssetsRouteAssetsToBasesLocalTestCase
from . import DistanceToAssetsRouteAssetsToBasesAGOLTestCase
from . import DistanceToAssetsSummarizeTestCase

''' Test suite for all tools in the Distance to Assets Tools toolbox '''

def getTestSuite():

    if Configuration.DEBUG == True:
        print("      DistanceToAssetsTestSuite.getSuite")

    testSuite = unittest.TestSuite()

    ''' Add the Distance to Assets tests '''

    loader = unittest.TestLoader()

    testSuite.addTest(loader.loadTestsFromTestCase(DistanceToAssetsCodeAssetsToBasesTestCase.DistanceToAssetsCodeAssetsToBasesTestCase))
    testSuite.addTest(loader.loadTestsFromTestCase(DistanceToAssetsCopyGeolocatedLocationsTestCase.DistanceToAssetsCopyGeolocatedLocationsTestCase))
    testSuite.addTest(loader.loadTestsFromTestCase(DistanceToAssetsRouteAssetsToBasesLocalTestCase.DistanceToAssetsRouteAssetsToBasesLocalTestCase))
    testSuite.addTest(loader.loadTestsFromTestCase(DistanceToAssetsRouteAssetsToBasesAGOLTestCase.DistanceToAssetsRouteAssetsToBasesAGOLTestCase))
    testSuite.addTest(loader.loadTestsFromTestCase(DistanceToAssetsSummarizeTestCase.DistanceToAssetsSummarizeTestCase))

    return testSuite
