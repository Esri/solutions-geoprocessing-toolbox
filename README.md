[![Planned Issues](https://badge.waffle.io/Esri/solutions-geoprocessing-toolbox.png?label=0%20-%20backlog&title=In%20Backlog)](https://waffle.io/Esri/solutions-geoprocessing-toolbox)
[![Issues in Progress](https://badge.waffle.io/Esri/solutions-geoprocessing-toolbox.png?label=2%20-%20In%20Progress&title=In%20Progress)](https://waffle.io/Esri/solutions-geoprocessing-toolbox)
[![Issues waiting for Verification](https://badge.waffle.io/Esri/solutions-geoprocessing-toolbox.png?label=3%20-%20Verify&title=For%20Verification)](https://waffle.io/Esri/solutions-geoprocessing-toolbox)

[![Code Climate](https://codeclimate.com/github/Esri/solutions-geoprocessing-toolbox/badges/gpa.svg)](https://codeclimate.com/github/Esri/solutions-geoprocessing-toolbox)
# solutions-geoprocessing-toolbox

The ArcGIS Solutions Geoprocessing Toolbox is a set of models, scripts, and tools for use in ArcGIS Desktop. These tools provide specialized processing, workflows, and analysis for defense, intelligence, emergency management, and other solutions domains.

![Image of the toolbox](SolutionsGeoprocessingToolboxGraphic.png)

## Sections

* [Features](#features)
* [Requirements](#requirements)
* [A Tale of Two Toolboxes](#a-tale-of-two-toolboxes)
* [Instructions](#instructions)
	* [General Help](#general-help)
	* [Getting Started with the tools](#getting-started-with-the-tools)
	* [Downloading Test Data](#downloading-test-data)
	* [Running Verification Tests](#running-verification-tests)
* [Resources](#resources)
* [Issues](#issues)
* [Contributing](#contributing)
* [Credits](#credits)
* [Licensing](#licensing)

## Features

* Specialized geoprocessing models and tools for general defense and intelligence analysis tasks including
  * Tools for visibility and range analysis
  * Tools for analyzing the battlefield environment
  * Tools for data management and coordinates 

* The [**capability**](./capability/README.md) folder contains:
  * ERG (Emergency Resources Guide) Tools
  * Helicopter Landing Zone Tools
  * Point Of Origin Tools

* The [**data_management**](./data_management/README.md) folder contains:
  * Adjust Sample Data Dates Tools
  * Build Elevation Mosaic Tools - **To be deprecated**, replaced by Elevation Tools
  * CADRG ECRG Tools
  * CIB Tools
  * Elevation Tools
  * Geonames Tools
  * Imagery Basemap Tools - **To be deprecated**, replaced by CIB Tools
  * Import and Conversion Tools - formerly Position Analysis Tools
  * LiDAR Elevation Tools
  * Network Data Preparation Tools
  * Patrol Data Capture Tools
  * Publishable Task Tools
  * Scanned Map Basemap Tools - **To be deprecated**, replaced by CADRG ECRG Tools
  * Topographic Basemap Tools - **To be deprecated**, replaced by Elevation Tools

* The [**operational_graphics**](./operational_graphics/README.md) folder contains:
  * Clearing Operations Tools
  * Range Card Tools
  
* The [**patterns**](./patterns/README.md) folder contains:
  * Change Detection Tools
  * Incident Analysis Tools
  * Landsat Pre Processing Tools
  * Movement Analysis Tools

* The [**suitability**](./suitability/README.md) folder contains:
  * Maritime Decision Aid Tools
  * Military Aspects of Terrain Tools
  * Military Aspects of Weather Tools
  * Path Slope Tools

* The [**visibility**](./visibility/README.md) folder contains:
  * Sun Position Analysis Tools
  * Visibility and Range Tools
  * Visibility Data Prep Tools

## Requirements

* ArcGIS Desktop 10.3+ or ArcGIS Pro 1.0+
    * Check [Releases](https://github.com/Esri/solutions-geoprocessing-toolbox/releases) for tools for previous versions of ArcGIS Desktop
* Apache Ant - used to download and extract dependent data and run test drivers
* Java Runtime Environment (JRE) or Developer Kit (JDK) (required by Ant)
* Some tools require additional licenses (these tools will be disabled if license is unavailable), see READMEs for more information: 
    * ArcGIS Desktop Advanced (ArcInfo)
    * ArcGIS Spatial Analyst Extension
    * ArcGIS 3D Analyst Extension
    * ArcGIS Network Analyst Extension
    * For example these tools require Desktop Advanced and Spatial Analyst:
        * Path Slope Tools.tbx\Path Slope
        * Visibility and Range Tools.tbx\Range Fan

## A Tale of Two Toolboxes

The solutions-geoprocessing-toolbox repo is now supporting toolboxes for both ArcMap/ArcCatalog/ArcGlobe/ArcScene (collectively called ArcGIS for Desktop) and also ArcGIS Pro. Toolboxes that are modified in ArcGIS Pro are not
backwards compatible with other ArcGIS Desktop applications (ArcMap), so most toolboxes are duplicated for one or the other. The naming of these toolboxes is as follows:

* Toolboxes that are for ArcGIS Desktop 10.3 will include *_10.3* after the toolbox name. For example: **Visibility and Range Tools_10.3.tbx**
* Toolboxes with a 'unversioned' name are for ArcGIS Pro 1.0. For example: **Visibility and Range Tools.tbx**

Please note that some toolboxes are for ArcGIS Pro only, or ArcGIS Desktop 10.3 only. These toolboxes will follow the above naming convention, but will not have a duplicate.

* [Product info for ArcGIS Pro](http://www.esri.com/software/arcgis-pro)
* [Help for ArcGIS Pro](http://pro.arcgis.com/en/pro-app/)


## Instructions

### General Help
[New to Github? Get started here.](http://htmlpreview.github.com/?https://github.com/Esri/esri.github.com/blob/master/help/esri-getting-to-know-github.html)

[Downloading Test Data](#downloading-test-data) and [Running Verification Tests](#running-verification-tests) are only available through the GitHub repository, and are not available from other download versions of the repository.

### Getting Started with the tools

* Download the Github repository
    * If repository was downloaded as a zip, extract the zip file
    * Make note of this directory, the steps below assume it will be called "solutions-geoprocessing-toolbox"

### Downloading Test Data

* Install and configure Apache Ant
    * Download Ant from the [Apache Ant Project](http://ant.apache.org/bindownload.cgi) and unzip to a location on your machine, for example 'c:\apache-ant-1.9.2'.
    * Set environment variable `ANT_HOME` to Ant Install Location (e.g. the folder from first step)
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

* Learn more about [ArcGIS Solutions](http://solutions.arcgis.com/).
* Learn more about [ArcGIS for the Military](http://solutions.arcgis.com/military/).
* Learn more about [ArcGIS for Intelligence](http://solutions.arcgis.com/intelligence/).
* Learn more about [ArcGIS for Emergency Management](http://solutions.arcgis.com/emergency-management/).
* Learn more about [ArcGIS Pro](http://pro.arcgis.com/en/pro-app/).

## Issues

* Find a bug or want to request a new feature?  Please let us know by submitting an issue.

## Contributing

Esri welcomes contributions from anyone and everyone through GitHub. Please see our [guidelines for contributing](https://github.com/esri/contributing).


### Fork and Clone the Repo
Start contributing to the solutions-geoprocessing-toolbox repo by making a fork and cloning it to your local machine.

* Fork the repo in github.com with ![fork button](ForkButtonIcon.png)
* Clone your remote onto your local system ![clone button](CloneInDesktopButtonIcon.png)
* Get the *mdcs-py* submodule:
	* `> git submodule init`
	* `> git submodule update`

### Set Your Upstream
Setting the parent repo to get changes from.

* `> git remote -v`

if no *upstream* is listed continue with:

* `> git remote add upstream https://github.com/Esri/solutions-geoprocessing-toolbox`
* `> git remote set-url upstream --push no_push`

check that an *upstream* is registered:

* `> git remote -v`

### Getting Changes from Upstream
The solutions-geoprocessing-toolbox repo changes often, so make sure you are getting the latest updates often.

* `> git fetch upstream`
* `> git merge upstream/master`
*

### Share Your Mods
If you've made changes to the repo that you want to share with the community.

* Commit your changes to your local
* Sync local with your remote fork
* Make a **Pull Request** from your remote fork on github.com ![New Pull Request](NewPullRequestButtonIcon.png)


## Credits
Mosaic Dataset Configuration Scripts (MDCS) is an Esri repo available at [https://github.com/Esri/mdcs-py](https://github.com/Esri/mdcs-py) and [licensed](https://github.com/Esri/mdcs-py/blob/master/license.txt) under Apache License Version 2.0, January 2004.

## Licensing

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

A copy of the license is available in the repository's
[license.txt](license.txt) file.

[](Esri Tags: ArcGIS Defense and Intelligence Military Emergency Management National Security)
[](Esri Language: Python)
