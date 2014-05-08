#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      patr5136
#
# Created:     03/09/2013
# Copyright:   (c) patr5136 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import arcpy, os

if __name__ == '__main__':
    ws = arcpy.GetParameter(0)
    name = arcpy.GetParameterAsText(1)
    infeatures = arcpy.GetParameter(2)
    outpath = os.path.join(ws, name)
    #arcpy.CopyFeatures_management(infeatures, outpath)
    arcpy.SetParameter(3, outpath)
