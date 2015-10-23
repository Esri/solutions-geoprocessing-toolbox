#Writing tests for solutions-geoprocessing-toolbox

##Sections
* [Introduction](#introduction)
* [The Test Structure](#the-test-structure)
* [TestKickStart and TestRunner](testkickstart-and-testrunner)
* [Test Suites](#test-suites)
* [Test Cases](#test-cases)
* [Test Data](#test-data)

##Introduction
The goal of this document is to give an overview of how the solutions-geoprocessing-toolbox tests are structured and how they are intended to work. This is just an overview. To build new tests, the successful developer will need to review the existing tests as a guide for building their own.

##The Test Structure

##TestKickStart and TestRunner
These two files, along with some supporting files, start the tests, and determine which platform the tests will run within.

**TestKickStart.bat** is a simple .BAT file to run the tests under both Python 2.7 (ArcGIS Desktop) and Python 3.4 (ArcGIS Pro).

**TestRunner.py** calls the test suites to run.

##Test Suites
Test suites are collections of [Test Cases](#test-cases). There are two major levels of test suites. The top level are test suites for each of the six tool categories: capability, data_management, operational_graphics, patterns, suitability, visibility. 

The test suite files are named **All[category]TestSuite.py**. In each one is the collection the second level of test suites: the toolbox test suites.

The toolbox test suites are the collection of test cases for each toolbox in the tool category.

These are named **[toolbox name]TestSuite.py**. 

##Test Cases
Test cases are the collection of individual tests for a specific tool, or supporting toolset.

They are named **[toolname]TestCase.py**

##Data
The it is impossible to build a test without some kind of inputs. Some tests generate their own data internally (Check out the ERG tool tests as an example). But most will require some kind of output test data.

Test data **must** be stored in the *./data* folder.
