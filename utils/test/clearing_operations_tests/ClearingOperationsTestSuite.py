import unittest
import logging
import Configuration

from . import ClearingOperationsPointTargetTestCase
from . import ClearingOperationsCanvasAreaGRGTestCase
from . import ClearingOperationsNumberFeaturesTestCase


''' Test suite for all tools in the Clearing Operationss Tools toolbox '''

def getTestSuite():

    if Configuration.DEBUG == True:
        print("      ClearingOperationsTestSuite.getSuite")

    testSuite = unittest.TestSuite()

    ''' Add the Clearing Operations tests '''

    loader = unittest.TestLoader()


    testSuite.addTest(loader.loadTestsFromTestCase(ClearingOperationsCanvasAreaGRGTestCase.ClearingOperationsCanvasAreaGRGTestCase))
    testSuite.addTest(loader.loadTestsFromTestCase(ClearingOperationsNumberFeaturesTestCase.ClearingOperationsNumberFeaturesTestCase))
    testSuite.addTest(loader.loadTestsFromTestCase(ClearingOperationsPointTargetTestCase.ClearingOperationsPointTargetTestCase))


    return testSuite
