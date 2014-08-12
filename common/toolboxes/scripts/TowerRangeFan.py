
#------------------------------------------------------------------------------
# Copyright 2014 Esri
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
# UpdateRangeFans.py
# --------------------------------------------------
# Built for ArcGIS 10.1
# ==================================================


# IMPORTS ==========================================
import os, sys, math, traceback, decimal
import arcpy
from arcpy import env
from arcpy import sa

# ARGUMENTS & LOCALS ===============================
defPosFeatClass = arcpy.GetParameterAsText(3)
descField = arcpy.GetParameterAsText(4)
input_surface = arcpy.GetParameterAsText(16)
towerName = arcpy.GetParameterAsText(5)
observation_height = arcpy.GetParameterAsText(13)
weaponModel = arcpy.GetParameterAsText(10)
maxRange = float(arcpy.GetParameterAsText(12)) #1000.0 # meters
geoBearing = float(arcpy.GetParameterAsText(14)) #45.0 # degrees
traversal = float(arcpy.GetParameterAsText(15)) #60.0 # degrees
# The name of the workspace in which the features should be stored
outWorkspace = arcpy.GetParameterAsText(18)
# The name of the featureclass in which the features should be stored
outFeatureClassName = arcpy.GetParameterAsText(17)

outFeature = os.path.join(outWorkspace,outFeatureClassName)
# Check for existence of data before deleting
if arcpy.Exists(outFeature):
    arcpy.Delete_management(outFeature)
    
# Local variables:

deleteme = []
DEBUG = True
leftAngle = 0.0 # degrees
rightAngle = 90.0 # degrees


# CONSTANTS ========================================


# FUNCTIONS ========================================
def Geo2Arithmetic(inAngle):
    outAngle = -1.0
    # force input angle into 0 to 360 range
    if (inAngle > 360.0):
        inAngle = math.fmod(inAngle,360.0)
    
    # if 360, make it zero
    if inAngle == 360.0: inAngle = 0.0
    
    #0 to 90
    if (inAngle >= 0.0 and inAngle <= 90.0):
        outAngle = math.fabs(inAngle - 90.0)
    
    # 90 to 360
    if (inAngle > 90.0 and inAngle < 360.0):
        outAngle = 360.0 - (inAngle - 90.0)
        
    if DEBUG == True: arcpy.AddMessage("G2A inAngle(" + str(inAngle) + "), outAngle(" + str(outAngle) + ")")
    return outAngle

def updateValue(fc, field, value):
    cursor = arcpy.UpdateCursor(fc)
    for row in cursor:
        row.setValue(field, value)
        cursor.updateRow(row)
    return

def zfactor(dataset):
    desc = arcpy.Describe(dataset)
    # if it's not geographic return 1.0
    if desc.spatialReference.type != "Geographic":
        return 1.0
    extent = desc.Extent
    extent_split = [extent.xmin,extent.ymin,extent.xmax,extent.ymax]
       
    top = float(extent_split[3])
    bottom = float(extent_split[1])
    
    #find the mid-latitude of the dataset
    if (top > bottom):
        height = (top - bottom)
        mid = (height/2) + bottom
    elif (top < bottom):  # Unlikely, but just in case
        height = bottom - top
        mid = (height/2) + top
    else: # top == bottom
        mid = top

    # convert degrees to radians
    mid = math.radians(mid)

    # Find length of degree at equator based on spheroid's semi-major axis
    spatial_reference = desc.SpatialReference
    semi_major_axis = spatial_reference.semiMajorAxis # in meters
    equatorial_length_of_degree = ((2.0 * math.pi * float(semi_major_axis))/360.0)

    # function:
    # Z-Factor = 1.0/(111320 * cos(mid-latitude in radians)) 
    decimal.getcontext().prec = 28
    decimal.getcontext().rounding = decimal.ROUND_UP
    a = decimal.Decimal("1.0")
    b = decimal.Decimal(str(equatorial_length_of_degree))
    c = decimal.Decimal(str(math.cos(mid)))
    zfactor = a/(b * c)
    zfactor = "%06f" % (zfactor.__abs__())
    return zfactor

