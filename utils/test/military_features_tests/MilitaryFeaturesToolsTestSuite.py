# coding: utf-8
#------------------------------------------------------------------------------
# Copyright 2017 Esri
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

from . import AppendMilitaryFeaturesTestCase
from . import AppendMessageFileTestCase

''' Test suite for all tools in the toolbox '''
    
def getTestSuite():
        
    if Configuration.DEBUG == True:
        print("      MilitaryFeaturesTestSuite.getSuite")
        
    testSuite = unittest.TestSuite()

    # IMPORTANT: this toolbox/suite does not run under Pro (ArcMap only)
    if Configuration.Platform == Configuration.PLATFORM_PRO :
        print('Skipping MilitaryFeatures Tests for Pro (ArcMap Only Tools)')
        return testSuite

    loader = unittest.TestLoader()

    ''' Add all the tests '''
    testSuite.addTest(loader.loadTestsFromTestCase(AppendMilitaryFeaturesTestCase.AppendMilitaryFeaturesTestCase))
    testSuite.addTest(loader.loadTestsFromTestCase(AppendMessageFileTestCase.AppendMessageFileTestCase))

    return testSuite
    