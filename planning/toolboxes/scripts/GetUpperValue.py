#--------ESRI 2010-------------------------------------
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
    feature = features.next()
    
    while feature:
        count += 1
        if (count >= numrows * (1- float(inPercent))):
            upperval = feature.getValue(inField)
            break
        feature = features.next()
        
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