try:

    # Remove special characters and replace spaces with underscores
    scrubbedTowerName = ''.join(e for e in towerName if (e.isalnum() or e == " " or e == "_"))
    scrubbedTowerName = scrubbedTowerName.replace(" ", "_")
    if DEBUG == True:
        arcpy.AddMessage("towerName: " + towerName)
        arcpy.AddMessage("scrubbedTowerName: " + scrubbedTowerName)
    tower = arcpy.MakeFeatureLayer_management(defPosFeatClass, scrubbedTowerName, descField + " = '" + str(towerName) +"'")

    # Do a Minimum Bounding Geometry (MBG) on the input observers
    observers_mbg = os.path.join(env.scratchWorkspace,"observers_mbg")
    deleteme.append(observers_mbg)
    arcpy.AddMessage("Finding observer's minimum bounding envelope ...")
    arcpy.MinimumBoundingGeometry_management(tower,observers_mbg,"RECTANGLE_BY_AREA") 

    # Now find the center of the (MBG)
    arcpy.AddMessage("Finding center of in features ...")
    mbgCenterPoint = os.path.join(env.scratchWorkspace,"mbgCenterPoint_towerrangefanlos")
    mbgExtent = arcpy.Describe(observers_mbg).extent
    mbgSR = arcpy.Describe(observers_mbg).spatialReference
    mbgCenterX = mbgExtent.XMin + (mbgExtent.XMax - mbgExtent.XMin)
    mbgCenterY = mbgExtent.YMin + (mbgExtent.YMax - mbgExtent.YMin)
    if DEBUG == True: 
        arcpy.AddMessage("mbgCenterX: " + str(mbgCenterX))
        arcpy.AddMessage("mbgCenterY: " + str(mbgCenterY))
    arcpy.CreateFeatureclass_management(os.path.dirname(mbgCenterPoint),os.path.basename        (mbgCenterPoint),"POINT","#","DISABLED","DISABLED",mbgSR)
    mbgShapeFieldName = arcpy.Describe(mbgCenterPoint).ShapeFieldName
    rows = arcpy.InsertCursor(mbgCenterPoint)
    feat = rows.newRow()
    feat.setValue(mbgShapeFieldName,arcpy.Point(mbgCenterX,mbgCenterY))
    rows.insertRow(feat)
    del rows
    deleteme.append(mbgCenterPoint)
       
    ###############################
    # Set the snap raster to the input surface
    ###############################
    if DEBUG == True: arcpy.AddMessage("Setting snap raster to: " + input_surface)
    env.snapRaster = input_surface

    currentOverwriteOutput = env.overwriteOutput
    env.overwriteOutput = True
    sr = arcpy.SpatialReference()
    sr.factoryCode = 4326
    sr.create()
    GCS_WGS_1984 = sr
    #GCS_WGS_1984 = arcpy.SpatialReference(r"WGS 1984")
    wbsr = arcpy.SpatialReference()
    wbsr.factoryCode = 3857
    wbsr.create()
    webMercator = wbsr
    #webMercator = arcpy.SpatialReference(r"WGS 1984 Web Mercator (Auxiliary Sphere)")
    env.overwriteOutput = True
    scratch = env.scratchWorkspace
    
    #Project doesn't like in_memory featureclasses, copy to scratch
    copyInFeatures = os.path.join(scratch,"copyInFeatures_towerrangefanlos")
    arcpy.CopyFeatures_management(tower,copyInFeatures)
    deleteme.append(copyInFeatures)
    
    prjInFeature = os.path.join(scratch,"prjInFeature_towerrangefanlos")
    srInputPoints = arcpy.Describe(copyInFeatures).spatialReference
    if DEBUG == True: arcpy.AddMessage("Projecting input points to Web Mercator ...")
    arcpy.Project_management(copyInFeatures,prjInFeature,webMercator)
    deleteme.append(prjInFeature)
    tempFans = os.path.join(env.scratchWorkspace,"tempFans_towerrangefanlos")
    
    #########################################################################
    # Create Range Fans
    #########################################################################
    # put bearing into 0 - 360 range
    geoBearing = math.fmod(geoBearing,360.0)
    if DEBUG == True: arcpy.AddMessage("geoBearing: " + str(geoBearing))
    arithmeticBearing = Geo2Arithmetic(geoBearing) # need to convert from geographic angles (zero north clockwise) to arithmetic (zero east counterclockwise)
    if DEBUG == True: arcpy.AddMessage("arithmeticBearing: " + str(arithmeticBearing))
    
    if traversal == 0.0:
        traversal = 1.0 # modify so there is at least 1 degree of angle.
        arcpy.AddWarning("Traversal is zero! Forcing traversal to 1.0 degrees.")
    leftAngle = arithmeticBearing + (traversal / 2.0) # get left angle (arithmetic)
    leftBearing = geoBearing - (traversal / 2.0) # get left bearing (geographic)
    if leftBearing < 0.0: leftBearing = 360.0 + leftBearing
            
    rightAngle = arithmeticBearing - (traversal / 2.0) # get right angle (arithmetic)
    rightBearing = geoBearing + (traversal / 2.0) # get right bearing (geographic)
    if rightBearing < 0.0: rightBearing = 360.0 + rightBearing
    
    if DEBUG == True: arcpy.AddMessage("arithemtic left/right: " + str(leftAngle) + "/" + str(rightAngle))
    if DEBUG == True: arcpy.AddMessage("geo left/right: " + str(leftBearing) + "/" + str(rightBearing))
    
    centerPoints = []
    arcpy.AddMessage("Getting centers ....")
    centerPoints.append([mbgCenterX,mbgCenterY])
    
    paths = []
    arcpy.AddMessage("Creating paths ...")
    for centerPoint in centerPoints:
        path = []
        centerPointX = centerPoint[0]
        centerPointY = centerPoint[1]
        path.append([centerPointX,centerPointY]) # add first point
        step = -1.0 # step in degrees
        rightAngleRelativeToLeft = leftAngle - traversal - 1
        #for d in xrange(int(leftAngle),int(rightAngleRelativeToLeft),int(step)): #UPDATE
        for d in range(int(leftAngle),int(rightAngleRelativeToLeft),int(step)):
            x = centerPointX + (maxRange * math.cos(math.radians(d)))
            y = centerPointY + (maxRange * math.sin(math.radians(d)))
            path.append([x,y])
            if DEBUG == True: arcpy.AddMessage("d,x,y: " + str(d) + "," + str(x) + "," + str(y))    
        path.append([centerPointX,centerPointY]) # add last point
        paths.append(path)
        if DEBUG == True: arcpy.AddMessage("Points in path: " + str(len(path)))
    if DEBUG == True: arcpy.AddMessage("paths: " + str(paths))
    
    arcpy.AddMessage("Creating target feature class ...")
    arcpy.CreateFeatureclass_management(os.path.dirname(tempFans),os.path.basename(tempFans),"Polygon","#","DISABLED","DISABLED",webMercator)
    arcpy.AddField_management(tempFans,"Range","DOUBLE","#","#","#","Range (meters)")
    arcpy.AddField_management(tempFans,"Bearing","DOUBLE","#","#","#","Bearing (degrees)")
    arcpy.AddField_management(tempFans,"Traversal","DOUBLE","#","#","#","Traversal (degrees)")
    arcpy.AddField_management(tempFans,"LeftAz","DOUBLE","#","#","#","Left Bearing (degrees)")
    arcpy.AddField_management(tempFans,"RightAz","DOUBLE","#","#","#","Right Bearing (degrees)")
    arcpy.AddField_management(tempFans,"Model","TEXT","#","#","#","Weapon Model")
    deleteme.append(tempFans)
    
    if DEBUG == True: arcpy.AddMessage("Building " + str(len(paths)) + " fans ...")
    cur = arcpy.InsertCursor(tempFans)
    for outPath in paths:
        lineArray = arcpy.Array()
        for vertex in outPath:
            pnt = arcpy.Point()
            pnt.X = vertex[0]
            pnt.Y = vertex[1]
            lineArray.add(pnt)
            del pnt
        feat = cur.newRow()
        feat.shape = lineArray
        feat.Range = maxRange
        feat.Bearing = geoBearing
        feat.Traversal = traversal
        feat.LeftAz = leftBearing
        feat.RightAz = rightBearing
        feat.Model = str(weaponModel)
        cur.insertRow(feat)
        del lineArray
        del feat
    del cur
                
    #########################################################################
    # Viewshed/Line of Sight
    #########################################################################
    #Begin calculating line of sight
    terrestrial_refractivity_coefficient = 0.13
    polygon_simplify = "SIMPLIFY"
    Temp_Feature_Class = mbgBuffer = os.path.join(env.scratchWorkspace,"tmpFeature")
    vizMods = {'OFFSETA':observation_height, 'RADIUS2':maxRange}
    if DEBUG == True: 
        arcpy.AddMessage("vizMods: " + str(vizMods))
        arcpy.AddMessage("observation_height: " + str(observation_height))
        arcpy.AddMessage("maxRange: " + str(maxRange))      
 
