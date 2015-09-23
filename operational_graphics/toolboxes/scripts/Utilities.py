# coding: utf-8
#------------------------------------------------------------------------------
# Copyright 2015 Esri
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#------------------------------------------------------------------------------
#
# ==================================================
# Utilities.py
# --------------------------------------------------
# Built on ArcGIS 10.?
# ==================================================
#
# Utility module for Operational Graphics toolboxes
#
# ==================================================
# HISTORY:
#
# 9/3/2015 - mf - Created utilities.py to centralize common tool functions
#
# ==================================================

import arcpy

app_found = 'NOT_SET'
toolbox10xSuffix = "_10.3"

def GetApplication():
    '''Return app environment as: ARCMAP, ARCGIS_PRO, OTHER'''

    global app_found
    if app_found != 'NOT_SET':
            return app_found

    try:
        from arcpy import mp
    except ImportError:
        try:
            from arcpy import mapping
            mxd = arcpy.mapping.MapDocument("CURRENT")
            app_found = "ARCMAP"
            return app_found
        except:
            app_found = "OTHER"
            return app_found
    try:
        aprx = arcpy.mp.ArcGISProject('CURRENT')
        app_found = "ARCGIS_PRO"
        return app_found
    except:
        app_found = "OTHER"
        return app_found
