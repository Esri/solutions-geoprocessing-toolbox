#--------ESRI 2010-------------------------------------
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
# Get Upper Value
# This script will return the value of
# infield which represents the value higher
# than which only x% of values lie (which
# are likely to include any outliers)
# INPUTS:
#    Input Table (TABLE)
#    Field to test (FIELD)
#    Proportion (x) to test (FLOAT)
# OUTPUTS:
#    Output Value (STRING)
#
# Date: June 10, 2010
#------------------------------------------------------

import arcpy

try:
    #set features and cursors so that they are deletable in
    #'finally' block should the script fail prior to their creation
    feature, features = None, None

    inTable = arcpy.GetParameterAsText(0)
    inField = arcpy.GetParameterAsText(1)
    inPercent = arcpy.GetParameterAsText(2)

    numrows = int(arcpy.GetCount_management(inTable).getOutput(0))
    arcpy.AddMessage(str(numrows) + " rows")
    upperval = 0
    count = 0

    features = arcpy.SearchCursor(inTable,"",None,"",inField + " A")
    #feature = features.next() #UPDATE
    feature = next(features)

    while feature:
        count += 1
        if (count >= numrows * (1- float(inPercent))):
            upperval = feature.getValue(inField)
            break
        #feature = features.next() #UPDATE
        feature = nextxt(features)

    arcpy.AddMessage("Cut-off Value = " + str(upperval))

    arcpy.SetParameterAsText(3, upperval)

except:
    if not arcpy.GetMessages() == "":
        arcpy.AddMessage(arcpy.GetMessages(2))

finally:
    if feature:
        del feature
    if features:
        del features
