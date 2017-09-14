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
import arcpy

app_found = 'NOT_SET'

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

def tempLayerFileName():
    '''
    returns temp .lyr file
    '''
    import tempfile
    return os.path.join(tempfile.mkstemp(), ".lyr")

def resetLayerPaths(layer_file, feature_class):
    '''
    reset source dataset path in layer_file using gdb_path

    layer_file: path to the .lyr in the current filesystem
    gdb_path: path to the featuresetWebMerc.gdb

    returns layer_file with updated source data
    '''
    global app_found
    if app_found == "NOT_SET":
        app_found = Utilities.GetApplication()

    if app_found == "ARCGIS_PRO":
        from arcpy import mp
        broken_layer = mp.LayerFile(layer_file).listBrokenDataSources()[0]
        if broken_layer:
            broken_layer.updateConnectionProperties({'dataset':broken_layer.filePath},
                                                    {'dataset':os.path.basename(feature_class)})
            temp_lyr = tempLayerFileName()
            broken_layer.saveACopy(temp_lyr)
            os.remove(layer_file)
            import shutil
            shutil.copyfile(temp_lyr, layer_file)
            os.remove(temp_lyr)
            return layer_file
        else:
            return layer_file
    else:
        from arcpy import mapping
        broken_layer = mapping.listBrokenDataSources(arcpy.mapping.Layer(layer_file))[0]
        if broken_layer:
            broken_layer.replaceDataSource(os.path.dirname(feature_class),
                                           "FILEGDB_WORKSPACE",
                                           os.path.basename(feature_class))
            return layer_file
        else:
            return layer_file
