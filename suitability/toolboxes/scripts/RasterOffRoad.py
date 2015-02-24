#------------------------------------------------------------------------------
# Copyright 2015 Esri
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
#------------------------------------------------------------------------------

# ==================================================
# RasterOffRoad.py
# --------------------------------------------------
# Built for ArcGIS 10.3
# --------------------------------------------------
#
# ==================================================


# IMPORTS ==========================================
import os, sys, math, traceback, types
import arcpy
from arcpy import da
from arcpy import env
from arcpy import sa

# FUNCTIONS ========================================

# LOCALS ===========================================
deleteme = []
debug = True
GCS_WGS_1984 = arcpy.SpatialReference("WGS 1984")
## webMercator = arcpy.SpatialReference("WGS 1984 Web Mercator (Auxiliary Sphere)")
ccmFactorList = []

# ARGUMENTS ========================================
inputAOI = arcpy.GetParameterAsText(0)

inputVehicleParameterTable = arcpy.GetParameterAsText(1)
inputVehicleType = str(arcpy.GetParameterAsText(2))

inputElevation = arcpy.GetParameterAsText(3)
inputSlope = arcpy.GetParameterAsText(4)

outputCCM = arcpy.GetParameterAsText(5)

inputVegetation = arcpy.GetParameterAsText(6)
inputVegetationConversionTable = arcpy.GetParameterAsText(7)
min_max = arcpy.GetParameterAsText(8) # "MAX" or "MIN", where "MAX" is default

inputSoils = arcpy.GetParameterAsText(9)
inputSoilsTable = arcpy.GetParameterAsText(10)
wet_dry = arcpy.GetParameterAsText(11) # "DRY" or "WET", where "DRY" is default

inputSurfaceRoughness = arcpy.GetParameterAsText(12)
inputSurfaceRoughnessTable = arcpy.GetParameterAsText(13)
commonSpatialReference = arcpy.GetParameter(14)
commonSpatialReferenceAsText = arcpy.GetParameterAsText(14)


# ==================================================

