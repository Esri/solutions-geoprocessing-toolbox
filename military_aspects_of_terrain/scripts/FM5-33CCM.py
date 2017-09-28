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
# FM5-33CCM.py
# --------------------------------------------------
# Built for ArcGIS 10.1
# ==================================================
# 2/4/2015 - mf - Updates to change Web Mercator to user-selected coordinate system


# IMPORTS ==========================================
import os, sys, math, traceback, random, types
import arcpy
from arcpy import env
from arcpy import da
from arcpy import sa


# CONSTANTS ========================================
# VITD/FACC veg table
# {<key>:[<description>,<min_VR>,<max_VR>]}
# NOTE: min/max VR numbers estimated from FM 5-33/MIL-P-89305A
#FACC_veg_tab = {"AL020":["Built-Up Area",0.0,0.0],
#                "BH070":["Brush",0.60,0.70],
#                "BH077":["Hummock",0.0,0.0],
#                "BH090":["Land subject to inundation",0.30,0.60],
#                "BH095":["Marsh/Swamp",0.10,0.80],
#                "BH135":["Rice Field",0.30,0.60],
#                "BJ110":["Tundra",0.10,0.60],
#                "DA020":["Barren Ground",1.0,1.0],
#                "EA010":["Cropland",0.70,0.90],
#                "EA020":["Hedgerow",0.40,0.60],
#                "EA030":["Nursery",0.40,0.60],
#                "EA031":["Botanical Garden",0.40,0.80],
#                "EA040":["Orchard/Plantation",0.40,0.80],
#                "EA050":["Vineyard",0.40,0.60],
#                "EA055":["Hops",0.40,0.60],
#                "EB010":["Grassland",0.80,0.90],
#                "EB015":["Grass/Scrub/Brush",0.60,0.70],
#                "EB020":["Scrub/Brush/Bush",0.60,0.70],
#                "EB030":["Land Use/Land Cover (Vegetation)",0.0,1.0],
#                "EB070":["Brush",0.50,0.60],
#                "EC005":["Tree",0.40,0.80],
#                "EC010":["Bamboo/Cane",0.30,0.60],
#                "EC015":["Forest",0.40,0.80],
#                "EC020":["Oasis",0.20,0.60],
#                "EC030":["Trees",0.40,0.80],
#                "EC040":["US-Cleared Way/Cut Line/Firebreak UK-Cleared Way/Firebreak",0.30,0.80],
#                "ED010":["Marsh",0.30,0.80],
#                "ED020":["Swamp",0.10,0.70],
#                "EE000":["Miscellaneous Vegetation"],
#                "EE010":["Logging Area",0.30,0.80],
#                "EE020":["Land devoid of vegetation",1.0,1.0]}

# "CATEGORY": [<representative>,<weight>,<kph>,<max slope on-road>,<max slope off-road>]
#vehicle_parameters = {"HEAVY_TRACKED":["M1 Abrams",69.5,72.0,60.0,45.0],
#                      "MEDIUM_TRACKED":["M2 Bradley",27.0,66.0,60.0,45.0],
#                      "LIGHT_TRACKED":["M113 APC",15.5,66.0,60.0,45.0],
#                      "HEAVY_WHEELED":["MRAP Buffalo",24.25,105.0,60.0,45.0],
#                      "MEDIUM_WHEELED":["IAV Stryker",19.0,100.0,60.0,45.0],
#                      "LIGHT_WHEELED":["HMMWV",2.6,144.0,60.0,45.0],
#                      "ATV":["Generic ATV",0.25,90.0,60.0,45.0],
#                      "PACK_ANIMAL":["Wild Ass",0.25,56.0,45.0,45.0]}

# M1 Abrams: http://www.globalsecurity.org/military/systems/ground/m1-specs.htm
#            http://www.fas.org/man/dod-101/sys/land/m1.htm
#           - slope values assumed from above doc "Speed - 60% Slope"
# M2 Bradley: http://www.globalsecurity.org/military/systems/ground/m2-specs.htm
#             http://www.fas.org/man/dod-101/sys/land/m2.htm
#           - used same slope values from M1 Abrams
# M113 APC: http://www.globalsecurity.org/military/systems/ground/m113-specs.htm
#           http://www.fas.org/man/dod-101/sys/land/m113.htm
# MRAP Buffalo: http://www.globalsecurity.org/military/systems/ground/buffalo-specs.htm
#           - used same slope values from IAV Stryker
# IAV Stryker: http://www.globalsecurity.org/military/systems/ground/iav-icv.htm
# HMMWV: http://www.globalsecurity.org/military/systems/ground/m1152-specs.htm
# ATV: estimated
# Pack_Animal: wild-assed guess (ha ha)


