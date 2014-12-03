#-------------------------------------------------------------------------------
# Name:        ACCA Cloud Detector
# Purpose:      To execute the Automated Cloud Cover Assesment algorithm on Landsat 7 imagery
#
# Author:      Quinten Geddes   Quinten.A.Geddes@nasa.gov
#               NASA DEVELOP Program
# Created:     13/02/2013

#-------------------------------------------------------------------------------
import arcpy
import math
import sys
from textwrap import dedent
from arcpy.sa import *
import DNtoReflectance
import numpy as np
import scipy
from scipy import stats
import os
arcpy.env.overwriteOutput = True
arcpy.CheckOutExtension("Spatial")
ReflOutputPath = r'C:\Change_Detection_Imagery\cloud'

def ACCACloudDetector(L7bands, pixelvalue, OutputPath,MetaData="",SaveRefl=False,ReflOutputFolder="",Filter5Thresh=2.0,Filter6Thresh=2.0):
    """This function uses the Automated Cloud Cover Assessment algorithm to classify cloud
    cover in a Landsat 7 image using spectral bands 2,3,4, and 5 and thermal band 6.
    The Output image will have binary cell values.  0=cloud, 1= noncloud

    INPUTS----------------

    L7bands: A list of paths to GeoTIFF files containing individual bands of
             Landsat imagery. The order of these bands must be 2 - 3 - 4 - 5 - 6.
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

    Filter5Thresh: This threshold will affect the aggressiveness of the cloud classification.
                    Higher-more aggressive
                    Lower-less aggressive

    Filter6Thresh: This threshold will affect the aggressiveness of the cloud classification.
                    Higher-more aggressive
                    Lower -less aggressive

    OUTPUTS----------------

    The path to a cloud mask for the input image. 0=cloud, 1= noncloud
    """

    Band2,Band3,Band4,Band5,Band6 = "","","","","" #scope errors on vars at 3.4
    if pixelvalue=="Digital Numbers":
        #if pixel values for input bands are Digital Numbers, the following loop will
        # convert pixel values to TOA Reflectance. If SaveRefl is 'True' the Reflectance
        #images will be saved in ReflOutputPath. If ReflOutputPath is not provided,
        # the images will be saved in the containing folder of the OutputPath.

        for i,pathname in enumerate(L7bands):
        #iterating for each input band

            inputbandnum=str(["2","3","4","5","6"][i])

            #Checking whether the Band number in the filename matches up with
            # the appropriate band order band number

            try:
                #attempting to aquire the band number from the filenames
                BandNum=pathname.split("\\")[-1].split("_B")[1][0]
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

        #if ReflOutputFolder is not provided, one is generated using the OutputPath
        if not ReflOutputFolder:
            ReflOutputPath="\\".join(OutputPath.split("\\")[0:-1])
        else:
            ReflOutputPath=ReflOutputFolder

        #Using the DNtoReflectance tool to convert Digital Numbers to Reflectance
        Bands=DNtoReflectance.DNtoReflectance(L7bands,MetaData,Save=SaveRefl,OutputFolder=ReflOutputPath)

        for i,raster in enumerate(Bands):
            #exec("Band{0} = raster".format(["2","3","4","5","6"][i])) # fails in 3.4, use brute force method
            if i == 0: Band2 = raster
            if i == 1: Band3 = raster
            if i == 2: Band4 = raster
            if i == 3: Band5 = raster
            if i == 4: Band6 = raster


    elif pixelvalue=="Reflectance":
        #if the pixel values are in Reflectance, the bands are directly inputed in the algorithm
        for i,pathname in enumerate(L7bands):
            #exec("Band{0} = arcpy.Raster(pathname)".format(["2","3","4","5","6"][i])) # will probably fail in 3.4
            if i == 0: Band2 = arcpy.Raster(pathname)
            if i == 1: Band3 = arcpy.Raster(pathname)
            if i == 2: Band4 = arcpy.Raster(pathname)
            if i == 3: Band5 = arcpy.Raster(pathname)
            if i == 4: Band6 = arcpy.Raster(pathname)

        #if ReflOutputFolder is not provided, one is generated using the OutputPath
        if not ReflOutputFolder:
            ReflOutputPath="\\".join(OutputPath.split("\\")[0:-1])
        else:
            ReflOutputPath=ReflOutputFolder
            
    #Establishing location of gaps in data. 0= Gap, 1=Data
    #This will be used multiple times in later steps
    arcpy.AddMessage("Creating Gap Mask")
    print("Creating Gap Mask")
    GapMask=((Band2>0)*(Band3>0)*(Band4>0)*(Band5>0)*(Band6>0))
    GapMask.save(ReflOutputPath+"\\GapMask.tif")


    arcpy.AddMessage("First pass underway")
    print("First pass underway")

    #Filter 1 - Brightness Threshold--------------------------------------------
    Cloudmask=Band3 >.08

    #Filter 2 - Normalized Snow Difference Index--------------------------------
    NDSI=(Band2-Band5)/(Band2+Band5)
    Snow=(NDSI>.6)*Cloudmask
    Cloudmask=(NDSI<.6)*Cloudmask

    #Filter 3 - Temperature Threshold-------------------------------------------
    Cloudmask=(Band6<300)*Cloudmask

    #Filter 4 - Band 5/6 Composite----------------------------------------------
    Cloudmask=(((1-Band5)*Band6)<225)*Cloudmask
    Amb=(((1-Band5)*Band6)>225)

    #Filter 5 - Band 4/3 Ratio (eliminates vegetation)--------------------------
    #bright cloud tops are sometimes cut out by this filter. original threshold was
    #raising this threshold will make the algorithm more aggresive
    Cloudmask=((Band4/Band3)<Filter5Thresh)*Cloudmask
    Amb=((Band4/Band3)>Filter5Thresh)*Amb

    #Filter 6 - Band 4/2 Ratio (eliminates vegetation)--------------------------
    #bright cloud tops are sometimes cut out by this filter. original threshold was
    #raising this threshold will make the algorithm more aggresive
    Cloudmask=((Band4/Band2)<Filter6Thresh)*Cloudmask
    Amb=((Band4/Band2)>Filter6Thresh)*Amb

    #Filter 7 - Band 4/5 Ratio (Eliminates desert features)---------------------
    #   DesertIndex recorded
    DesertIndMask=((Band4/Band5)>1.0)
    Cloudmask=DesertIndMask*Cloudmask
    Amb=((Band4/Band5)<1.0)*Amb




    #Filter 8  Band 5/6 Composite (Seperates warm and cold clouds)--------------
    WarmCloud=(((1-Band5)*Band6)>210)*Cloudmask
    ColdCloud=(((1-Band5)*Band6)<210)*Cloudmask

    #Calculating percentage of the scene that is classified as Desert
    DesertGap=(DesertIndMask+1)*GapMask
    try:
        arcpy.CalculateStatistics_management(DesertGap,ignore_values="0")
        DesertIndex=DesertGap.mean-1
    except:
        DesertGap.save(ReflOutputPath+"\\Desert.tif")
        arcpy.CalculateStatistics_management(DesertGap,ignore_values="0")
        DesertIndex=DesertGap.mean-1
        os.remove(ReflOutputPath+"\\Desert.tif")
    del DesertIndMask, DesertGap, NDSI


    #Calculating percentage of the scene that is classified as Snow
    ColdCloudGap=(ColdCloud+1)*GapMask
    try:
        arcpy.CalculateStatistics_management(ColdCloudGap,ignore_values="0")
        ColdCloudMean=ColdCloudGap.mean-1
        del ColdCloudGap
    except:
        ColdCloudGap.save(ReflOutputPath+"\\ColdCloud.tif")
        arcpy.CalculateStatistics_management(ColdCloudGap,ignore_values="0")
        ColdCloudMean=ColdCloudGap.mean-1
        os.remove(ReflOutputPath+"\\ColdCloud.tif")
        del ColdCloudGap

    del Band2,Band3,Band4,Band5


    SnowGap=(Snow+1)*GapMask
    try:
        arcpy.CalculateStatistics_management(SnowGap,ignore_values="0")
        SnowPerc=SnowGap.mean-1
        del SnowGap
    except:
        SnowGap.save(ReflOutputPath+"\\Snow.tif")
        arcpy.CalculateStatistics_management(SnowGap,ignore_values="0")
        SnowPerc=SnowGap.mean-1
        os.remove(ReflOutputPath+"\\Snow.tif")
        del SnowGap
    del Snow

    #Determining whether or not snow is present and adjusting the Cloudmask
    #accordinging. If snow is present the Warm Clouds are reclassfied as ambigious
    if SnowPerc>.01:
        SnowPresent=True
        Cloudmask=ColdCloud
        Amb=Amb+WarmCloud
    else:
        SnowPresent=False

    #Collecting statistics for Cloud pixel Temperature values. These will be used in later conditionals
    Tempclouds=Cloudmask*Band6

    Tempclouds.save(ReflOutputPath+"\\TempClouds.tif")
    Band6array=arcpy.RasterToNumPyArray(ReflOutputPath+"\\TempClouds.tif")
    del Tempclouds
    os.remove(ReflOutputPath+"\\TempClouds.tif")

    Band6clouds=Band6array[np.where(Band6array>0)]
    del Band6array
    TempMin=Band6clouds.min()
    TempMax=Band6clouds.max()
    TempMean=Band6clouds.mean()
    TempStd=Band6clouds.std()
    TempSkew=stats.skew(Band6clouds)
    Temp98perc=stats.scoreatpercentile(Band6clouds, 98.75)
    Temp97perc=stats.scoreatpercentile(Band6clouds, 97.50)
    Temp82perc=stats.scoreatpercentile(Band6clouds, 82.50)
    del Band6clouds

    #Pass 2 is run if the following conditionals are met
    if ColdCloudMean>.004 and DesertIndex>.5 and TempMean<295:
        #Pass 2
        arcpy.AddMessage("Second Pass underway")

        #Adjusting Temperature thresholds based on skew
        if TempSkew>0:
            if TempSkew>1:
                shift=TempStd
            else:
                shift = TempStd*TempSkew
        else: shift=0
        Temp97perc+=shift
        Temp82perc+=shift
        if Temp97perc>Temp98perc:
            Temp82perc=Temp82perc-(Temp97perc-Temp98perc)
            Temp97perc=Temp98perc

        warmAmbmask=((Band6*Amb)<Temp97perc)
        warmAmbmask=warmAmbmask*((Amb*Band6)>Temp82perc)

        coldAmbmask=(Band6*Amb)<Temp82perc
        coldAmbmask=coldAmbmask*((Amb*Band6)>0)

        warmAmb=warmAmbmask*Band6
        coldAmb=coldAmbmask*Band6

        ThermEffect1=warmAmbmask.mean
        ThermEffect2=coldAmbmask.mean

        arcpy.CalculateStatistics_management(warmAmb,ignore_values="0")
        arcpy.CalculateStatistics_management(coldAmb,ignore_values="0")

        if ThermEffect1<.4 and warmAmb.mean<295 and SnowPresent==False:
            Cloudmask=Cloudmask+warmAmbmask+coldAmbmask
            arcpy.AddMessage("Upper Threshold Used")
        elif ThermEffect2<.4 and coldAmb.mean<295:
            Cloudmask=Cloudmask+coldAmbmask
            arcpy.AddMessage("Lower Threshold Used")

    #switch legend to 1=good data 0 = cloud pixel

    Cloudmask=Reclassify(Cloudmask,"Value",RemapValue([[1,0],[0,1],["NODATA",1]]))
    Cloudmask.save(OutputPath)
    del GapMask

    os.remove(ReflOutputPath+"\\GapMask.tif")
    return Cloudmask
