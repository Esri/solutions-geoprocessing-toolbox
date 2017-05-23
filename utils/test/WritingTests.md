# Writing tests for solutions-geoprocessing-toolbox

## Sections
* [Introduction](#introduction)
* [The Test Structure](#the-test-structure)
* [TestKickStart and TestRunner](testkickstart-and-testrunner)
* [Test Suites](#test-suites)
* [Test Cases](#test-cases)
* [Test Data](#test-data)

## Introduction
The goal of this document is to give an overview of how the solutions-geoprocessing-toolbox tests are structured and how they are intended to work. This is just an overview. To build new tests, the successful developer will need to review the existing tests as a guide for building their own.

## The Test Structure

### TestKickStart and TestRunner
These two files, along with some supporting files, start the tests, and determine which platform the tests will run within.

**TestKickStart.bat** is a simple .BAT file to run the tests under both Python 2.7 (ArcGIS Desktop) and Python 3.4 (ArcGIS Pro).

**TestRunner.py** calls the test suites to run.

### Test Suites
Test suites are collections of [Test Cases](#test-cases). There are two major levels of test suites. The top level are test suites for each of the six tool categories: capability, data_management, operational_graphics, patterns, suitability, visibility. 

The test suite files are named **All[category]TestSuite.py**. In each one is the collection the second level of test suites: the toolbox test suites.

The toolbox test suites are the collection of test cases for each toolbox in the tool category.

These are named **[toolbox name]TestSuite.py**. 

### Test Cases
Test cases are the collection of individual tests for a specific tool, or supporting toolset.

They are named **[toolname]TestCase.py**

### Test Data
The it is impossible to build a test without some kind of inputs. Some tests generate their own data internally (Check out the ERG tool tests as an example). But most will require some kind of output test data.

* Test data **must** be stored in the *./data* folder. 
* Keep feature data in a file geodatabase. You should name it like your toolbox.
* Any file data (CSV, TXT, XLSX, etc.) should be easy to identify which toolbox it belongs to.

## Outline for writing tests
### 1. Make a separate branch from dev
Use this as a chance to create a feature branch from **dev** which will be merged back in when you are done. THis keeps your work separate from other work and the main **dev** branch.

### 2. Get data and run the test manually
Before you start writing any test code, collect your releasable data. Then manually run the tool or tools with the data. Make sure it works and you are familiar with the tool's operation and the expected results.

### 3. Write your test cases
Use the existing Test Case files as a guide to get started writing your own. The goal is to run the tool to create output that can be tested by the unittest TestCase assert methods [link to assert methods](https://docs.python.org/3/library/unittest.html#unittest.TestCase).

### 4. Wire them up to the framework
Create a Test Suite that calls your Test Case
Add your Test Suite to the existing All[category]TestSuite.py

### 5. Run the test from TestKickStarter.bat