###if slope_cat == 1: slope_val = 1.5
###if slope_cat == 2: slope_val = 6.5
###if slope_cat == 3: slope_val = 15.0
###if slope_cat == 4: slope_val = 25.0
###if slope_cat == 5: slope_val = 37.5
###if slope_cat == 6: slope_val = 45.0
slopeMedians = {1:1.5,2:6.5,3:15.0,4:25.0,5:37.5,6:45.0}

# FUNCTIONS ========================================


# LOCALS ===============================
deleteme = []
debug = True
GCS_WGS_1984 = arcpy.SpatialReference("WGS 1984")
webMercator = arcpy.SpatialReference("WGS 1984 Web Mercator (Auxiliary Sphere)")

# ==================================================
# INPUTS
inputAOI = arcpy.GetParameterAsText(0)

inputVehicleParameterTable = arcpy.GetParameterAsText(1)
inputVehicleType = str(arcpy.GetParameterAsText(2))

#inputElevation = arcpy.GetParameterAsText()
inputSlope = arcpy.GetParameterAsText(3)
inputContours = arcpy.GetParameterAsText(4)

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
    scratch = env.scratchWorkspace
    env.overwriteOutput = True
    intersectionList = []

    # set operations
    #TODO: Need more thorough and complete checks of inputs
    #TODO: do we want SIF as an option if no contours?
    #runSIF = False
    # if arcpy.Exists(inputContours) == True:
    #    runSIF = True

    runVegetation = False
    #if inputVegetation != types.NoneType and arcpy.Exists(inputVegetation) == True: #UPDATE
    if inputVegetation != None and arcpy.Exists(inputVegetation) == True:
        runVegetation = True

    runSoils = False
    #if inputSoils != types.NoneType and  arcpy.Exists(inputSoils) == True: UPDATE
    if inputSoils != None and  arcpy.Exists(inputSoils) == True:
        runSoils = True

    runRoughness = False
    #if inputSurfaceRoughness != types.NoneType and  arcpy.Exists(inputSurfaceRoughness) == True: #UPDATE
    if inputSurfaceRoughness != None and  arcpy.Exists(inputSurfaceRoughness) == True:
        runRoughness = True


    # Load vehicle Parameters Table into a dictionary
    if debug == True: arcpy.AddMessage("Building vehicle table...")
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

    if commonSpatialReferenceAsText == "":
        arcpy.AddWarning("Spatial Reference is not defined. Using Spatial Reference of Input Area Of Interest: " + str(commonSpatialReference.name))
        commonSpatialReference = arcpy.Describe(inputAOI).spatialReference

    descAOI = arcpy.Describe(inputAOI)
    env.outputCoordinateSystem = commonSpatialReference
    extAOI = descAOI.Extent


    # get rows/columns/height/width of AOI
    numRows, numCols = 1,1
    height = extAOI.height / 10000
    if ((height - math.trunc(height)) >= 0.5):
        numRows = math.ceil(height)
    else:
        numRows = math.floor(height)
    width = extAOI.width / 10000
    if ((width - math.trunc(width)) >= 0.5):
        numCols = math.ceil(width)
    else:
        numCols = math.floor(width)

    # Tile AOI (each tile should be 10km x 10km)
    prefishnet = os.path.join("in_memory","prefishnet")
    fishnet = os.path.join("in_memory","fishnet")
    originPoint = str(extAOI.XMin) + " " + str(extAOI.YMin)
    axisPoint = str(extAOI.XMin) + " " + str(extAOI.YMax)
    #TODO: check w/ GP, why does this guy not take an arcpy.Point???
    if debug == True: arcpy.AddMessage("fishnet: " + str(time.strftime("%m/%d/%Y  %H:%M:%S", time.localtime())))
    arcpy.CreateFishnet_management(prefishnet,originPoint,axisPoint,10000,10000,numRows,numCols,"#","#","#","POLYGON")
    deleteme.append(prefishnet)
    if debug == True: arcpy.AddMessage("intersect fishnet & AOI: " + str(time.strftime("%m/%d/%Y  %H:%M:%S", time.localtime())))
    arcpy.Intersect_analysis([inputAOI,prefishnet],fishnet)
    deleteme.append(fishnet)

    numTiles = int(arcpy.GetCount_management(fishnet).getOutput(0))
    arcpy.AddMessage("AOI has " + str(numTiles) + " 10km square tiles.")

    fishnetBoundary = os.path.join("in_memory","fishnetBoundary")
    if debug == True: arcpy.AddMessage("fishnet boundary: " + str(time.strftime("%m/%d/%Y  %H:%M:%S", time.localtime())))
    arcpy.Dissolve_management(fishnet,fishnetBoundary)
    deleteme.append(fishnetBoundary)

    # Clip slope service layers over fishnet
    env.extent = fishnetBoundary
    env.mask = fishnetBoundary
    #arcpy.MakeImageServerLayer_management(inputSlope,"SlopeLayer")
    arcpy.MakeRasterLayer_management(inputSlope,"SlopeLayer")

    if runVegetation == True:
        arcpy.AddMessage("Clipping soils to fishnet and joining parameter table...")
        vegetation = os.path.join("in_memory","vegetation")
        if debug == True: arcpy.AddMessage(str(time.strftime("Clip Vegetation: %m/%d/%Y  %H:%M:%S", time.localtime())))
        arcpy.Clip_analysis(inputVegetation,fishnetBoundary,vegetation)
        intersectionList.append(vegetation)
        deleteme.append(vegetation)
        arcpy.JoinField_management(vegetation,"f_code",inputVegetationConversionTable,"f_code")

    if runSoils == True:
        # Clip to AOI
        arcpy.AddMessage("Clipping soils to fishnet and joining parameter table...")
        clipSoils = os.path.join("in_memory","clipSoils")
        if debug == True: arcpy.AddMessage(str(time.strftime("Clip Soils: %m/%d/%Y  %H:%M:%S", time.localtime())))
        arcpy.Clip_analysis(inputSoils,fishnetBoundary,clipSoils)
        deleteme.append(clipSoils)
        # Join soils table
        arcpy.JoinField_management(clipSoils,"soilcode",inputSoilsTable,"soilcode")
        intersectionList.append(clipSoils)

    if runRoughness == True:
        # Clip to AOI
        arcpy.AddMessage("Clipping roughness to fishnet and joining parameter table...")
        clipRoughness = os.path.join("in_memory","clipRoughness")
        if debug == True: arcpy.AddMessage(str(time.strftime("Clip Roughness: %m/%d/%Y  %H:%M:%S", time.localtime())))
        arcpy.Clip_analysis(inputSurfaceRoughness,fishnetBoundary,clipRoughness)
        # Join roughness table
        arcpy.JoinField_management(clipRoughness,"roughnesscode",inputRoughnessTable,"roughnesscode")
        intersectionList.append(clipRoughness)


    remap = r"0 3 1;3 10 2;10 20 3;20 30 4;30 45 5;45 999999999999 6"
    missing_values = "NODATA"
    if debug == True: arcpy.AddMessage(str(time.strftime("copyraster: %m/%d/%Y  %H:%M:%S", time.localtime())))
    scratchSlope = os.path.join("in_memory","scratchSlope")
    arcpy.CopyRaster_management("SlopeLayer",scratchSlope)
    deleteme.append(scratchSlope)
    reclassSlope = os.path.join(scratch,"reclassSlope")
    if debug == True: arcpy.AddMessage(str(time.strftime("Reclassify: %m/%d/%Y  %H:%M:%S", time.localtime())))
    arcpy.AddMessage("Reclassifying slope...")
    reclass = sa.Reclassify(scratchSlope,"VALUE",remap,missing_values)
    reclass.save(reclassSlope)
    deleteme.append(reclassSlope)
    #clean edges
    boundaryClean = os.path.join(scratch,"boundaryClean")
    if debug == True: arcpy.AddMessage(str(time.strftime("BoundaryClean: %m/%d/%Y  %H:%M:%S", time.localtime())))
    clean = sa.BoundaryClean(reclassSlope,"NO_SORT","TWO_WAY")
    clean.save(boundaryClean)
    deleteme.append(boundaryClean)

    # Convert reclassified slope ranges to polygon features
    slopePoly = os.path.join(scratch,"slopePoly")
    if debug == True: arcpy.AddMessage(str(time.strftime("RasterToPolygon: %m/%d/%Y  %H:%M:%S", time.localtime())))
    arcpy.RasterToPolygon_conversion(boundaryClean,slopePoly,"NO_SIMPLIFY","VALUE")
    arcpy.AddField_management(slopePoly,"SlopeCat","SHORT")
    arcpy.CalculateField_management(slopePoly,"SlopeCat","!gridcode!","PYTHON_9.3")
    arcpy.DeleteField_management(slopePoly,"gridcode")

    # Calculate f1 using slope category and vehicle parameters
    # vehicleTable[name] = [classname,name,weight,maxkph,onslope,offslope]
    # vehicleParams = vehicleTable[inputVehicleType]
    arcpy.AddField_management(slopePoly,"f1","DOUBLE")
    expression = "CalcF1(!slopeCat!)"
    # f1 = (max off road slope - ground slope)/(max on road slope / max road speed kph)
    if debug == True: arcpy.AddMessage(str(time.strftime("Calculate F1: %m/%d/%Y  %H:%M:%S", time.localtime())))
    block = "slopeMedians = {1:1.5,2:6.5,3:15.0,4:25.0,5:37.5,6:45.0}\ndef CalcF1(slope_cat):\n   f1 = float((" + str(vehicleParams[5]) + " - slopeMedians[slope_cat]) / (" + str(vehicleParams[4]) + " / " + str(vehicleParams[3]) + "))\n   return f1"
    arcpy.CalculateField_management(slopePoly,"f1",expression,"PYTHON_9.3",block)
    deleteme.append(slopePoly)
    intersectionList.append(slopePoly)

    tileList = [] # this guys keeps track of the tile outputs we need to merge later
    tileNum = 1 # number of tiles
    fishnetRows = arcpy.da.SearchCursor(fishnet,["OID@","SHAPE@"])
    for tile in fishnetRows:
    #
    # FOR EACH TILE IN THE AOI
    #
        arcpy.AddMessage("Processing tile " + str(tileNum) + " of " + str(numTiles))
        if debug == True: arcpy.AddMessage("Start tile " + str(tileNum) + " : " + str(time.strftime("%m/%d/%Y  %H:%M:%S", time.localtime())))
        # get the OID of the fishnet tile feature. we'll use this as the tile id number
        tileOID = tile[0]

        # create a clipping polygon from the tile shape
        tileClip = os.path.join(scratch,"tileClip")
        arcpy.CreateFeatureclass_management(os.path.dirname(tileClip),os.path.basename(tileClip),"POLYGON","#","#","#",env.outputCoordinateSystem)
        arcpy.AddField_management(tileClip,"FnetID","LONG")
        arcpy.CalculateField_management(tileClip,"FnetID",tileOID)
        deleteme.append(tileClip)
        rs = arcpy.da.InsertCursor(tileClip,["SHAPE@"])
        rs.insertRow([tile[1]])
        del rs

        # clip Slope to the tile
        arcpy.AddMessage(str(tileNum) + "     Clipping slope categories to tile boundary...")
        slopeClip = os.path.join(scratch,"slopeClip")
        arcpy.Clip_analysis(slopePoly,tileClip,slopeClip,"#")
        if debug == True: arcpy.AddMessage(str(tileNum) + "     slopeClip has " + str(arcpy.GetCount_management(slopeClip).getOutput(0)) + " slope categories.")
        deleteme.append(slopeClip)
        slopeClipOIDFieldName = arcpy.Describe(slopeClip).OIDFieldName

        arcpy.AddMessage(str(tileNum) + "     Building random OID list...")
        # get the max OID in the slope polygon FCs
        max_OID = 0
        OID_SlopeCat_list = {}

        rows = arcpy.da.SearchCursor(slopeClip,["OID@","SlopeCat"])
        for row in rows:
            i = row[0] # OID
            j = row[1] # SlopeCat
            #if OID_SlopeCat_list.has_key(j): #UPDATE
            if j in OID_SlopeCat_list:
                lst = OID_SlopeCat_list[j]
                lst.append(int(i)) # add the current OID to the slope category dictionary
                OID_SlopeCat_list[j] = lst
            else:
                lst = []
                lst.append(int(i))
                OID_SlopeCat_list[j] = lst
            max_OID = max(max_OID,i) # what is the max OID to this point
        del rows
        OID_list = {}

        for currentSlopeCat in OID_SlopeCat_list: # lets loop through each of the slope categories
            currentList = OID_SlopeCat_list[currentSlopeCat]
            newList = []
            if len(currentList) > 10:
                for x in range(0,10):
                    choice = random.choice(currentList)
                    newList.append(choice)
                    currentList.remove(choice)
            else:
                newList = currentList
            OID_list[currentSlopeCat] = sorted(newList)

        # take values of OID dictionary put into a single sorted list
        sort_OIDs = []
        for i in OID_list:
            for j in OID_list[i]:
                sort_OIDs.append(j)
        sorted(sort_OIDs)

        # build where clause to export polys with selected OIDs
        expression = ""
        for i in sort_OIDs:
            if expression == "":
                expression = slopeClipOIDFieldName + " = " + str(i)
            else:
                expression = expression + " or " + slopeClipOIDFieldName + " = " + str(i)

        arcpy.AddMessage(str(tileNum) + "     Copying random polys from slope categories...")
         # copy the random polys to a new feature class
        randomPoly = os.path.join(scratch,"randomPoly")
        arcpy.FeatureClassToFeatureClass_conversion(slopeClip,os.path.dirname(randomPoly),os.path.basename(randomPoly),expression)
        deleteme.append(randomPoly)

        # generate points within 'selected' polygons -- ARCINFO ONLY!!!!!
        randomPoint = os.path.join(scratch,"randomPoint")
        arcpy.FeatureToPoint_management(randomPoly,randomPoint,"INSIDE")
        deleteme.append(randomPoint)

        # generate diagonals for each point
        arcpy.AddMessage(str(tileNum) + "     Building diagonals...")
        diagonals = os.path.join(scratch,"diagonals")
        arcpy.CreateFeatureclass_management(os.path.dirname(diagonals), os.path.basename(diagonals), "POLYLINE", "#", "#", "#", env.outputCoordinateSystem, "#", "#", "#", "#")
        arcpy.AddField_management(diagonals,"RNDID","LONG")
        deleteme.append(diagonals)
        rows = arcpy.da.SearchCursor(randomPoint,["OID@","SHAPE@XY"])
        insert = arcpy.da.InsertCursor(diagonals,["SHAPE@","RNDID"])
        offset = 500.0 # 1/2 km offsets
        for row in rows:
            rndPtOID = row[0]
            rndPt = row[1]
            # if I'm right this is how we add a multipart line feature
            diagArray1 = arcpy.Array([arcpy.Point(rndPt[0] - offset,rndPt[1] + offset),arcpy.Point(rndPt[0] + offset,rndPt[1] - offset)])
            diagArray2 = arcpy.Array([arcpy.Point(rndPt[0] - offset,rndPt[1] - offset),arcpy.Point(rndPt[0] + offset,rndPt[1] + offset)])
            diagArray = arcpy.Array([diagArray1,diagArray2])
            diagLine = arcpy.Polyline(diagArray)
            insert.insertRow([diagLine,rndPtOID])
        del insert
        del rows

        # Intersect diagonals with contours
        intersects = os.path.join(scratch,"intersects")
        arcpy.AddMessage(str(tileNum) + "     Intersecting diagonals with contours...")
        arcpy.Intersect_analysis([diagonals,inputContours],intersects,"ONLY_FID","#","point")
        deleteme.append(intersects)
        # for some reason Intersect makes multipoints
        intersectSingle = os.path.join(scratch,"intersectSingle")
        arcpy.MultipartToSinglepart_management(intersects,intersectSingle)
        deleteme.append(intersectSingle)

        #Identity of points with slope categories
        pointIdentity = os.path.join(scratch,"pointIdentity")
        arcpy.AddMessage(str(tileNum) + "     Identity slope categories and intersections...")
        arcpy.Identity_analysis(intersectSingle,slopeClip,pointIdentity,"ALL")
        deleteme.append(pointIdentity)

        # Get intercept statistics from intersect points
        arcpy.AddMessage(str(tileNum) + "     Getting intersection statistics...")
        stats1 = os.path.join(scratch,"stats1")
        arcpy.Statistics_analysis(pointIdentity,stats1,[["ID","COUNT"]],"ID")
        deleteme.append(stats1)
        arcpy.JoinField_management(pointIdentity,"ID",stats1,"ID", "FREQUENCY; COUNT_ID")
        stats2 = os.path.join(scratch,"stats2")
        arcpy.Statistics_analysis(pointIdentity,stats2,[["COUNT_ID","MEAN"]], "SlopeCat")
        deleteme.append(stats2)
        arcpy.AddField_management(stats2,"f2","DOUBLE")
        #
        # CALCULATE F2
        arcpy.AddMessage(str(tileNum) + "     Calculating F2 for the tile...")
        #
        # SIF count with adjustment for 100m contour intervals
        codeblock = "import types\ndef calcSIF(meancount):\n   if meancount == None: meancount = 0.0\n   SIF = (280.0 - float((meancount * 100.0)/20.0))/280.0\n   return SIF"
        arcpy.CalculateField_management(stats2,"f2",r"calcSIF(!MEAN_COUNT_ID!)","PYTHON_9.3",codeblock)

        # join intercept stats table to slope polys
        arcpy.AddIndex_management(slopeClip,"SlopeCat","SlopeIndx")
        arcpy.JoinField_management(slopeClip,"SlopeCat",stats2,"SlopeCat")

        # copy to new
        arcpy.AddMessage(str(tileNum) + "     Identity vegetation and intersections...")
        outMobilityTile = os.path.join(scratch,"tile_" + str(tileOID))
        arcpy.CopyFeatures_management(slopeClip,outMobilityTile)
        tileList.append(outMobilityTile)
        deleteme.append(outMobilityTile)

        # TODO: Every 10 tiles, APPEND to output 'tileMerge' (rather than MERGE them at the end)

        if debug == True: arcpy.AddMessage("Finish tile " + str(tileNum) + " : " + str(time.strftime("%m/%d/%Y  %H:%M:%S", time.localtime())))
        arcpy.AddMessage(str(tileNum) + "     Finished with tile...")
        tileNum += 1

    # Merge tiles into one.
    tileMerge = os.path.join("in_memory","tileMerge")
    arcpy.AddMessage("Merging " + str(numTiles) + " tiles for final SIF (F2) count...")
    arcpy.Merge_management(tileList,tileMerge)
    deleteme.append(tileMerge)

    # SlopeCat with f1
    # tileMerge with f2
    f1_f2 = os.path.join(scratch,"f1_f2")
    arcpy.Identity_analysis(slopePoly,tileMerge,f1_f2)
    deleteme.append(f1_f2)

    # vegetation with f3min/f3max OPTIONAL
    # clipSoils with f4wet/f4dry OPTIONAL
    # clipRoughness with f5 OPTIONAL
    if len(intersectionList) == 0:
        arcpy.AddMessage("Identity: F1 & F2 only.")
        arcpy.CopyFeatures_management(f1_f2,outputCCM)
    if len(intersectionList) == 1:
        arcpy.AddMessage("Identity: F1, F2 plus one.")
        if debug == True: arcpy.AddMessage(str(intersectionList))
        arcpy.Identity_analysis(f1_f2,intersectionList[0],outputCCM)
    if len(intersectionList) == 2:
        arcpy.AddMessage("Identity: F1, F2 plus two.")
        if debug == True: arcpy.AddMessage(str(intersectionList))
        twoitem = os.path.join(scratch,"twoitem")
        arcpy.Identity_analysis(intersectionList[0],intersectionList[1],twoitem)
        deleteme.append(twoitem)
        arcpy.Identity_analysis(f1_f2,twoitem,outputCCM)
    if len(intersectionList) == 3:
        arcpy.AddMessage("Identity: F1, F2 plus three.")
        if debug == True: arcpy.AddMessage(str(intersectionList))
        twoitem = os.path.join(scratch,"twoitem")
        arcpy.Identity_analysis(intersectionList[0],intersectionList[1],twoitem)
        deleteme.append(twoitem)
        threeitem = os.path.join(scratch,"threeitem")
        arcpy.Identity_analysis(twoitem,intersectionList[2],threeitem)
        deleteme.append(threeitem)
        arcpy.Identity_analysis(f1_f2,threeitem,outputCCM)

    # make list of applicable factors
    fieldList = arcpy.ListFields(outputCCM)
    inputFactorList = []
    if "f3min" in fieldList: inputFactorList.append("f3min")
    if "f3max" in fieldList: inputFactorList.append("f3max")
    if "f4dry" in fieldList: inputFactorList.append("f4dry")
    if "f4wet" in fieldList: inputFactorList.append("f4wet")
    if "f5" in fieldList: inputFactorList.append("f5")

    #Calc CCM
    arcpy.AddField_management(outputCCM,"ccm","DOUBLE")
    cursorFieldList = ["OID@","ccm","f1","f2"] + inputFactorList
    ccmRows = arcpy.da.UpdateCursor(outputCCM,cursorFieldList)
    for ccmRow in ccmRows:
        ccm = 1.0

        # Start with Vehicle/Slope Parameter F1
        f1 = ccmRow[cursorFieldList.index("f1")]
        #if f1 == types.NoneType: #UPDATE
        if f1 == None:
            f1 = 1.0
            ccmRow[cursorFieldList.index("f1")] = f1
        ccm *= f1

        # Next use Slope-Intercept Frequency Count F2
        f2 = ccmRow[cursorFieldList.index("f2")]
        #if f2 == types.NoneType: #UPDATE
        if f2 == None:
            f2 = 1.0
            ccmRow[cursorFieldList.index("f2")] = f2
        ccm *= f2

        # If using vegetation minimum
        if "f3min" in cursorFieldList:
            f3min = ccmRow[cursorFieldList.index("f3min")]
            #if f3min == types.NoneType: #UPDATE
            if f3min == None:
                f3min = 1.0
                ccmRow[cursorFieldList.index("f3min")] = f3min
            ccm *= f3min

        # if using vegetation maximum
        if "f3max" in cursorFieldList:
            f3max = ccmRow[cursorFieldList.index("f3max")]
            #if f3max == types.NoneType: #UPDATE
            if f3max == None:
                f3max = 1.0
                ccmRow[cursorFieldList.index("f3max")] = f3max
            ccm *= f3max

        # if using dry soils
        if "f4dry" in cursorFieldList:
            f4dry = ccmRow[cursorFieldList.index("f4dry")]
            ##if f4dry == types.NoneType: #UPDATE
            if f4dry == None:
                f4dry = 1.0
                ccmRow[cursorFieldList.index("f4dry")] = f4dry
            ccm *= f4dry

        # if using wet soils
        if "f4wet" in cursorFieldList:
            f4wet = ccmRow[cursorFieldList.index("f4wet")]
            #if f4wet == types.NoneType: #UPDATE
            if f4wet == None:
                f4wet = 1.0
                ccmRow[cursorFieldList.index("f4wet")] = f4wet
            ccm *= f4wet

        # if using surface roughness
        if "f5" in cursorFieldList:
            f5 = ccmRow[cursorFieldList.index("f5")]
            #if f5 == types.NoneType: #UPDATE
            if f5 == None:
                f5 = 1.0
                ccmRow[cursorFieldList.index("f5")] = f5
            ccm *= f5

        ccmRow[1] = ccm
        ccmRows.updateRow(ccmRow)
    del ccmRows


    ## copy temp_mobility to out_mobility and keep certain fields
    dropFields = []
    if debug == True: arcpy.AddMessage("Dropping extraneous fields:")
    fieldList = arcpy.ListFields(outputCCM)
    for field in fieldList:
        if field.name not in ["OBJECTID","Shape","shape","SHAPE","SlopeCat","f_code","soilcode","roughnesscode","f1","f2","f3min","f3max","f4wet","f4dry","f5","ccm",r"Shape_Area",r"Shape_Length"]:
            dropFields.append(field.name)
    if debug == True: arcpy.AddMessage(str(dropFields))
    arcpy.DeleteField_management(outputCCM,dropFields)

    # set the output
    arcpy.SetParameter(5,outputCCM)
    if debug == True: arcpy.AddMessage("DONE: " + str(time.strftime("%m/%d/%Y  %H:%M:%S", time.localtime())))

    # cleanup intermediate datasets
    if debug == True: arcpy.AddMessage("Removing intermediate datasets...")
    for i in deleteme:
        if debug == True: arcpy.AddMessage("Removing: " + str(i))
        if arcpy.Exists(i):
            arcpy.Delete_management(i)
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


