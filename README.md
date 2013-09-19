# defense-and-intel-toolbox

The ArcGIS Defense and Intelligence Toolbox is a set of models, scripts, and tools for use in ArcGIS Desktop. These tools provide specialized processing and workflows for defense and intelligence analysis.


## Features

* Specialized geoprocessing models and tools for defense and intelligence analysis including
* Tools for visibility and range analysis
* Tools for analyzing the battlefield environment
* Tools for position analysis
* The **common** folder contains shared tools:
  * Military Aspects of Terrain Toolbox
  * Position Analysis Tools
  * Publishable Task Tools
  * Range Card Tools
  * Visibility and Range Tools
* The **environment** folder contains:
  * Build Elevation Mosiac Tools
  * Geonames Tools
  * Network Data Preparation Tools
  * Path Slope Tools

## <a id="Requirements"></a>Requirements

* ArcGIS Desktop 10.1 Standard 
* Apache Ant - used to download and extract dependent data and run test drivers
* Java Runtime Environment (JRE) or Developer Kit (JDK)
* Some tools require additional licenses (these tools will be disabled if license is unavailable):
    * ArcGIS Desktop Advanced (ArcInfo)
    * ArcGIS Spatial Analyst Extension
    * ArcGIS 3D Analyst Extension
    * For example these tools require Desktop Advanced and Spatial Analyst:
        * Path Slope Tools.tbx\Path Slope
        * Visibility and Range Tools.tbx\Range Fan

## <a id="Instructions"></a>Instructions

### General Help
[New to Github? Get started here.](http://htmlpreview.github.com/?https://github.com/Esri/esri.github.com/blob/master/help/esri-getting-to-know-github.html)

### Getting Started with the toolbox
* Download the Github repository
    * If repository was downloaded as a zip, extract the zip file
    * Make note of this directory, the steps below assume it will be called "defense-and-intel-analysis-toolbox"
* Install and configure Apache Ant
    * Download Ant from the [Apache Ant Project](http://ant.apache.org/bindownload.cgi) and unzip to a location on your machine
    * Set environment variable `ANT_HOME` to Ant Install Location
    * Add Ant\bin to your path: `%ANT_HOME%\bin`
    * NOTE: Ant requires Java [Runtime Environment (JRE) or Developer Kit (JDK)](http://www.oracle.com/technetwork/java/javase/downloads/index.html) to be installed and the environment variable `JAVA_HOME` to be set to this location
    * To verify your Ant Installation: Open Command Prompt> `ant -h` and verify it runs and returns the help options correctly 
    * You may optionally install the [PyDev Eclipse Plugin for Python](http://pydev.org) if you plan to use Eclipse to run/debug
* To download the data dependencies 
    * Open Command Prompt>
    * cd defense-and-intel-analysis-toolbox
    * > ant
    * Verify “Build Succeeded”  
* To run unit tests
    * Open Command Prompt>
    * > cd defense-and-intel-analysis-toolbox\source\test
    * > ant
    * Verify “Build Succeeded”
    * Note: this will run the test drivers from each test subdirectory (test_position_analysis, test_viz_and_range, etc.)


## Resources

* Learn more about Esri's [ArcGIS for Defense maps and apps](http://resources.arcgis.com/en/communities/defense-and-intelligence/).

## Issues

* Find a bug or want to request a new feature?  Please let us know by submitting an issue.

## Contributing

* Anyone and everyone is welcome to contribute.

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

[](Esri Tags: ArcGIS Defense and Intelligence)
[](Esri Language: Python)
