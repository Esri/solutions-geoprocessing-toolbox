#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      qgeddes
#
# Created:     29/04/2013
# Copyright:   (c) qgeddes 2013
# Licence:     <your licence>
#-------------------------------------------------------------------------------

import numpy
try:
    import numpy as np

except:
    msg="""
    The NumPy module is need for this tool. The module can be downloaded at the following address:
    http://sourceforge.net/projects/numpy/files/NumPy/1.6.2
    Download the appropriate superpack installer for windows for your Python version
    ArcGIS 10   uses Python 2.6
    ArcGIS 10.1 uses Python 2.7"""
    arcpy.AddError(dedent(msg))
    raise arcpy.ExecuteError

import scipy
#try:
#    from scipy import stats
#except:
#    msg="""
#    The SciPy module is need for this tool. The module can be downloaded at the following address:
#    http://sourceforge.net/projects/scipy/files/scipy/0.11.0
#    Download the appropriate superpack installer for windows for your Python version
#    ArcGIS 10   uses Python 2.6
#    ArcGIS 10.1 uses Python 2.7"""
#    arcpy.AddError(dedent(msg))
#    raise arcpy.ExecuteError
import ACCACloudDetector


Band2path=      arcpy.GetParameterAsText(0)
Band3path=      arcpy.GetParameterAsText(1)
Band4path=      arcpy.GetParameterAsText(2)
Band5path=      arcpy.GetParameterAsText(3)
Band6path=      arcpy.GetParameterAsText(4)

pixelvalue=     arcpy.GetParameterAsText(5)
MetaData=       arcpy.GetParameterAsText(6)
OutputFolder=   arcpy.GetParameterAsText(7)
OutputFileName= arcpy.GetParameterAsText(8)

Filter5Thresh=float(arcpy.GetParameterAsText(9))
Filter6Thresh=float(arcpy.GetParameterAsText(10))
SaveRefl=arcpy.GetParameter(11)
ReflFolder=arcpy.GetParameterAsText(12)


L7bands=[Band2path,Band3path,Band4path,Band5path,Band6path]
#checking if the file extension is appropriate and making alterations if necessary
FileNameSplit=OutputFileName.split(".")
if FileNameSplit[-1] not in ["tif","img"]:
    arcpy.AddWarning("Output Image must be saved in either the .tif or .img file format.  File has been change to .tif")
    if len(FileNameSplit)==1:
        OutputFileName+=".tif"
    else:
        FileNameSplit[-1]="tif"
        OutputFileName=".".join(FileNameSplit)

arcpy.env.scratchWorkspace=OutputFolder


ACCACloudDetector.ACCACloudDetector(L7bands,
                                    pixelvalue,
                                    OutputFolder+"\\"+OutputFileName,
                                    MetaData,
                                    SaveRefl,
                                    ReflFolder,
                                    Filter5Thresh,
                                    Filter6Thresh)
