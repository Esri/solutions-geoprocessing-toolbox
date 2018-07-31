# coding: utf-8
'''
------------------------------------------------------------------------------
Copyright 2017 Esri
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

  http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
------------------------------------------------------------------------------

==================================================
Utilities.py
==================================================

Utility module for Operational Graphics toolboxes

==================================================
HISTORY:

9/3/2015 - mf - Created utilities.py to centralize common tool functions
9/14/2017 - mf - Update for resetLayerPaths

==================================================
'''

import os
import sys
import string
import random
import arcpy

PLATFORM_PRO = 'ARCGIS_PRO'
PLATFORM_DESKTOP = 'ARCMAP'
PLATFORM_OTHER = 'OTHER'
PLATFORM_NOT_SET = 'NOT_SET'

platform = None
app_found = PLATFORM_NOT_SET

# Returns Pro or ArcMap only
def GetPlatform() :

    global platform

    if platform is None :

        platform = PLATFORM_DESKTOP

        installInfo = arcpy.GetInstallInfo()
        if installInfo['ProductName'] == 'ArcGISPro':
            platform = PLATFORM_PRO

    return platform

# Returns Pro or ArcMap if running in application (where arcpy.mapping or arcpy.mp present)
# and Other if in stand-alone arcpy
def GetApplication():
    '''Return app environment as: ARCMAP, ARCGIS_PRO, OTHER'''

    global app_found
    if app_found != PLATFORM_NOT_SET:
            return app_found

    try:
        from arcpy import mp
    except ImportError:
        try:
            from arcpy import mapping
            mxd = arcpy.mapping.MapDocument("CURRENT")
            app_found = PLATFORM_DESKTOP
            return app_found
        except:
            app_found = PLATFORM_OTHER
            return app_found
    try:
        aprx = arcpy.mp.ArcGISProject('CURRENT')
        app_found = PLATFORM_PRO
        return app_found
    except:
        app_found = PLATFORM_OTHER
        return app_found

def MakeScratchGeodatabase():
    '''
    '''
    name = ''.join([random.choice(string.ascii_uppercase) for _ in range(6)])
    ws = arcpy.CreateFileGDB_management('%scratchFolder%',name,'CURRENT')[0]
    return ws