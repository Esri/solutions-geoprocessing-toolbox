#--------ESRI 2010-------------------------------------
# Calculate Field FloatDate
# This script will calculate the Unix timestamp of a date
# field and populate a 'FloatDate' field with the result
# INPUTS: 
#    Input Table (TABLE)
#    DateTime Field (FIELD)
#    Field in which to store FloatDate (FIELD)
# OUTPUTS:
#    Output Table - derived (TABLE)
# 
# Date: June 30, 2010
#------------------------------------------------------

import arcpy
import datetime, time
from time import mktime

try:
    #set features and cursors so that they are deletable in
    #'finally' block should the script fail prior to their creation
    updatefeat, updt_cursor = None, None

    inTable = arcpy.GetParameterAsText(0)
    inDateField = arcpy.GetParameterAsText(1)
    inFloatDateField = arcpy.GetParameterAsText(2)
   
    updt_cursor = arcpy.UpdateCursor(inTable,"",None,"",inDateField + " A")
    updatefeat = updt_cursor.next()

    
    while updatefeat:
        dt = updatefeat.getValue(inDateField)
        floatdate = mktime(dt.timetuple()) + 1e-6*dt.microsecond
        updatefeat.setValue(inFloatDateField, floatdate)
        updt_cursor.updateRow(updatefeat)
        updatefeat = updt_cursor.next()        
 
    arcpy.SetParameterAsText(3, inTable)

except:
    if not arcpy.GetMessages() == "":
        arcpy.AddMessage(arcpy.GetMessages(2))

finally:
    if updatefeat:
        del updatefeat
    if updt_cursor:
        del updt_cursor
