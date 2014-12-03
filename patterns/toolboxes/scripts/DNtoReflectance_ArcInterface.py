#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      qgeddes
#
# Created:     26/04/2013
# Copyright:   (c) qgeddes 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import DNtoReflectance
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")
#Variables-----------------------------------------------------------------
Lbands=arcpy.GetParameterAsText(0)
MetaData =arcpy.GetParameterAsText(1)
OutputType=arcpy.GetParameterAsText(2)
OutputFolder=arcpy.GetParameterAsText(3)
#--------------------------------------------------------------------------

#Reading Metadata that pertains to all bands
Lbands=Lbands.split(";")

DNtoReflectance.DNtoReflectance(Lbands,MetaData,OutputType,True,OutputFolder)
