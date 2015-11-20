# coding: utf-8
'''
-----------------------------------------------------------------------------
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
-----------------------------------------------------------------------------

==================================================
ERGTestUtils.py
--------------------------------------------------
requirments: ArcGIS X.X, Python 2.7 or Python 3.4
author: ArcGIS Solutions
contact: ArcGISTeam<Solution>@esri.com
company: Esri
==================================================
description:
These are utility modules used by the two ERG tool test cases:
* ERGByChemicalTestCase.py
* ERGByPlacardTestCase.py

==================================================
history:
11/10/2015 - MF - intial work
==================================================
'''

import arcpy

def getInputPointFC():
        ''' returns UTM projected point from static WGS 84 point '''
        fc = getInputPointFCFromXY(77.0, 38.9)
        return fc

def getInputPointFCFromXY(x, y):
        ''' returns UTM projected point from X and Y coords (longitude, latitude) in WGS 84 '''
        inPoint = arcpy.Point(x, y)
        inWGS84Point = arcpy.PointGeometry(inPoint)
        sr = arcpy.SpatialReference(4326) #GCS_WGS_1984?
        inWGS84Point.spatial_reference = sr
        # create an in_memory feature class to initially contain the input point
        fc = arcpy.CreateFeatureclass_management("in_memory", "tempfc", "POINT",
                                                 None, "DISABLED", "DISABLED",
                                                 sr)[0]
        # open and insert cursor
        with arcpy.da.InsertCursor(fc, ["SHAPE@"]) as cursor:
            cursor.insertRow([inWGS84Point])
        # create a featureset object and load the fc
        inputFeatureSet = arcpy.FeatureSet()
        inputFeatureSet.load(fc)
        return fc
