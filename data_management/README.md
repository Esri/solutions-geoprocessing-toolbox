# Data Management Tools

Data Management tools help to prepare, format, filter, and organize your data into usable formats.

![Image of repository-template](data_management_screenshot.png)

## Sections

* [Adjust Sample Data Dates Tools](#adjust_sample_data_dates_tools)
* [Build Elevation Mosaic Tools](#build_elevation_mosaic_tools)
* [Geonames Tools](#geonames_tools)
* [Imagery Basemap Tools](#imagery_ basemap_tools)
* [Network Data Preparation Tools](#network_data_preparation_tools)
* [Patrol Data Capture Tools](#patrol_data_capture_tools)
* [Position Analysis Tools](#position_analysis_tools)
* [Publishable Task Tools](#publishable_task_tools)
* [Scanned Map Basemap Tools](#scanned_map_basemap_tools)
* [Topographic Basemap Tools](#topographic_basemap_tools)
* [Issues](#issues)
* [Contributing](#contributing)
* [Licensing](#licensing)

## Adjust Sample Data Dates Tools

This toolbox contains a tool to adjust the date fields of the sample data included with the Inciedent Analysis toolbox.

* Change Sample Data Dates to Recent Dates

## Build Elevation Mosaic Tools

This toolbox contains tools that take raster or LIDAR data and create surface or terrain mosaics.

* Build Elevation Mosaics
* Create Derived Elevation Mosaic
* Create Source Elevation Mosaics
* Create Source LAS Ground Elevation Mosaics
* Create Source LAS Surface Elevation Mosaics

## Geonames Tools

Tools for building geonames locator.

* Create Geonames Gazetter Locator
* Load Geonames File

## Imagery Basemap Tools

Tools to assist in building an imagery basemap from standard defense raster formats.

* Add CIB Rasters to Mosaic Dataset
* Calculate Raster Visibility
* Create CIB Mosaic Dataset

## Network Data Preparation Tools

These tools are used to prepare road data for use in a road network dataset.

* Add Orientation Angle To Lines
* Add Travel Time To Roads
* Feature Class to Feature Class (System Tool)
* Split Lines At Intersections

## Patrol Data Capture Tools

Includes tools to import data that has been gathered on or after a patrol. This includes GPS data, saved in .gpx files, and Patrol Report data, saved in .xml files (as saved by an Infopath form)

* Append Tracks to DB
* Despike GPS Log
* Distinguish Tracks
* GPX to Layer
* Import Patrol Rpt
* Make Track Lines
* Recalculate Delta Times
* Rejoin Track Parts
* Remove Duplicate GPS Data

## Position Analysis Tools

Tools for converting tabular information to different geometries, and generating positional datasets.

* Convert Coordinates
* Locate Event
* Range Rings
* Table To 2-Point Line
* Table To Ellipse
* Table To Line Of Bearing
* Table To Point
* Table To Polygon
* Table To Polyline

## Publishable Task Tools

Publishable Tasks are a series of models that should be published as geoprocessing services for:

* Fast Visibility: visibility tools optimized to be run as geoprocessing services
  * Fast Visibility By Circle
  * Fast Visibility By Distance
  * Fast Visibility By Line
  * Fast Visibility By Parameters

* Road Network: tools for routing and drive time
  * Drive Time
  * Point-to-Point Route

## Scanned Map Basemap Tools

Tools for building a basemap from CADRG/ECRG scanned imagery.

* Add Miscellaneous CADRG/ECRG Rasters To Mosaic Dataset
* Add Standard CADRG/ECRG Rasters To Mosaic Dataset
* Calculate Raster Visibility
* Create CADRG/ECRG Mosaic Dataset

## Topographic Basemap Tools

Tools to assist in building a topographic basemap from feature data in the Urban Topographic Data Store (NGA's TFDM) geodatabase schema.

* Add DTED 1,2 to Elevation Mosaic Dataset
* Create Elevation Mosaic Dataset

## Issues

Find a bug or want to request a new feature?  Please let us know by submitting an issue.

## Contributing

Esri welcomes contributions from anyone and everyone. Please see our [guidelines for contributing](https://github.com/esri/contributing).

## Licensing

Copyright 2014 Esri

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

   [http://www.apache.org/licenses/LICENSE-2.0](http://www.apache.org/licenses/LICENSE-2.0)

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

A copy of the license is available in the repository's
[license.txt](license.txt) file.

[](Esri Tags: ArcGIS Defense and Intelligence Military Environment Planning Analysis Emergency Management ArcGISSolutions)
[](Esri Language: Python)
