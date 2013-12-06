#------------------------------------------------------------------------------
# Copyright 2013 Esri
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
# Script to deliver ERG geometries

import arcpy
import os
import math
import datetime


def LookUpERG(pChemical, pPlacardID, pSpillSize, pTimeOfDay, pERGdbf):
    # Returns a tuple of {Initial Isolation Distance, Protective Action Distance, Materials, GuideNum}, the first 2 both in meters, the
    # third a list of materials that match the Placard ID passed in (where one was passed in - otherwise this will simply be
    # equal to pChemical) and the last the guide number that relates to the ERG entry

    materialFieldName = "Material"
    placardFieldName = "Placard"
    guideNumFieldName = "GuideNum"

    scriptFolder = os.path.dirname(__file__)
    toolBoxFolder = os.path.dirname(scriptFolder)

    # Identify the where clause and fields to request
    whereClause = materialFieldName + " = '" + pChemical + "'"
    if (pChemical == ""):
        whereClause = placardFieldName + " = " + str(pPlacardID)
        
    prefix = "SM"
    if (pSpillSize == "Large"):
        prefix = "LG"

    timeField = "DWD_DAY"
    if (pTimeOfDay == "Night"):
        timeField = "DWD_NITE"

    iidField = prefix + "_RAD"
    padField = prefix + timeField

    # Look up the dbf file for the relevant distances
    iid = 0
    pad = 0
    materials = ""
    guidenum = ""
    myCount = 0
    for row in arcpy.da.SearchCursor(pERGdbf, (iidField, padField, materialFieldName, guideNumFieldName), whereClause):
        # If there are multiple results, find the highest values
        myCount += 1
        thisIid = row[0]
        thisPad = row[1]
        thisMaterial = row[2]
        guidenum = row[3]
        if (materials != ""):
            materials += " OR "
        materials += thisMaterial
        arcpy.AddMessage("Found " + thisMaterial)
        arcpy.AddMessage("Initial Isolation Distance = " + str(thisIid) + " meters")
        arcpy.AddMessage("Protective Action Distance = " + str(thisPad) + " meters")
        if (thisIid > iid):
            iid = thisIid
        if (thisPad > pad):
            pad = thisPad
            
    # Report if there were multiple results
    if (myCount > 1):
        arcpy.AddMessage("Multiple possible materials found... selecting the maximum distances across all of them:")
        arcpy.AddMessage("Furthest Initial Isolation Distance = " + str(iid) + " meters")
        arcpy.AddMessage("Furthest Protective Action Distance = " + str(pad) + " meters")
        
    # Return a tuple of (IID, PAD, Materials)
    return (iid, pad, materials, guidenum)


def GetProjectedPoint(pPointFeatureRecordSet):
    arcpy.AddMessage("Getting the projected point")
    # Returns a point in a projected coordinate system (could be the same as the input feature set)
    for row in arcpy.da.SearchCursor(pPointFeatureRecordSet, ["SHAPE@",]):
        geom = row[0]
        pt = geom.firstPoint
        sr = geom.spatialReference
        if (sr.type == "Geographic"):
            arcpy.AddMessage("Point is in Geographic reference system (" + sr.name + ")")
            arcpy.AddMessage("Projecting to...")
            # The following code is taken from the previous (.NET) version of ERG to assign a UTM based on NAD27
            uTMConstantValue = int(math.floor((pt.X - 3) / 6 + 0.5) + 31)
            if (uTMConstantValue > 60):
                uTMConstantValue = 60
            arcpy.AddMessage("  UTM Zone: " + str(uTMConstantValue))
            if (pt.Y) > 0:
                if (uTMConstantValue < 10):
                    esriPRConstant = "3260" + str(uTMConstantValue)
                else:
                    esriPRConstant = "326" + str(uTMConstantValue)
            else:
                if (uTMConstantValue < 10):
                    esriPRConstant = "3270" + str(uTMConstantValue)
                else:
                    esriPRConstant = "327" + str(uTMConstantValue)
            arcpy.AddMessage("  Factory code: " + esriPRConstant)
            srUTM = arcpy.SpatialReference(int(esriPRConstant))
            newgeom = geom.projectAs(srUTM)
            if newgeom == None:
                arcpy.AddError("Failed to project point to UTM")
                return None
            if newgeom.firstPoint == None:
                arcpy.AddError("Reprojection to UTM resulted in no point being returned")
                return None
        else:
            newgeom = geom
        return newgeom