try:

    if debug == True: arcpy.AddMessage("START: " + str(time.strftime("%m/%d/%Y  %H:%M:%S", time.localtime())))
    scratch = env.scratchGDB
    if debug == True: arcpy.AddMessage("scratch: " + str(scratch))
    env.overwriteOutput = True
    env.resample = "NEAREST"
    env.compression = "LZ77"
    env.extent = arcpy.Describe(inputAOI).Extent
    env.mask = inputAOI
    
    calcCellSize = None
    GridSize = 2000.0
    if commonSpatialReferenceAsText == '':
        commonSpatialReference = arcpy.Describe(inputAOI).spatialReference
        arcpy.AddWarning("Spatial Reference is not defined. Using Spatial Reference of Input Area Of Interest: " + str(commonSpatialReference.name))
        calcCellSize = max(arcpy.Describe(inputAOI).Extent.width,arcpy.Describe(inputAOI).Extent.height)/GridSize
    elif commonSpatialReference.type == "Projected":
        inputAOIExtent = arcpy.Describe(inputAOI).extent
        newAOIExtent = inputAOIExtent.projectAs(commonSpatialReference)
        calcCellSize = max(newAOIExtent.width,newAOIExtent.height)/GridSize
    else:
        arcpy.AddError("Undefined Spatial Reference or type is Geographic.\nInput Area of Interest feature or Spatial Reference must be of type Projected.")
        raise
    
    if calcCellSize == 0.0:
        arcpy.AddError("Calculated a zero cell size. Spatial references might not be comparable.")
        raise
    
    env.spatialReference = commonSpatialReference
    env.outputCoordinateSystem = commonSpatialReference
    arcpy.AddMessage("Using cell size: " + str(calcCellSize))
    env.cellSize = calcCellSize
    intersectionList = []

    # Load vehicle Parameters Table into a dictionary
    arcpy.AddMessage("Building vehicle table...")
    vehicleTable = {}
    vehicleRows = arcpy.da.SearchCursor(inputVehicleParameterTable,["OID@","classname","name","weight","maxkph","onslope","offslope"])
    for vehicleRow in vehicleRows:
        oid = vehicleRow[0]
        classname = str(vehicleRow[1])
        name = str(vehicleRow[2])
        weight = float(vehicleRow[3])
        maxkph = float(vehicleRow[4])
        onslope = float(vehicleRow[5])
        offslope = float(vehicleRow[6])
        vehicleTable[name] = [classname,name,weight,maxkph,onslope,offslope]
    del vehicleRows
    if debug == True: arcpy.AddMessage("vehicleTable: " + str(vehicleTable))
    vehicleParams = vehicleTable[inputVehicleType]
    if debug == True: arcpy.AddMessage("vehicleParams: " + str(vehicleParams))

    # Clip slope service layers
    arcpy.AddMessage("Clipping slope...")
    slopeClip = os.path.join(scratch,"slopeClip")
    #arcpy.MakeRasterLayer_management(inputSlope,"SlopeLayer")
    #arcpy.CopyRaster_management("SlopeLayer",slopeClip)
    outSlope = sa.ExtractByMask(inputSlope,inputAOI)
    outSlope.save(slopeClip)
    deleteme.append(slopeClip)

    # Set all Slope values greater than the vehicle's off road max to that value
    arcpy.AddMessage("Reclassifying Slope ...")
    reclassSlope = os.path.join(os.path.dirname(scratch),"reclassSlope.tif")
    if debug == True: arcpy.AddMessage("reclassSlope: " + str(reclassSlope))
    #float(vehicleParams[5])
    if debug == True: arcpy.AddMessage(str(time.strftime("Con: %m/%d/%Y  %H:%M:%S", time.localtime())))
    outCon = sa.Con(sa.Raster(slopeClip) > float(vehicleParams[5]),float(vehicleParams[5]),sa.Raster(slopeClip))
    # FAILS HERE:
    outCon.save(reclassSlope)
    # ERROR 010240: Could not save raster dataset to C:\Workspace\MAoT for A4W\A4W\test.gdb\reclassSlope with output format FGDBR.
    #
    # 010240 : Could not save raster dataset to <value> with output format <value>.
    #
    # Description
    # The output raster dataset could not be created in the specified format. There may already exist an output raster with the
    # same name and format. Certain raster formats have limitations on the range of values that are supported. For example, the GIF
    # format only supports a value range of 0 to 255, which would be a problem if the output raster would have a range of -10 to 365.
    #
    # Solution
    # Check that a raster with the same name and format does not already exist in the output location. Also, check the technical
    # specifications for raster dataset formats to make sure that the expected range of values in the output is compatible with
    # the specified format.
    #
    # WORKAROUND: Saving to a TIF in the scratch gdb's folder worked.


    deleteme.append(reclassSlope)

    # clip Elevaiton to AOI
    arcpy.AddMessage("Clipping Elevation...")
    elevClip = os.path.join(env.scratchGDB,"elevClip")
    #arcpy.MakeRasterLayer_management(inputElevation,"ElevLayer")
    #arcpy.CopyRaster_management("ElevLayer",elevClip)
    outElev = sa.ExtractByMask(inputElevation,inputAOI)
    outElev.save(elevClip)
    deleteme.append(elevClip)

    # make constant raster
    constNoEffect = os.path.join(env.scratchGDB,"constNoEffect")
    outConstNoEffect = sa.CreateConstantRaster(1.0,"FLOAT",env.cellSize,arcpy.Describe(inputAOI).Extent.projectAs(env.outputCoordinateSystem))
    outConstNoEffect.save(constNoEffect)
    deleteme.append(constNoEffect)

    # f1: vehicle parameters
    f1 = os.path.join(env.scratchFolder,"f1.tif")
    # f1 = (vehicle max off-road slope %) - (surface slope %) / (vehicle max on-road slope %) / (vehicle max KPH)
    if debug == True:
        arcpy.AddMessage(str(time.strftime("F1: %m/%d/%Y  %H:%M:%S", time.localtime())))
        arcpy.AddMessage("slopeClip: " + str(slopeClip))
    slopeAsRaster = sa.Raster(reclassSlope)
    outF1 = (float(vehicleParams[5]) - slopeAsRaster) / (float(vehicleParams[4]) / float(vehicleParams[3]))
    outF1.save(f1)
    ccmFactorList.append(f1)
    deleteme.append(f1)


    # f2: surface change
    arcpy.AddMessage("Surface Curvature ...")
    f2 = os.path.join(env.scratchFolder,"f2.tif")
    if debug == True: arcpy.AddMessage(str(time.strftime("Curvature: %m/%d/%Y  %H:%M:%S", time.localtime())))
    # CURVATURE
    curvature = os.path.join(scratch,"curvature")
    curveSA = sa.Curvature(elevClip)
    curveSA.save(curvature)
    deleteme.append(curvature)
    if debug == True: arcpy.AddMessage(str(time.strftime("Focal Stats: %m/%d/%Y  %H:%M:%S", time.localtime())))
    # FOCALSTATISTICS (RANGE)
    focalStats = os.path.join(scratch,"focalStats")
    window = sa.NbrCircle(3,"CELL")
    fstatsSA = sa.FocalStatistics(curvature,window,"RANGE")
    fstatsSA.save(focalStats)
    deleteme.append(focalStats)
    # F2
    maxRasStat = float(str(arcpy.GetRasterProperties_management(focalStats,"MAXIMUM")))
    fsRasStat = sa.Raster(focalStats)
    if debug == True:
        arcpy.AddMessage("maxRasStat: " + str(maxRasStat) + " - " + str(type(maxRasStat)))
        arcpy.AddMessage("fsRasStat: " + str(fsRasStat) + " - " + str(type(fsRasStat)))
    f2Calc = (maxRasStat - fsRasStat) / maxRasStat # (max - cell/max)
    f2Calc.save(f2)
    deleteme.append(f2)
    ccmFactorList.append(f2)

    #TODO: Need more thorough and complete checks of inputs
    #if inputVegetation != types.NoneType and arcpy.Exists(inputVegetation) == True: #UPDATE
    if inputVegetation != None and arcpy.Exists(inputVegetation) == True:
        # f3: vegetation
        f3t = os.path.join(scratch,"f3t")
        #f3 = os.path.join(scratch,"f3") #ERROR 010240 : Could not save raster dataset to <value> with output format <value>.
        f3 = os.path.join(os.path.dirname(scratch),"f3.tif")
        arcpy.AddMessage("Clipping vegetation to fishnet and joining parameter table...")
        vegetation = os.path.join("in_memory","vegetation")
        if debug == True: arcpy.AddMessage(str(time.strftime("Clip Vegetation: %m/%d/%Y  %H:%M:%S", time.localtime())))
        arcpy.Clip_analysis(inputVegetation,inputAOI,vegetation)
        deleteme.append(vegetation)
        arcpy.JoinField_management(vegetation,"f_code",inputVegetationConversionTable,"f_code")
        # Convert vegetation to Raster using MIN or MAX field
        if min_max == "MAX":
            arcpy.PolygonToRaster_conversion(vegetation,"f3max",f3t)
        else:
            arcpy.PolygonToRaster_conversion(vegetation,"f3min",f3t)
        # if F3T is null, make it 1.0 (from constNoEffect), otherwise keep F3T value
        outF3T = sa.Con(sa.IsNull(f3t),constNoEffect,f3t)
        outF3T.save(f3)
        deleteme.append(f3t)
        deleteme.append(f3)
        #TODO: what about areas in the AOI but outside VEG? No effect (value = 1.0)?
        ccmFactorList.append(f3)

    #if inputSoils != types.NoneType and  arcpy.Exists(inputSoils) == True: #UPDATE
    if inputSoils != None and  arcpy.Exists(inputSoils) == True:
        # f4: soils
        f4t = os.path.join(scratch,"f4t")
        #f4 = os.path.join(scratch,"f4") #ERROR 010240 : Could not save raster dataset to <value> with output format <value>.
        f4 = os.path.join(os.path.dirname(scratch),"f4.tif")
        arcpy.AddMessage("Clipping soils to fishnet and joining parameter table...")
        clipSoils = os.path.join("in_memory","clipSoils")
        if debug == True: arcpy.AddMessage(str(time.strftime("Clip Soils: %m/%d/%Y  %H:%M:%S", time.localtime())))
        arcpy.Clip_analysis(inputSoils,inputAOI,clipSoils)
        deleteme.append(clipSoils)
        arcpy.JoinField_management(clipSoils,"soilcode",inputSoilsTable,"soilcode")
        # Convert soils to Raster using WET or DRY field
        if wet_dry == "DRY":
            arcpy.PolygonToRaster_conversion(clipSoils,"f4dry",f4t)
        else:
            arcpy.PolygonToRaster_conversion(clipSoils,"f4wet",f4t)
        deleteme.append(f4t)
        outF4T = sa.Con(sa.IsNull(f4t),constNoEffect,f4t)
        outF4T.save(f4)
        deleteme.append(f4)
        ccmFactorList.append(f4)

    #if inputSurfaceRoughness != types.NoneType and  arcpy.Exists(inputSurfaceRoughness) == True: #UPDATE
    if inputSurfaceRoughness != None and  arcpy.Exists(inputSurfaceRoughness) == True:
        # f5: surface roughness
        f5t = os.path.join(scratch,"f5t")
        #f5 = os.path.join(scratch,"f5") #ERROR 010240 : Could not save raster dataset to <value> with output format <value>.
        f5 = os.path.join(os.path.dirname(scratch),"f5.tif")
        arcpy.AddMessage("Clipping roughness to fishnet and joining parameter table...")
        clipRoughness = os.path.join("in_memory","clipRoughness")
        if debug == True: arcpy.AddMessage(str(time.strftime("Clip Roughness: %m/%d/%Y  %H:%M:%S", time.localtime())))
        arcpy.Clip_analysis(inputSurfaceRoughness,inputAOI,clipRoughness)
        # Join roughness table
        arcpy.JoinField_management(clipRoughness,"roughnesscode",inputRoughnessTable,"roughnesscode")
        intersectionList.append(clipRoughness)
        # Convert surface roughness to raster
        arcpy.PolygonToRaster_conversion(clipRoughness,"f5",f5t)
        deleteme.append(f5t)
        outF5T = sa.Con(sa.IsNull(f5t),constNoEffect,f5t)
        outF5T.save(f5)
        deleteme.append(f5)
        ccmFactorList.append(f5)

    # Map Algebra to calc final CCM
    if debug == True: arcpy.AddMessage("BEFORE: " + str(ccmFactorList) + str(time.strftime(" %m/%d/%Y  %H:%M:%S", time.localtime())))
    tempCCM = os.path.join(env.scratchFolder,"tempCCM.tif")
    targetCCM = ""
    if len(ccmFactorList) == 2:
        if debug == True: arcpy.AddMessage(str(time.strftime("Two factors " + str(ccmFactorList) + " : %m/%d/%Y  %H:%M:%S", time.localtime())))
        targetCCM = sa.Raster(ccmFactorList[0]) * sa.Raster(ccmFactorList[1])
    elif len(ccmFactorList) == 3:
        if debug == True: arcpy.AddMessage(str(time.strftime("Three factors " + str(ccmFactorList) + " : %m/%d/%Y  %H:%M:%S", time.localtime())))
        targetCCM = sa.Raster(ccmFactorList[0]) * sa.Raster(ccmFactorList[1]) * sa.Raster(ccmFactorList[2])
    elif len(ccmFactorList) == 4:
        if debug == True: arcpy.AddMessage(str(time.strftime("Four factors " + str(ccmFactorList) + " : %m/%d/%Y  %H:%M:%S", time.localtime())))
        targetCCM = sa.Raster(ccmFactorList[0]) * sa.Raster(ccmFactorList[1]) * sa.Raster(ccmFactorList[2]) * sa.Raster(ccmFactorList[3])
    elif len(ccmFactorList) == 5:
        if debug == True: arcpy.AddMessage(str(time.strftime("Five factors " + str(ccmFactorList) + " : %m/%d/%Y  %H:%M:%S", time.localtime())))
        targetCCM = sa.Raster(ccmFactorList[0]) * sa.Raster(ccmFactorList[1]) * sa.Raster(ccmFactorList[2]) * sa.Raster(ccmFactorList[3]) * sa.Raster(ccmFactorList[4])
    else:
        if debug == True: arcpy.AddMessage("ERROR!!!!!: " + str(ccmFactorList) + str(time.strftime(" %m/%d/%Y  %H:%M:%S", time.localtime())))
        #raise WrongFactors, ccmFactorList #UPDATE
        arcpy.AddError("Wrong number of ccm factors: " + str(ccmFactorList))
        raise
    
    targetCCM.save(tempCCM)
    arcpy.CopyRaster_management(tempCCM,outputCCM)

    # set the output
    arcpy.SetParameter(5,outputCCM)
    if debug == True: arcpy.AddMessage("DONE: " + str(time.strftime("%m/%d/%Y  %H:%M:%S", time.localtime())))

    # cleanup intermediate datasets
    if debug == True: arcpy.AddMessage("Removing intermediate datasets...")
    for i in deleteme:
        if debug == True: arcpy.AddMessage("Removing: " + str(i))
        if arcpy.Exists(i):
            arcpy.Delete_management(i)
            pass
    if debug == True: arcpy.AddMessage("Done")


except arcpy.ExecuteError:
    if debug == True: arcpy.AddMessage("CRASH: " + str(time.strftime("%m/%d/%Y  %H:%M:%S", time.localtime())))
        # Get the traceback object
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    arcpy.AddError("Traceback: " + tbinfo)
    # Get the tool error messages
    msgs = arcpy.GetMessages()
    arcpy.AddError(msgs)
    #print msgs #UPDATE
    print(msgs)

except:
    if debug == True: arcpy.AddMessage("CRASH: " + str(time.strftime("%m/%d/%Y  %H:%M:%S", time.localtime())))
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
    #print pymsg + "\n" #UPDATE
    print(pymsg + "\n")
    #print msgs #UPDATE
    print(msgs)


