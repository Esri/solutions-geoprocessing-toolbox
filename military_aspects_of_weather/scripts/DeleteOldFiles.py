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
DeleteOldFiles.py
--------------------------------------------------
requirements: ArcGIS 10.3+, Python 2.7
author: ArcGIS Solutions
company: Esri
==================================================
description:
Deletes old NETCDF files from a directory specified by the user
for a time period specified by a user
==================================================
history:
3/24/2015 - AB - Original development
12/3/2015 - MF - Updates for standards
==================================================
'''

import os
import time
import arcpy

# Input path from which files should be deleted.
path = arcpy.GetParameterAsText(0)
# number of days to remove
days = arcpy.GetParameter(1)

# Get the present time
now = time.time()
# Get the list of files within the directory.
for f in os.listdir(path):
    f = os.path.join(path, f)
    #get the last modified time for each of the files and compare this to the date 7 days ago.
    if os.stat(f).st_mtime < now - days * 86400:
        if os.path.isfile(f):
            #If the file is older than specified age then delete it.
            #TODO: Check that we are removing a NetCDF (*.nc) file, and not something else?
            os.remove(f)
            print(f)
            arcpy.AddMessage(f)

print("Specified files deleted")
arcpy.AddMessage("Specified files deleted")