#DO MBG ON TOWER....... CUT POINT...
   
    # reset center of AZED using Lat/Lon of MBG center point
    # Project point to WGS 84
    arcpy.AddMessage("Recentering Azimuthal Equidistant to centroid ...")
    mbgCenterWGS84 = os.path.join(env.scratchWorkspace,"mbgCenterWGS84_towerrangefanlos")
    arcpy.Project_management(mbgCenterPoint,mbgCenterWGS84,GCS_WGS_1984)
    arcpy.AddXY_management(mbgCenterWGS84)
    pointx = 0.0
    pointy = 0.0
    shapeField = arcpy.Describe(mbgCenterWGS84).ShapeFieldName
    rows = arcpy.SearchCursor(mbgCenterWGS84)
    for row in rows:
        feat = row.getValue(shapeField)
        pnt = feat.getPart()
        pointx = pnt.X
        pointy = pnt.Y
    del row
    del rows
    # write new central meridian and latitude of origin...
    strAZED = 'PROJCS["World_Azimuthal_Equidistant",GEOGCS["GCS_WGS_1984",DATUM["D_WGS_1984",SPHEROID["WGS_1984",6378137.0,298.257223563]],PRIMEM["Greenwich",0.0],UNIT["Degree",0.0174532925199433]],PROJECTION["Azimuthal_Equidistant"],PARAMETER["False_Easting",0.0],PARAMETER["False_Northing",0.0],PARAMETER["Central_Meridian",' + str(pointx) + '],PARAMETER["Latitude_Of_Origin",' + str(pointy) + '],UNIT["Meter",1.0],AUTHORITY["ESRI",54032]]'
    if DEBUG == True: 
        arcpy.AddMessage("strAZED: " + strAZED)
        arcpy.AddMessage("pointx: " + str(pointx))
        arcpy.AddMessage("pointy: " + str(pointy))
    deleteme.append(mbgCenterWGS84)

    # Set the working extent only to the area in which the range fans will be generated
    mbgBuffer = os.path.join(env.scratchWorkspace,"mbgBuffer_towerrangefanlos")
    arcpy.Buffer_analysis(observers_mbg,mbgBuffer,maxRange)
    deleteme.append(mbgBuffer)
    mbgBufferPrj = os.path.join(env.scratchWorkspace,"mbgBufferPrj_towerrangefanlos")
    arcpy.Project_management(mbgBuffer,mbgBufferPrj,strAZED)
    deleteme.append(mbgBufferPrj)
    mbgBufferPrjExtent = arcpy.Describe(mbgBufferPrj).extent
    arcpy.AddMessage("Setting procesing extent to: " + str(mbgBufferPrjExtent))
    env.extent = mbgBufferPrjExtent

    # Project surface to the new AZED
    extract_prj = os.path.join(env.scratchWorkspace,"input_surface_prj_towerrangefanlos")
    arcpy.AddMessage("Projecting surface ...")
    arcpy.ProjectRaster_management(input_surface,extract_prj,strAZED)
    deleteme.append(extract_prj)
    
    #Add viewshed-utilized fields
    if DEBUG == True: arcpy.AddMessage("Adding OFFSETA field to: " + str(prjInFeature))
    arcpy.AddField_management(prjInFeature, "OFFSETA", "DOUBLE", "", "", "", "Observer Offset", "NULLABLE", "NON_REQUIRED", "")
    arcpy.CalculateField_management(prjInFeature, "OFFSETA", observation_height, "PYTHON", "")   
    if DEBUG == True: arcpy.AddMessage("Adding RADIUS2 field to: " + str(prjInFeature))
    arcpy.AddField_management(prjInFeature, "RADIUS2", "DOUBLE", "", "", "", "Farthest distance", "NULLABLE", "NON_REQUIRED", "")
    arcpy.CalculateField_management(prjInFeature, "RADIUS2", maxRange, "PYTHON", "")   
    
    # Project observers to the new AZED
    obs_prj = os.path.join(env.scratchWorkspace,"obs_prj_towerrangefanlos")
    arcpy.AddMessage("Projecting observers ...")
    #arcpy.Project_management(prjInFeature,obs_prj,strAZED)
    arcpy.Project_management(mbgCenterPoint,obs_prj,strAZED)
    deleteme.append(obs_prj)

    # Project the MBG buffer to AZED
    obs_buf = os.path.join(env.scratchWorkspace,"obs_buf_towerrangefanlos")
    arcpy.Project_management(mbgBufferPrj,obs_buf,strAZED)
    deleteme.append(obs_buf)
    
    # determine the proper z factor
    arcpy.AddMessage("Calculating Z Factor ...")
    z_factor = float(zfactor(extract_prj))
    arcpy.AddMessage("z_factor: " + str(z_factor))
    
    # Finally ... run Viewshed
    arcpy.AddMessage("Calculating Viewshed ...")    
    vshed = os.path.join(env.scratchWorkspace,"vshed_towerrangefanlos")
    deleteme.append(vshed)
    outVshed = sa.Viewshed(extract_prj,obs_prj,z_factor,"CURVED_EARTH",terrestrial_refractivity_coefficient)
    #outVshed = sa.Visibility(extract_prj,mbgCenterPoint,z_factor=z_factor,curvature_correction="CURVED_EARTH",refractivity_coefficient=terrestrial_refractivity_coefficient,observer_offset=observation_height)
    outVshed.save(vshed)

    # Raster To Polygon
    arcpy.AddMessage("Converting to polygons ...")
    ras_poly = os.path.join(env.scratchWorkspace,"ras_poly_towerrangefanlos")
    arcpy.RasterToPolygon_conversion(vshed,ras_poly,polygon_simplify)
    deleteme.append(ras_poly)   
    
    arcpy.AddMessage("Projecting Range Fans back to " + str(srInputPoints.name))
    tempFanFeature = os.path.join(env.scratchWorkspace,"tempRangeFan_towerrangefanlos")
    arcpy.Project_management(tempFans,outFeature,srInputPoints)
    arcpy.CopyFeatures_management(outFeature, tempFanFeature)
    arcpy.Project_management(tempFans,tempFanFeature,srInputPoints)
    deleteme.append(tempFanFeature)
   

    # Add and calculate the visibility field, this is used by the layer symbology
    arcpy.AddField_management(ras_poly, "visibility", "DOUBLE", "", "", "", "Observer Visibility", "NULLABLE", "NON_REQUIRED", "")
    arcpy.CalculateField_management(ras_poly, "visibility", "!gridcode!", "PYTHON", "")

    # Intersect the Range Fans with the Viewshed, being certain to keep all fields
    arcpy.Intersect_analysis([ras_poly,tempFanFeature],outFeature,"","","")
    
    # Add the layer to the map.  Need to go through these steps to ensure that labels are properly applied
    layerSymLocation = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'layers'))
    arcpy.AddMessage("LayerSymLocation: " + str(layerSymLocation))
    # Retrieve the layer file that specifies the symbology
    sourceLayer = arcpy.mapping.Layer(layerSymLocation + "\Radial Line Of Sight Output With Range Fans.lyr")
    sourceLayer.name= os.path.basename(outFeature)
    # Grab the MXD and Dataframe
    mxd = arcpy.mapping.MapDocument('CURRENT')
    df = arcpy.mapping.ListDataFrames(mxd)[0]
    # Create the new layer from the output data
    layerToAdd = arcpy.mapping.Layer(outFeature)
    layerToAdd.name = os.path.basename(outFeature)
    # Configure and turn on labeling - this has to be done manually because the layer file's labeling specs are ignored
    layerToAdd.showLabels = True
    if layerToAdd.supports("LABELCLASSES"):
        for lblclass in layerToAdd.labelClasses:
            lblclass.showClassLabels = True
            lblclass.expression = "\"Range: \" & [Range] & \" m\" & vbcrlf & \"Bearing: \" & [Bearing] & \" deg.\" & vbcrlf & \"Model: \" & [Model]"
    layerToAdd.showLabels = True
    arcpy.ApplySymbologyFromLayer_management(layerToAdd, sourceLayer)
    #    Add the layer
    arcpy.mapping.AddLayer(df, layerToAdd, "AUTO_ARRANGE")

