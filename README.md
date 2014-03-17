# solutions-geoprocessing-toolbox

The ArcGIS Solutions Geoprocessing Toolbox is a set of models, scripts, and tools for use in ArcGIS Desktop. These tools provide specialized processing, workflows, and analysis for defense, intelligence, and other solutions domains.

Important Note: This is the 10.2 and later version of all of the tools from the previous repository at [https://github.com/Esri/defense-and-intel-analysis-toolbox](https://github.com/Esri/defense-and-intel-analysis-toolbox). That repo will be retired once this repo has been fully validated.

![Image of toolbox](ScreenShot.jpg)

## Sections

* [Features](#features)
* [Requirements](#requirements)
* [Instructions](#instructions)
* [Resources](#resources)
* [Issues](#issues)
* [Contributing](#contributing)
* [Licensing](#licensing)

## Features

* Specialized geoprocessing models and tools for general defense and intelligence analysis tasks including
  * Tools for visibility and range analysis
  * Tools for analyzing the battlefield environment
  * Tools for position analysis
* Specialized geoprocessing models and tools for emergency management
* The [**common**](./common/README.md) folder contains shared tools:
  * Military Aspects of Terrain Toolbox
  * Position Analysis Tools
  * Publishable Task Tools
  * Range Card Tools
  * Visibility and Range Tools
* The [**analysis**](./analysis/README.md) folder contains:
  * AdjustSampleDataDates
  * Helicopter Landing Zone Tools
  * Incident Analysis Tools
  * VillageClearing
* The [**environment**](./environment/README.md) folder contains:
  * Build Elevation Mosiac Tools
  * Geonames Tools
  * Maritime Decision Aid Tools
  * Network Data Preparation Tools
  * Path Slope Tools
  * Imagery Basemap Tools
  * Scanned Map Basemap Tools
  * Topographic Basemap Tools
* The [**emergencymanagement**](./emegencymanagement/README.md) folder contains:
  * ERG Tools
* The [**planning**](./planning/README.md) folder contains:


## Requirements

* ArcGIS Desktop 10.1 or later Standard 
* Apache Ant - used to download and extract dependent data and run test drivers
* Java Runtime Environment (JRE) or Developer Kit (JDK) (required by Ant)
* Some tools require additional licenses (these tools will be disabled if license is unavailable), see READMEs for more information: 
    * ArcGIS Desktop Advanced (ArcInfo)
    * ArcGIS Spatial Analyst Extension
    * ArcGIS 3D Analyst Extension
    * For example these tools require Desktop Advanced and Spatial Analyst:
        * Path Slope Tools.tbx\Path Slope
        * Visibility and Range Tools.tbx\Range Fan

## Instructions

### General Help
[New to Github? Get started here.](http://htmlpreview.github.com/?https://github.com/Esri/esri.github.com/blob/master/help/esri-getting-to-know-github.html)

### Getting Started with the toolbox

* Download the Github repository
    * If repository was downloaded as a zip, extract the zip file
    * Make note of this directory, the steps below assume it will be called "solutions-geoprocessing-toolbox"

### Downloading Data Dependencies/Test Data

* Install and configure Apache Ant
    * Download Ant from the [Apache Ant Project](http://ant.apache.org/bindownload.cgi) and unzip to a location on your machine
    * Set environment variable `ANT_HOME` to Ant Install Location
    * Add Ant\bin to your path: `%ANT_HOME%\bin`
    * NOTE: Ant requires Java [Runtime Environment (JRE) or Developer Kit (JDK)](http://www.oracle.com/technetwork/java/javase/downloads/index.html) to be installed and the environment variable `JAVA_HOME` to be set to this location
    * To verify your Ant Installation: Open Command Prompt> `ant -h` and verify it runs and returns the help options correctly 
    * You may optionally install the [PyDev Eclipse Plugin for Python](http://pydev.org) if you plan to use Eclipse to run/debug
* To download the data dependencies 
    * Open Command Prompt>
    * `cd solutions-geoprocessing-toolbox`
    * `> ant`
    * Verify “Build Succeeded”  

### Running Verification Tests

* Configure and verify Ant as described in the previous steps
* To run all unit tests
    * `> cd solutions-geoprocessing-toolbox`
    * `>  ant -f run_all_tests.xml`
    *  Note/Warning: this will run the test drivers from each test directory and can take several hours to run
* To run individual unit tests
    * Open Command Prompt>
    * Go to the folder for the area you would like to test, the example below uses the `environment` area/folder, but each area has similar tests 
    * `> cd solutions-geoprocessing-toolbox\environment\test`
    * `> ant`
    * Verify “Build Succeeded”

## Resources

* Learn more about Esri's [ArcGIS for Defense maps and apps](http://resources.arcgis.com/en/communities/defense-and-intelligence/).

## Issues

* Find a bug or want to request a new feature?  Please let us know by submitting an issue.

## Contributing

Esri welcomes contributions from anyone and everyone. Please see our [guidelines for contributing](https://github.com/esri/contributing).

## Licensing

Copyright 2013 Esri

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

A copy of the license is available in the repository's
[license.txt](license.txt) file.

[](Esri Tags: ArcGIS Defense and Intelligence Military Environment Planning Analysis Emergency Management )
[](Esri Language: Python)
