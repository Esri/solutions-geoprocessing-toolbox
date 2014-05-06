#--------ESRI 2010-------------------------------------
# Identify GPS Spikes
# This script looks at distances and bearings
# between points in a featureclass and, given
# a max distance value and max deviation,
# identifies potential spikes (exceeding both
# max values)
# INPUTS: 
#    Input Points Feature Class (FEATURECLASS)
#    Distance Field - holding dist from last point to this (FIELD)
#    Bearing Field - holding deviation around this point (FIELD)
#    DateTime Field - holding the GPS Timestamp (FIELD)
#    Spike Field - this script will set it to 'True' for spikes (FIELD)
#    Maximum Distance - value above which points are considered potential spikes (DOUBLE)
#    Maximum Deviation - value above which points are considered potential spikes (DOUBLE)
# OUTPUTS:
#    Output Points (DERIVED FEATURECLASS)
# 
# Date: June 10, 2010
#------------------------------------------------------

import arcpy
import time
import datetime
import math

try:
    #set features and cursors so that they are deletable in
    #'finally' block should the script fail prior to their creation
    feature, features, nextfeature, findfeatures = None, None, None, None
    distanceval = None
    bearingval = None

    points = arcpy.GetParameterAsText(0)
    distancefield = arcpy.GetParameterAsText(1)
    bearingfield = arcpy.GetParameterAsText(2)
    datetimefield = arcpy.GetParameterAsText(3)
    spikefield = arcpy.GetParameterAsText(4)
    maxdistance = arcpy.GetParameterAsText(5)
    maxdeviation = arcpy.GetParameterAsText(6)

    maxdistance = float(maxdistance)
    maxdeviation = float(maxdeviation)

    features = arcpy.UpdateCursor(points,"",None,"",datetimefield + " A")
    findfeatures = arcpy.SearchCursor(points,"",None,"",datetimefield + " A")
    feature = features.next()
    nextfeature = findfeatures.next()
    
    while feature:
        nextfeature = findfeatures.next()
        distanceval = feature.getValue(distancefield)
        bearingval = feature.getValue(bearingfield)
        feature.setValue(spikefield, "false")
        if (distanceval > maxdistance):
            #unusually high distance - could be a spike if it's the last point or if the next point also shows a high distance (returning from the outlier)
            if nextfeature:
                nextdistanceval = nextfeature.getValue(distancefield)
            else:
                nextdistanceval = distanceval
            if (nextdistanceval > maxdistance):
                #2 high distances in a row, suggests out and back from a spike so check for accompanying change in deviation
                if nextfeature:
                    nextbearingval = nextfeature.getValue(bearingfield)
                    deviation = math.fabs(nextbearingval - bearingval)
                    if (deviation > maxdeviation) and ((360 - deviation) > maxdeviation):
                        feature.setValue(spikefield, "true")
        features.updateRow(feature)
        feature = features.next()

    arcpy.SetParameterAsText(7, points)    

except:
    if not arcpy.GetMessages() == "":
        arcpy.AddMessage(arcpy.GetMessages(2))

finally:
    if feature:
        del feature
    if features:
        del features
    if nextfeature:
        del nextfeature
    if findfeatures:
        del findfeatures
