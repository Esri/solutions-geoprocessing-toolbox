# Environment tools


![Image of environment screenshot](OpFactorsGraphicColor.png)


## Sections

* [Build Elevation Mosaic Tools](#build elevation mosaic tools)
* [Geonames Tools](#geonames tools)
* [Imagery Basemap Tools](#imagery basemap tools)
* [Maritime Decision Aid Tools](#maritime decision aid tools)
* [Network Data Preparation Tools](#network data preparation tools)
* [Path Slope Tools](#path slope tools)
* [Scanned Map Basemap Tools](#scanned map basemap tools)
* [Topographic Basemap Tools](#topographic basemap tools)
* [Issues](#issues)
* [Contributing](#contributing)
* [Licensing](#licensing)


## Build Elevation Mosaic Tools
This toolbox contains the model for creating a mosaic dataset from elevation data, such as SRTM or DTED.
The resulting mosaic can then be published using the Aspect, Hillshade, and PercentSlope Raster Functions.
These raster functions will allow the client to transform the pixel values the selected raster types.

Included tools:
* Build Elevation Mosaics

Associated files:
* [toolboxes\Raster Functions\Aspect.rft.xml](./toolboxes/Raster Functions/Aspect.rft.xml)
* [toolboxes\Raster Functions\Hillshade.rft.xml](./toolboxes/Raster Functions/Hillshade.rft.xml)
* [toolboxes\Raster Functions\PercentSlope.rft.xml](./toolboxes/Raster Functions/PercentSlope.rft.xml)

## Geonames Tools
The Geonames Tools toolbox contains two model tools, and two supporting script tools, for creating a geocoding locator for place names.

Included tools:
* Create Geonames Gazetter Locator
* Load Geonames File
* Model Script Tools\Check Input
* Model Script Tools\Load Geonames

Associated files:
* [toolboxes\scripts\CheckInput.py](./toolboxes/scripts/CheckInput.py)
* [toolboxes\scripts\LoadGeonames.py](./toolboxes/scripts/LoadGeonames.py)

## Imagery Basemap Tools
Contains model tools that help build mosaic datasets that support the construction of an Imagery Basemap.

Included tools:
* Add CIB Rasters To Mosaic Dataset
* Calculate Raster Visibility
* Create CIB Mosaic Dataset

## Maritime Decision Aid Tools
Contained in this toolbox are specialized geoprocessing models and tools for defense and intelligence analysis.

Included tools:
* Distance Of Horizon
* Farthest On Circle

## Network Data Preparation Tools
These tools are used to prepare road data for use in a road network dataset.

Included tools:
* Add Orientation Angle To Lines
* Add Travel Time To Roads
* Feature Class To Feature Class (System Tool)
* Split Lines At Intersections

Associated files:
* [toolboxes\scripts\AddTravelTimeToRoads.py](./toolboxes/scripts/AddTravelTimeToRoads.py)
* [toolboxes\scripts\LineFeatureAngle.py](./toolboxes/scripts/LineFeatureAngle.py)
* \data\geodatabases\NetworkPrepData.gdb\RoadTravelVelocity

## Path Slope Tools
Path Slope Tools is a terrain analysis toolset to determine slope changes along linear features (paths). For example finding percent slope along roadways or degree slope along trails.These can then be used to determine vehicle crossing limits or areas dangerous to hikers.

Included tools:
* Path Slope
* Path Slope By Custom Table
* Path Slope By Reclass Values

Associated files:
* [toolboxes\layers\PathSlope.lyr](./toolboxes/layers/PathSlope.lyr)
* [toolboxes\layers\PathSlopeCustom.lyr](./toolboxes/layers/PathSlopeCustom.lyr)
* [toolboxes\layers\PathSlopeReclass.lyr](./toolboxes/layers/PathSlopeReclass.lyr)

## Scanned Map Basemap Tools
These tools are useful for creating mosaic datasets from CADRG/ECRG rasters. The mosaics can then be published as a Scanned Map basemap.

Included tools:
* Add Miscellaneous CADRG/ECRG Rasters To Mosaic Dataset
* Add Standard CADRG/ECRG Rasters To Mosaic Dataset
* Calculate Raster Visibility
* Create CADRG/ECRG Mosaic Dataset


## Topographic Basemap Tools
These tools are useful for building the components of the Topographic Basemap.

Included tools:
* Add DTED 1,2 to Elevation Mosaic Dataset
* Create Elevation Mosaic Dataset
* Standard Tools\Build Pyramids And Statistics (System Tool)
* Standard Tools\Calculate Statistics (System Tool)
* Standard Tools\Contour (System Tool)
* Standard Tools\Create Referenced Mosaic Dataset (System Tool)

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

[](Esri Tags: ArcGIS Defense Intelligence Operational Environment)
[](Esri Language: Python)