def MakeERGFeatures(pProjectedPointGeometry, pWindBlowingToDirection, pInitialIsolationDistance, pProtectiveActionDistance,
                    pMaterials, pGuideNum, pSpillSize, pTimeOfDay, pOutAreas, pOutLines, pTemplateLoc):
    # Creates 3 polygon features in pOutAreas:-
    #   Initial Isolation Zone
    #   Protective Action Zone
    #   Combined Zone
    # and 3 line features in pOutLines:-
    #   Protective Action Arc
    #   Protective Action Radial (1)
    #   Protective Action Radial (2)

    # ASSUMPTION: The wind direction is relative to grid north of the projected coordinate system of the supplied point

    # Convert the supplied distances into meters (if needed)
    sr = pProjectedPointGeometry.spatialReference
    metersPerUnit = sr.metersPerUnit
    arcpy.AddMessage("Metres per map unit: " + str(metersPerUnit))
    iiDistanceInSrUnits = pInitialIsolationDistance / metersPerUnit
    paDistanceInSrUnits = pProtectiveActionDistance / metersPerUnit
    arcpy.AddMessage("IID: " + str(iiDistanceInSrUnits))
    arcpy.AddMessage("PAD: " + str(paDistanceInSrUnits))

    # Compute the initial isolation zone
    # (note the resulting polygon will contain circular arcs, which do not project well, so we will densify later)
    initialIsolationZone = pProjectedPointGeometry.buffer(iiDistanceInSrUnits)
    
    # Given the wind direction and the protective action distance, compute the X and Y components of the associated vector
    vectorX = paDistanceInSrUnits * math.sin(math.radians(float(pWindBlowingToDirection)))
    vectorY = paDistanceInSrUnits * math.cos(math.radians(float(pWindBlowingToDirection)))

    # Get the X and Y values of the spill point
    originX = pProjectedPointGeometry.firstPoint.X
    originY = pProjectedPointGeometry.firstPoint.Y

    # Calculate the 4 corners of the protective action zone
    paPoint1 = arcpy.Point(originX - vectorY/2, originY + vectorX/2)
    paPoint4 = arcpy.Point(originX + vectorY/2, originY - vectorX/2)
    paPoint2 = arcpy.Point(paPoint1.X + vectorX, paPoint1.Y + vectorY)
    paPoint3 = arcpy.Point(paPoint4.X + vectorX, paPoint4.Y + vectorY)

    # Generate the protective action zone
    array = arcpy.Array([paPoint1, paPoint2, paPoint3, paPoint4, paPoint1])
    protectiveActionZone = arcpy.Polygon(array, sr)

    # Also generate an extended zone for later computation of the protective action arc (to ensure it remains single part)
    vectorX *= 1.5
    vectorY *= 1.5
    paPoint2Ext = arcpy.Point(paPoint1.X + vectorX, paPoint1.Y + vectorY)
    paPoint3Ext = arcpy.Point(paPoint4.X + vectorX, paPoint4.Y + vectorY)
    arrayExt = arcpy.Array([paPoint1, paPoint2Ext, paPoint3Ext, paPoint4, paPoint1])
    paZoneExt = arcpy.Polygon(arrayExt, sr)

    # arcpy.Densify_edit(initialIsolationZone, "ANGLE", "", "", "1.0")
    # Apply trick to densify the initial isolation zone (i.e. to remove circular arcs in case of reprojection of the result)
    diff = initialIsolationZone.difference(protectiveActionZone)
    intsct = initialIsolationZone.intersect(protectiveActionZone, 4)
    initialIsolationZone = diff.union(intsct)

    # Compute the combined zone (iiz + paz)
    combinedZone = diff.union(protectiveActionZone)

    # Compute the "protective action arc" - the arc at the limit of the protective action zone
    paCircle = pProjectedPointGeometry.buffer(paDistanceInSrUnits)
    protectiveActionArc = paZoneExt.intersect(paCircle.boundary(), 2)

    # Compute the "radials" - the lines connecting the edges of the initial isolation zone to the ends of the protective action arc
    innerArc = protectiveActionZone.intersect(initialIsolationZone.boundary(), 2)
    radial1Array = arcpy.Array([innerArc.firstPoint, protectiveActionArc.firstPoint])
    radial2Array = arcpy.Array([innerArc.lastPoint, protectiveActionArc.lastPoint])
    protectiveActionRadial1 = arcpy.Polyline(radial1Array, sr)
    protectiveActionRadial2 = arcpy.Polyline(radial2Array, sr)

    arcpy.AddMessage("All output geometries have been calculated")

    # Create the output featureclasses based on the templates
    outWorkspaceAreas = os.path.dirname(pOutAreas)
    outAreas = os.path.basename(pOutAreas)
    outWorkspaceLines = os.path.dirname(pOutLines)
    outLines = os.path.basename(pOutLines)
    arcpy.AddMessage("Creating output polygon Feature Class...")
    arcpy.CreateFeatureclass_management(outWorkspaceAreas, outAreas, "POLYGON", pTemplateLoc + "\\ERGAreas", "DISABLED", "DISABLED", sr)
    arcpy.AddMessage("...created")
    arcpy.AddMessage("Creating output line Feature Class...")
    arcpy.CreateFeatureclass_management(outWorkspaceLines, outLines, "POLYLINE", pTemplateLoc + "\\ERGLines", "DISABLED", "DISABLED", sr)
    arcpy.AddMessage("...created")

    # Get the current date/time
    dtNow = datetime.datetime.now()
    
    # Create an insert cursor on pOutAreas and insert the polygon geometries
    arcpy.AddMessage("Populating output polygon Feature Class...")
    cursor = arcpy.da.InsertCursor(pOutAreas, ("SHAPE@", "X", "Y", "ERGZone", "Materials", "SpillTimeOfDay", "SpillSize", "DateEntered", "GuideNum"))
    cursor.insertRow((combinedZone, originX, originY, "Combined Zone", pMaterials, pTimeOfDay, pSpillSize, dtNow, pGuideNum))
    cursor.insertRow((protectiveActionZone, originX, originY, "Protective Action Zone", pMaterials, pTimeOfDay, pSpillSize, dtNow, pGuideNum))
    cursor.insertRow((initialIsolationZone, originX, originY, "Initial Isolation Zone", pMaterials, pTimeOfDay, pSpillSize, dtNow, pGuideNum))
    del cursor
    arcpy.AddMessage("...populated")
    
    # Create an insert cursor on pOutLines and insert the polyline geometries
    arcpy.AddMessage("Populating output line Feature Class...")
    cur = arcpy.da.InsertCursor(pOutLines, ("SHAPE@", "X", "Y", "LineType", "Materials", "SpillTimeOfDay", "SpillSize", "DateEntered", "GuideNum"))
    cur.insertRow((protectiveActionArc, originX, originY, "Arc", pMaterials, pTimeOfDay, pSpillSize, dtNow, pGuideNum))
    cur.insertRow((protectiveActionRadial1, originX, originY, "Radial", pMaterials, pTimeOfDay, pSpillSize, dtNow, pGuideNum))
    cur.insertRow((protectiveActionRadial2, originX, originY, "Radial", pMaterials, pTimeOfDay, pSpillSize, dtNow, pGuideNum))
    del cur
    arcpy.AddMessage("...populated")
    

    return
