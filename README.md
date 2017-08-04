
# solutions-geoprocessing-toolbox

The ArcGIS Solutions Geoprocessing Toolbox is a collection of models, scripts, and tools for use in [ArcGIS for Desktop](http://www.esri.com/software/arcgis/arcgis-for-desktop) and [ArcGIS Pro](http://www.esri.com/en/software/arcgis-pro). These tools provide specialized processing, workflows, and analysis for defense, intelligence, emergency management, and law enforcement. They are included in Esri's [Solutions Templates](http://solutions.arcgis.com/).


### Repository Owner: [Matt](https://github.com/mfunk)

* Merge Pull Requests
* Creates Releases and Tags
* Manages Milestones
* Manages and Assigns Issues

### Secondary: [Chris](https://github.com/csmoore)

* Backup when the Owner is away

Additional information is available in the repository's [Wiki](https://github.com/Esri/solutions-geoprocessing-toolbox/wiki).

## Sections

* [Features](#features)
* [Requirements](#requirements)
* [A Tale of Two Toolboxes](#a-tale-of-two-toolboxes)
* [Instructions To Get Started](#instructions-to-get-started)
	* [General Help](#general-help)
	* [Getting Started with the tools](#getting-started-with-the-tools)
	* [Running Verification Tests](#running-verification-tests)
* [Mature Support](#mature-support)
* [Resources](#resources)
* [Issues](#issues)
* [Contributing](#contributing)
* [Licensing](#licensing)

## Features

Specialized geoprocessing models and tools for general defense and intelligence analysis tasks including:

* The [**geonames**](./geonames) folder contains:
	* Geonames Tools_pro
	* Geonames Tools_arcmap
	* [Geonames Locator Solutions Page](http://solutions.arcgis.com/defense/help/geonames-locator/)

* The [**clearing_operations**](./clearing_operations) folder contains:
	* Clearing Operations Tools_pro
	* Clearing Operations Tools_arcmap
	* [Clearing Operations Solutions Page](http://solutions.arcgis.com/defense/help/clearing-operations/)

* The [**distance_to_assets**](./distance_to_assets) folder contains:
	* Distance To Assets_pro
	* Distance To Assets_arcmap
	* [Distance to Assets Solutions Page](http://solutions.arcgis.com/defense/help/distance-to-assets/)
  
* The [**military_aspects_of_terrain**](./military_aspects_of_terrain) folder contains:
	* Military Aspects of Terrain Tools_pro
	* Military Aspects of Terrain Tools_arcmap
	* [Military Aspects of Terrain Solutions Page](http://solutions.arcgis.com/defense/help/maot/)

* The [**military_aspects_of_weather**](./military_aspects_of_weather) folder contains:
	* Military Aspects of Weather Tools_arcmap
	* [Military Aspects of Weather Solutions Page](http://solutions.arcgis.com/defense/help/maow/)

* The [**sun_position_analysis**](./sun_position_analysis) folder contains:
	* Sun Position Analysis Tools_pro
	* Sun Position Analysis Tools_arcmap
	* [Sun Position Analysis Solutions Page](http://solutions.arcgis.com/defense/help/sun-position-analysis/)

* The [**incident_analysis**](./incident_analysis) folder contains:
	* Incident Analysis Tools_pro
	* Adjust Sample Data Dates Tools_pro
	* Incident Analysis Tools_arcmap
	* Adjust Sample Data Dates Tools_arcmap
	* [Incident Analysis Solutions Page](http://solutions.arcgis.com/defense/help/incident-analysis/)

## Requirements

* ArcGIS Desktop 10.3.1 (or later)
* ArcGIS Pro 1.4 (or later)

NOTE: Check [Releases](https://github.com/Esri/solutions-geoprocessing-toolbox/releases) for tools for previous versions of ArcGIS Desktop

* Some tools require additional licenses (these tools will be disabled if license is unavailable): 
    * ArcGIS Desktop Advanced
	    * Clearing Operations_arcmap
	    * Clearing Operations_pro
    * ArcGIS Spatial Analyst Extension
	    * Military Aspects of Terrain_pro
	    * Military Aspects of Terrain_arcmap
	    * Sun Position Analysis Tools_pro
	    * Sun Position Analysis Tools_arcmap
    * ArcGIS 3D Analyst Extension
	    * Military Aspects of Terrain_pro
	    * Military Aspects of Terrain_arcmap
    * Access to ArcGIS Organization Account
	    * Distance To Assets_pro
      * Distance To Assets_arcmap  

## A Tale of Two Toolboxes

The solutions-geoprocessing-toolbox repo supports toolboxes for both ArcMap/ArcCatalog/ArcGlobe/ArcScene (collectively called ArcGIS for Desktop) and also ArcGIS Pro. Toolboxes that are modified in ArcGIS Pro are not
backwards compatible (see **Compatibility** note below) with other ArcGIS Desktop applications (ArcMap), so most toolboxes are duplicated for one or the other. The naming of these toolboxes is as follows:

* Toolboxes that are for ArcGIS Desktop will include *arcmap* after the toolbox name. For example: **Geonames Tools__arcmap.tbx**
* Toolboxes for ArcGIS Pro will include *pro*. For example: **Geonames Tools__pro.tbx**


Please note that some toolboxes are for ArcGIS Pro only, or ArcGIS Desktop only. These toolboxes will follow the above naming convention, but will not have a duplicate.

* [Compatibility: ModelBuilder migration in Pro](http://pro.arcgis.com/en/pro-app/help/analysis/geoprocessing/modelbuilder/modelbuilder-changes-in-arcgis-pro.htm)
* [Product info for ArcGIS Pro](http://www.esri.com/software/arcgis-pro)
* [Help for ArcGIS Pro](http://pro.arcgis.com/en/pro-app/)


## Instructions To Get Started

### General Help
[New to Github? Get started here.](http://htmlpreview.github.com/?https://github.com/Esri/esri.github.com/blob/master/help/esri-getting-to-know-github.html)

[Downloading Test Data](#downloading-test-data) and [Running Verification Tests](#running-verification-tests) are only available through the GitHub repository, and are not available from other download versions of the repository.

### Getting Started with the tools

* Download the Github repository
    * If repository was downloaded as a zip, extract the zip file
    * Make note of this directory, the steps below assume it will be called "solutions-geoprocessing-toolbox"
    * Open the toolboxes in the appropriate version of ArcMap or ArcGIS Pro listed in [requirements](#requirements)
    * Questions about the tools? Start by reading the tool doc
    * Tool doc doesn't make sense? Please log an [issue](https://github.com/Esri/solutions-geoprocessing-toolbox/issues) and let us know!

### Running Verification Tests

- Follow instructions in [Running tests for solutions-geoprocessing-toolbox](./utils/test/Readme.md)

## Mature Support
For information Esri support levels visit the [Esri Product Life Cycle](http://support.esri.com/other-resources/product-life-cycle) page. Toolboxes marked for Mature Support will be removed from this repository's *dev* and *master* branches in the future, but will still be availalbe from earlier [releases](https://github.com/Esri/solutions-geoprocessing-toolbox/releases).

## Resources
* [GitHub Help](https://help.github.com/)
* Learn more about [ArcGIS Solutions](http://solutions.arcgis.com/).
* Learn more about [ArcGIS for the Military](http://solutions.arcgis.com/military/).
* Learn more about [ArcGIS for Intelligence](http://solutions.arcgis.com/intelligence/).
* Learn more about [ArcGIS for Emergency Management](http://solutions.arcgis.com/emergency-management/).
* Learn more about [ArcGIS Pro](http://pro.arcgis.com/en/pro-app/).

## Issues

Find a bug or want to request a new feature?  Please let us know by submitting an [issue](https://github.com/Esri/solutions-geoprocessing-toolbox/issues).

To submit an issue:

1. Go to the [issue](https://github.com/Esri/solutions-geoprocessing-toolbox/issues) tab
2. Click **New Issue**
3. Fill out *all* of the relevant sections
4. **Submit new issue** when completed

Tips:
* Include a FULL description of the problem or enhancement or idea. Include:
   * What happened (details)?
   * What did you expect to happen?
   * What is different between what happened and what you expected?
   * What versions of the software are you working on?
   * Include the text of any error messages.
* Include steps to reproduce the problem. We can't solve it if we can't see what's wrong.
   * Use a numbered list of steps.
   * DETAILS: Be explicit. More is better, than little, which is better than nothing. Never assume we know what you're talking about (assume we don't know).
* Include screenshots to support the info above, but NEVER replace a good description with a screenshot.

## Contributing

When you contribute to this repository we ask that you follow the guidelines in the [repository-specific guidelines for contributing](./CONTRIBUTING.md). If you have questions, or you get stuck, please ask the [Repository Owner](#repository-owner). We are here to help! Thanks.

Esri welcomes contributions from anyone and everyone through GitHub. Please see Esri's general [guidelines for contributing](https://github.com/esri/contributing).

## Licensing

Copyright 2016-2017 Esri

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at:

[http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

A copy of the license is available in the repository's
[license.txt](license.txt) file.