#    df = arcpy.mapping.ListDataFrames(mxd)[0]   
#    updateLayer = arcpy.mapping.ListLayers(mxd, layerToAdd, df)[0]
#    if DEBUG == True: arcpy.AddMessage("df: " + str(df))
#    if DEBUG == True: arcpy.AddMessage("updateLayer: " + str(updateLayer))
#    arcpy.mapping.UpdateLayer(df, updateLayer, sourceLayer, False)

except arcpy.ExecuteError: 
    # Get the tool error messages 
    msgs = arcpy.GetMessages() 
    arcpy.AddError(msgs) 
    #print msgs #UPDATE
    print(msgs)

except:
    # Get the traceback object
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]

    # Concatenate information together concerning the error into a message string
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    msgs = "\nArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

    # Return python error messages for use in script tool or Python Window
    arcpy.AddError(pymsg)
    arcpy.AddError(msgs)

    # Print Python error messages for use in Python / Python Window
    #print pymsg + "\n" #UPDATE
    print(pymsg + "\n")
    #print msgs #UPDATE
    print(msgs)

finally:
    # cleanup intermediate datasets
    if DEBUG == True: arcpy.AddMessage("Removing intermediate datasets...")
    for i in deleteme:
        if DEBUG == True: 
            arcpy.AddMessage("Removing: " + str(i))
            arcpy.Delete_management(i)
    if DEBUG == True: arcpy.AddMessage("Done")
