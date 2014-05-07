#-------------------------------------------------------------------------------
# Copyright 2010-2013 Esri
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
#-------------------------------------------------------------------------------
# Separate GPS Tracks
# This script looks at times between points in a
# featureclass and, given a maximum time period
# (in seconds) for any one leg, identifies where
# a new track must be starting. All points in each
# track are applied a GUID to distinguish them as
# belonging to a unique track.
# INPUTS: 
#    Input Points Feature Class (FEATURECLASS)
#    DateTime Field - holding the GPS Timestamp (FIELD)
#    DeltaTime Field - holding the difference in time (secs) between the points either side (FIELD)
#    GUID Field - this script will populate this field with a GUID value, different for each track (FIELD)
#    Maximum DeltaTime - value above which a point is considered to be the start of a new track (DOUBLE)
# OUTPUTS:
#    Output Points (DERIVED FEATURECLASS)
#-------------------------------------------------------------------------------

import arcpy
import time
import datetime
import uuid

try:
    #set features and cursors so that they are deletable in
    #'finally' block should the script fail prior to their creation
    feature, features = None, None
    deltatimeval = None

    points = arcpy.GetParameterAsText(0)
    datetimefield = arcpy.GetParameterAsText(1)
    deltatimefield = arcpy.GetParameterAsText(2)
    guidfield = arcpy.GetParameterAsText(3)
    maxdeltatime = arcpy.GetParameterAsText(4)

    maxdeltatime = float(maxdeltatime)    
    
    features = arcpy.UpdateCursor(points,"",None,"",datetimefield + " A")
    feature = features.next()

    guid = uuid.uuid4()

    endoftrack = None    
    
    while feature:
        deltatimeval = feature.getValue(deltatimefield)
        if (deltatimeval > maxdeltatime):
            if endoftrack:
                #start of a new trace, so need new GUID
                guid = uuid.uuid4()
                endoftrack = None
            else:
                endoftrack = "true"
        else:
            endoftrack = None
        feature.setValue(guidfield, "{" + str(guid) + "}")
        features.updateRow(feature)
        feature = features.next()

    arcpy.SetParameterAsText(5, points)
    
except:
    if not arcpy.GetMessages() == "":
        arcpy.AddMessage(arcpy.GetMessages(2))

finally:
    if feature:
        del feature
    if features:
        del features
