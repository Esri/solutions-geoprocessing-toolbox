#-------------------------------------------------------------------------------
# Name:        LTK Cloud Detector
# Purpose:      To execute the LTK cloud detection algorithm on Landsat 7 imagery
#
# Author:      Quinten Geddes     Quinten.A.Geddes
#               NASA DEVELOP Progra,
# Created:     15/02/2013

#-------------------------------------------------------------------------------
from glob import glob
import arcpy
arcpy.env.overwriteOutput = True
import sys
import os
import math
import tempfile
import DNtoReflectance
from textwrap import dedent
arcpy.CheckOutExtension("Spatial")

def LTKCloudDetector(Bands1345, pixelvalue, OutputPath,MetaData="",SaveRefl=False,ReflOutputFolder=""):
    """This function uses the LTK algorithm to classify cloud
    cover in a Landsat 7 image using spectral bands 1, 3, 4, and 5.
    The Output image will have binary cell values.  0=cloud, 1= noncloud

    INPUTS----------------

    L7bands: A list of paths to GeoTIFF files containing individual bands of
             Landsat imagery. The order of these bands must be 1 - 3 - 4 - 5.
             These images may have pixel values that correspond to TOA Reflectance
             or Digital Numbers.If Digital Numbers are provided, then the bands
             must have the original filenames as downloaded from the USGS

    pixelvalue: Specify whether the pixel values of L7bands represent Reflectance or Digital Numbers

    OutputPath: Destination of the final output cloud mask. This mask must have either the .img or .tif extension

    MetaData: If the pixelvalue is Digital Numbers, this parameter is required for the conversion to TOA reflectance

    SaveRefl: Indicate whethere or not the intermediate reflectance values (if calculated) are saved to disk
                Default value is False

    ReflOutputFolder: If SaveRefl is True, this parameter indicates where to save Reflectance images.
                        If SaveRelf is True and this parameter is not provided, the Reflectance images
                        will be save in the containing folder of the OutputPath

    OUTPUTS----------------

    The path to a cloud mask for the input image. 0=cloud, 1= noncloud
    """

    #checking if the file extension is appropriate and making alterations if necessary
    FileNameSplit=OutputPath.split(".")
    if FileNameSplit[-1] not in ["tif","img"]:
        msg=dedent("""
        Output Image must be saved in either the .tif or .img file format.
        File has been change to .tif""")
        arcpy.AddWarning(msg)
        print(msg)
        if len(FileNameSplit)==1:
            OutputFileName+=".tif"
        else:
            FileNameSplit[-1]="tif"
            OutputFileName=".".join(FileNameSplit)


    if pixelvalue=="Digital Numbers":
        #if pixel values for input bands are Digital Numbers, the following loop will
        # convert pixel values to TOA Reflectance. If SaveRefl is 'True' the Reflectance
        #images will be saved in ReflOutputPath. If ReflOutputPath is not provided,
        # the images will be saved in the containing folder of the OutputPath.
        for i,pathname in enumerate(Bands1345):
            inputbandnum=str(["1","3","4","5"][i])
            try:
                BandNum=pathname.split("\\")[-1].split("_B")[1][0]


            #Checking whether the Band number in the filename matches up with
            # the appropriate band order band number
            except:
                msg=dedent("""
                Error reading Band {0}.
                Bands must have original names as downloaded.""".format(str(inputbandnum)))
                arcpy.AddError(msg)
                print(msg)
                raise arcpy.ExecuteError
            if BandNum!=inputbandnum:
                msg=dedent("""
                Error reading Band {0}.
                Bands must have original names as downloaded.
                The inputed file appears to actually be Band {1} data""".format(inputbandnum,BandNum))
                arcpy.AddError(msg)
                print(msg)
                raise arcpy.ExecuteError
        if not ReflOutputFolder:
            ReflOutputPath="\\".join(OutputPath.split("\\")[0:-1])
        else:
            ReflOutputPath=ReflOutputFolder
        Bands=DNtoReflectance.DNtoReflectance(Bands1345,MetaData,Save=SaveRefl,OutputFolder=ReflOutputPath)

        for i,raster in enumerate(Bands):
            exec("Band{0}=raster".format(["1","3","4","5"][i]))


    elif pixelvalue=="Reflectance":
        for i,pathname in enumerate(Bands1345):
            exec("Band{0}=arcpy.Raster(pathname)".format(["1","3","4","5"][i]))
    arcpy.AddMessage("Creating Gap Mask")
    print("Creating Gap Mask")

    GapMask=((Band1>0)*(Band3>0)*(Band4>0)*(Band5>0))

    arcpy.AddMessage("Beginning LTK algorithm")
    print("Beginning LTK algorithm")

    #Begin of LTK Algorithm---------------------------------------------------------
    #filter 1
    nonveglands=(Band1<Band3)*(Band3<Band4)*(Band4<(Band5*1.07))*(Band5<.65)
    nonveglands=((Band1*.8)<Band3)*(Band3<(.8*Band4))*(Band4<Band5)*(Band3<.22)+nonveglands
    nonveglands=nonveglands>0
    Amb=nonveglands==0

    #filter 2
    SnowIce=Amb*((Band3>.24)*(Band5<.16)*(Band3>Band4))
    SnowIce=SnowIce+((.24>Band3)*(Band3>.18)*(Band5<(Band3-.08))*(Band3>Band4))
    SnowIce=SnowIce>0
    Amb=Amb*(SnowIce==0)

    #filter 3
    Water=Amb*(Band3>Band4)*(Band3>(.67*Band5))*(Band1<.30)*(Band3<.20)
    Water=Water+(Band3>(.8*Band4))*(Band3>(Band5*.67))*(Band3<.06)
    Water=Water>0
    Amb=Amb*(Water==0)

    #filter 4
    maxB1_B3=((Band1>=Band3)*Band1)+((Band3>Band1)*Band3)
    Clouds=Amb*( (((Band1>.15)+(Band3>.18))>0) * (Band5>.12)* (maxB1_B3>(Band5*.67)))

    #set all cloud pixels to 0 and all good pixels to 1. And apply the gap mask
    CloudMask=((Clouds*GapMask)==0)

    CloudMask.save(OutputPath)

    return OutputPath