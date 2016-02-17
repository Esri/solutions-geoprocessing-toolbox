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
ImportCRU_CL2ToRaster.py
--------------------------------------------------
requirments: ArcGIS 10.3+, Python 2.7
author: ArcGIS Solutions
company: Esri
==================================================
description:
Import Climate Resarch Unit CL 2.0 10' grids to raster
==================================================
history:
2/18/2014 - mf - original development
12/2/2015 - mf - updates for move into MAoW
==================================================
'''

# IMPORTS ==========================================
import os, sys, traceback, gzip, glob
import arcpy
from arcpy import env

# LOCALS ===========================================
deleteme = [] # intermediate datasets to be deleted
debug = True # extra messaging during development

headerGeneral = r"lat,lon,jan,feb,mar,apr,may,jun,jul,aug,sep,oct,nov,dec"
headerPrecip = r"lat,lon,jan,feb,mar,apr,may,jun,jul,aug,sep,oct,nov,dec,jancv,febcv,marcv,aprcv,maycv,juncv,julcv,augcv,sepcv,octcv,novcv,deccv"
headerElev = r"lat,lon,elev"
cl2Types = {"dtr":"Diurnal Temperature Range (C)","elv":"Elevation (km)","frs":"No Frost Days","pre":"Precipitation (mm)","rd0":"No Wet Days","reh":"Relative Humidity (%)","sunp":"Sunshine (max %)","tmp":"Mean Temp (C)","wnd":"Windspeed (m/s)"}
fieldList = ["jan","feb","mar","apr","may","jun","jul","aug","sep","oct","nov","dec"]
datFiles = []
featureClasses = []
outputRasterDatasets = []
GCS_WGS_1984 = arcpy.SpatialReference(4326)


# FUNCTIONS =======================================
def extract_archive(gzFile):
    ''' get the data from the GZ file archive '''
    arcpy.AddMessage("Extracting and converting " + os.path.basename(gzFile))
    
    if os.path.splitext(gzFile)[0].find("_pre.") != -1:
        header = headerPrecip
    elif os.path.splitext(gzFile)[0].find("_elv.") != -1:
        header = headerElev
    else:
        header = headerGeneral

    
    # open the archive
    gzOpen = gzip.open(gzFile,'rb')

    # make the output name
    newFilename0 = os.path.splitext(gzFile)[0]
    newFilename = str(os.path.splitext(newFilename0)[0]) + ".csv"
    outFile = open(newFilename,'w')    

    # write header
    outFile.write(header)
    # read line, convert, write line
    for line in gzOpen.readlines():
        after = ",".join(line.split())
        outFile.writelines("\n" + after)
    
    outFile.close()
    gzOpen.close()
    
    return newFilename

def pointName(datFile):
    ''' make a point feature class file name '''
    d = os.path.dirname(datFile)
    f = os.path.basename(datFile)
    f = str(f)
    f = f[11:]
    f = f.split(".")[0]
    f = f + "_pnt"
    if arcpy.Describe(d).workspaceType == "FileSystem":
        f = f + ".shp"
    return os.path.join(d,f)

def pointFieldToRaster(pntFile, fieldName):
    '''  '''
    pass
    return

# ARGUMENTS ========================================
import_archive_folder = arcpy.GetParameterAsText(0)
output_raster_workspace = arcpy.GetParameterAsText(1)


def main():
    ''' main script function to put it all together '''
    try:
        # get/set environment
        env.overwriteOutput = True
        env.scratchWorkspace = import_archive_folder
        
        # get list of GZ files in the import folder
        gzFiles = glob.glob(os.path.join(import_archive_folder,"*.gz"))
        if debug == True: arcpy.AddMessage("Found these files: " + str(gzFiles))
        
        # GZ To Table
        for gzFile in gzFiles:
            datFiles.append(extract_archive(gzFile))
        
        # Table To Points  
        for datFile in datFiles:
            
            pntFile = pointName(datFile)
            
            arcpy.AddMessage("Converting " + os.path.basename(datFile) + " to points (" + os.path.basename(pntFile) + "). This will take several minutes.")
            # arcpy.MakeXYEventLayer_management(datFile, "lon", "lat", os.path.basename(datFile),GCS_WGS_1984, "")
            # arcpy.FeatureClassToFeatureClass_conversion(os.path.basename(datFile), os.path.dirname(pntFile), os.path.basename(pntFile))
            arcpy.ConvertCoordinateNotation_management(datFile,pntFile,"lon","lat","DD_2","DD_NUMERIC","",GCS_WGS_1984, GCS_WGS_1984)
            featureClasses.append(pntFile)
                    
            # Points To Rasters
            if pntFile.find("elv") != -1:
                outRasterDataset = os.path.join(output_raster_workspace,"elv_ras")
                # process as elevation
                arcpy.AddMessage("Building " + "elv_ras")
                arcpy.PointToRaster_conversion(pntFile,"elev",outRasterDataset)
                outputRasterDatasets.append(outRasterDataset)
                                               
            else:
                for monthField in fieldList:
                    outRasterName = os.path.basename(pntFile).split("_")[0] + "_" + str(monthField)
                    if (arcpy.Describe(output_raster_workspace).workspaceType == "FileSystem"):
                        outRasterName = outRasterName + ".tif"  # if our output workspace is a folder, make the rasters as TIFFs
                    outRasterDataset= os.path.join(output_raster_workspace,outRasterName)
                    arcpy.AddMessage("Building " + outRasterName)
                    if debug == True: arcpy.AddMessage("RasterDataset: " + str(outRasterDataset))
                    arcpy.PointToRaster_conversion(pntFile,monthField,outRasterDataset)
                    outputRasterDatasets.append(outRasterDataset)
                    
        
        if debug == True: arcpy.AddMessage("DONE -----------------")
        # Set output
        arcpy.SetParameter(2,outputRasterDatasets)
        
    
    
    except arcpy.ExecuteError: 
        # Get the tool error messages 
        msgs = arcpy.GetMessages() 
        arcpy.AddError(msgs) 
        print(msgs)
    
    except:
        # Get the traceback object
        tb = sys.exc_info()[2]
        tbinfo = traceback.format_tb(tb)[0]
    
        # Concatenate information together concerning the error into a message string
        pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
        msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"
    
        # Return python error messages for use in script tool or Python Window
        arcpy.AddError(pymsg)
        arcpy.AddError(msgs)
    
        # Print Python error messages for use in Python / Python Window
        print(pymsg + "\n")
        print(msgs)

    finally:
        if debug == False and len(deleteme) > 0:
            # cleanup intermediate datasets
            if debug == True: arcpy.AddMessage("Removing intermediate datasets...")
            for i in deleteme:
                if debug == True: arcpy.AddMessage("Removing: " + str(i))
                arcpy.Delete_management(i)
            if debug == True: arcpy.AddMessage("Done")

# MAIN =============================================
if __name__ == "__main__":
    main()
