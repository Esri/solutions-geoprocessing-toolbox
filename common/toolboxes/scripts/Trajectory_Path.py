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

# IMPORTS ==========================================
import os, sys, math, traceback
import arcpy
from arcpy import env


# CONSTANTS ========================================
prjWGS1984Path = arcpy.SpatialReference("WGS 1984")
prjWebMercator = arcpy.SpatialReference("WGS 1984 Web Mercator (auxiliary sphere)")

useSurface = True
debug = True


# ARGUMENTS & LOCALS ===============================
inputFeature = arcpy.GetParameterAsText(0)
initialVelocityMPS =  float(arcpy.GetParameterAsText(1)) #500.0 # meters/second
elevationAngleDegrees = float(arcpy.GetParameterAsText(2)) #45.0 # degrees (range from 0 to 90)
azimuthAngleDegrees = float(arcpy.GetParameterAsText(3)) #315.0 # degrees, arithmetic orientation(East == 0.0)
analysisType = arcpy.GetParameterAsText(4) #IDEAL
# Currently this tool is developed using IDEAL projectile conditions (no air drag, no wind deflection, etc.)
# future versions of this tool may include calculations for other conditions
inputSurface = arcpy.GetParameterAsText(5) #r"\\mattf\Trajectory\IrwinWebMercator.gdb\IrwinDTED_WebMerc"  #surface dataset
outFeature = arcpy.GetParameterAsText(6)

deleteme = [] # stuff to get rid of when we're done

def SurfaceRange(d):
    # distance from origin point
    h = -1 * math.pow(d,2) * (gravitationalConstant * math.pow(sec(elevationAngleRadians),2))/(2 * math.pow(initialVelocityMPS,2)) + (d * math.tan(elevationAngleRadians))
    return h

def TimeToRange(h):
    # time to current position from origin point
    t = (initialVelocityMPS * math.sin(elevationAngleRadians)/gravitationalConstant) + math.sqrt(math.pow(initialVelocityMPS,2) * math.pow(math.sin(elevationAngleDegrees),2) + (2 * gravitationalConstant * math.fabs(h)))/ gravitationalConstant
    return t

def sec(x):
    return 1/(math.cos(x))
    
def csc(x):
    return 1/(math.sin(x))

def Geo2Arithmetic(inAngle):
    inAngle = math.fmod(inAngle,360.0)
    #0 to 90
    if (inAngle >= 0.0 or inAngle <= 90.0):
        outAngle = math.fabs(inAngle - 90.0)
    
    # 90 to 360
    if (inAngle >= 90.0 or inAngle < 360.0):
        outAngle = 360.0 - (inAngle - 90.0)

    return float(outAngle)

def euclideanDistance2D(x1,x2,y1,y2):
    dist = math.sqrt(math.pow((x2 - x1),2) + math.pow((y2 - y1),2))
    return dist

def euclideanDistance3D(x1,x2,y1,y2,z1,z2):
    dist = math.sqrt(math.pow((x2 - x1),2) + math.pow((y2 - y1),2) + math.pow((z2 - z1),2))
    return dist

def calcZFactor(mid):
    import decimal
    decimal.getcontext().prec = 28
    decimal.getcontext().rounding = decimal.ROUND_UP
    a = decimal.Decimal("1.0")
    b = decimal.Decimal("111320.0")
    c = decimal.Decimal(str(math.cos(mid)))
    # here's the actual calculation
    zfactor = a/(b * c)
    # return the correct format
    zfactor = "%06f" % (zfactor.__abs__())
    return float(zfactor)


try:
    
    if debug == True:
        arcpy.AddMessage("initialVelocityMPS: " + str(initialVelocityMPS))
        arcpy.AddMessage("elevationAngleDegrees: " + str(elevationAngleDegrees))
        arcpy.AddMessage("azimuthAngleDegrees: " + str(azimuthAngleDegrees))
    
    env.overwriteOutput = True
    scratch = env.scratchWorkspace

    # angular inputs in radians
    azimuthAngleRadians = math.radians(float(Geo2Arithmetic(azimuthAngleDegrees)))
    elevationAngleRadians = math.radians(float(elevationAngleDegrees))
    
    # create output layer
    arcpy.CreateFeatureclass_management(os.path.dirname(outFeature),os.path.basename(outFeature),"POLYLINE","","ENABLED","ENABLED",prjWebMercator)
    arcpy.AddField_management(outFeature,"Bearing","DOUBLE","","","","Bearing from north (deg)")
    arcpy.AddField_management(outFeature,"ElevAngle","DOUBLE","","","","Elevation angle from surface (deg)")
    arcpy.AddField_management(outFeature,"InitV","DOUBLE","","","","Initial velocity (m/sec)")
    arcpy.AddField_management(outFeature,"MaxHeight","DOUBLE","","","","Maximum projectile height (m)")
    arcpy.AddField_management(outFeature,"Range","DOUBLE","","","","3D range (m)")
    arcpy.AddField_management(outFeature,"TimeImpact","DOUBLE","","","","Time to impact (sec)")
    

    # get projection of input points
    prjInputFeature = arcpy.Describe(inputFeature).spatialReference
    prjInputSurface = arcpy.Describe(inputSurface).spatialReference
    if debug == True:
        arcpy.AddMessage("prjInputFeatures: " + str(prjInputFeature.name))
        arcpy.AddMessage("prjInputSurface: " + str(prjInputSurface.name))
    
    # Interpolate Z values from surface
    # arcpy.AddSurfaceInformation_3d(inputFeature,inputSurface,"Z","LINEAR") # interpolate from surface
    
    # Extract Z values from surface
    extractPoints = os.path.join("in_memory","extractPoints")
    arcpy.sa.ExtractValuesToPoints(inputFeature,inputSurface,extractPoints,"NONE","VALUE_ONLY")
    arcpy.AddField_management(extractPoints,"Z","DOUBLE")
    arcpy.CalculateField_management(extractPoints,"Z","!RASTERVALU!","PYTHON_9.3")
    
    # make dictionary from observer XYs and project to Web Merc
    initialObservers = {}
    observersWebMerc = {}  
    #rows = arcpy.da.SearchCursor(inputFeature,["OID@","SHAPE@XY","Z"]) # use for interpolated points, not extracted
    rows = arcpy.da.SearchCursor(extractPoints,["OID@","SHAPE@XY","Z"])
    for row in rows:
        OID = row[0]
        pnt = row[1]
        Z = row[2]
        initialObservers[OID] = [pnt[0],pnt[1],Z]
        # project to Web Merc and add to separate dictionary
        #pnt2 = arcpy.Geometry("POINT",arcpy.Point(pnt[0],pnt[1],Z),arcpy.Describe(inputFeature).spatialReference,True) # user for interpolated points, not extracted
        pnt2 = arcpy.Geometry("POINT",arcpy.Point(pnt[0],pnt[1],Z),arcpy.Describe(extractPoints).spatialReference,True)
        pntWM = pnt2.projectAs(prjWebMercator)
        observersWebMerc[OID] = [pntWM.firstPoint.X,pntWM.firstPoint.Y,Z] 
    if debug == True:
        arcpy.AddMessage("Initial Observers: " + str(initialObservers))
        arcpy.AddMessage("Web Merc Observer: " + str(observersWebMerc))
    del rows
    
    # are we working in feet or meters?
    linearUnits = prjWebMercator.linearUnitName # for now do all work in Web Merc
    linearUnitsSurface = arcpy.Describe(inputSurface).spatialReference.linearUnitName
    gravitationalConstant = 9.80665 # meters/second^2
    
    step = 50 # interval step in meters
    if linearUnits == "Feet":
        gravitationalConstant = 32.17405 # ft/sec^2
        step = 328 # interval step in feet
    
    # start a cursor on the output path features.    
    addRows = arcpy.da.InsertCursor(outFeature,["SHAPE@","MaxHeight","Range","TimeImpact","Bearing","ElevAngle","InitV"])
    
    # go through each observer and build a trajectory path
    # TODO: check for analysis type. For first release this is under IDEAL conditions
    for obsOID in observersWebMerc.keys():
        if debug == True: arcpy.AddMessage("Starting observer OID: " + str(obsOID))
        path = []
        pathArray = arcpy.Array() # this is giong to be the array storing the points that become each path polyline
        coordTriple = observersWebMerc[obsOID]
        longitudeOfObserver = coordTriple[0]
        latitudeOfObserver = coordTriple[1]
        elevationOfObserver = coordTriple[2]
        
        # find the approximate 2D (flat) range
        rangeFlat = int((math.pow(initialVelocityMPS,2)* math.sin(2 * elevationAngleRadians))/gravitationalConstant)
        if debug == True: arcpy.AddMessage("Flat range: " + str(rangeFlat) + " " + str(linearUnits))
        # find maximum height
        maxHeight = (math.pow(initialVelocityMPS,2)* math.sin(elevationAngleRadians))/(2 * gravitationalConstant)
        if debug == True: arcpy.AddMessage("Maximum Height: " + str(maxHeight) + " " + str(linearUnits))

        # since we are using a surface assume we might be shooting downhill, so the flat range needs to be extended
        stepRange = int(rangeFlat * 2 )
    
        # set scope and initial values for these guys
        surfZ = 0.0
        h = 0.0
        t = 0.0
        tMax = 0.0
        x = 0.0
        y = 0.0
        z = 0.0
    
        # build the set of points in the trajectory path 
        iterations = stepRange / step # the number of points in the range we are going to build
        if stepRange <= 1000:
            step = 10
            iterations = stepRange / step
        if stepRange <= 100: # if the range is too short (ie. we are shooting uphill)
            step = 1 # make a new step
            iterations = stepRange / step # update iterations
            
        if debug == True:
            arcpy.AddMessage("stepRange: " + str(stepRange))
            arcpy.AddMessage("step: " + str(step))
            arcpy.AddMessage("iterations: " + str(iterations))
        
        if (stepRange > 0):
            if debug == True: arcpy.AddMessage("Normal range")
            for d in xrange(0,stepRange,step):
                h = SurfaceRange(d)
                if debug == True: arcpy.AddMessage("d,h: " + str(d) + "," + str(h))
                t = TimeToRange(h)
                if t > tMax: tMax = t
                x = longitudeOfObserver + (d * math.cos(azimuthAngleRadians))
                y = latitudeOfObserver + (d * math.sin(azimuthAngleRadians))
                z = elevationOfObserver + h
                

                result = arcpy.GetCellValue_management(inputSurface,str(x) + " " + str(y))
                if result.getOutput(0) == None or result.getOutput(0) == "NoData":
                    arcpy.AddWarning("Encountered NoData cell on surface.\nStopping trajectory for observer " + str(obsOID))
                    break
                surfElev = float(result.getOutput(0))
                
                if debug == True: arcpy.AddMessage(str([d,x,y,z,h,t,surfElev]))
                
                path.append([x,y,z,t])
                pathArray.append(arcpy.Point(x,y,z,t)) # add the point to the path array
               
                # compare if the path-point's Z is below the surface, if so stop adding points.
                if int(surfElev) > int(z):
                    break
                
               
            ###### Let's check the line and intersect it with our surface
            #####impactPoint = []
            #####impactPoints = os.path.join("in_memory","impactPoint")
            #####tempPath = os.path.join("in_memory","tempPath")
            #####arcpy.CopyFeatures_management(arcpy.Polyline(pathArray,prjWebMercator),tempPath)
            #####arcpy.Intersect3DLineWithSurface_3d(tempPath,inputSurface,r"in_memory\tempsplitline",impactPoints)
            ###### get the intersect point's coordinates (this is the point of impact on the surface)
            #####ipRows = arcpy.da.SearchCursor(impactPoints,["SHAPE@XY","SHAPE@Z"])
            #####for i in ipRows:
            #####    ipX,ipY = i[0]
            #####    ipZ = i[1]
            #####    impactPoint = [ipX,ipY,ipZ]
            #####del ipRows
            #####if debug == True: arcpy.AddMessage("impactPoint: " + str(impactPoint))
            ###### remove the very last point from the path array
            #####pathArray.remove(pathArray.count - 1)
            ###### add the impact point as the last point
            #####first = pathArray.getObject(0)
            #####if debug == True: arcpy.AddMessage([first.X,impactPoint[0],first.Y,impactPoint[1]])
            #####t = TimeToRange(euclideanDistance2D(first.X,impactPoint[0],first.Y,impactPoint[1]))
            #####pathArray.append(arcpy.Point(impactPoint[0],impactPoint[1],impactPoint[2],t))
            
            
            # calculate the length between the first point and the last point as our 3D Range
            first = pathArray.getObject(0)
            last = pathArray.getObject(pathArray.count - 1)
            dddRange = euclideanDistance3D(first.X,last.X,first.Y,last.Y,first.Z,last.Z)
            
        # special case:
        if (stepRange == 0): # if the range is zero e.g. projectile is shot straight up into the air (RUN!!!!)
            if debug == True: arcpy.AddMessage("Zero range")
            x = longitudeOfObserver
            y = latitudeOfObserver
            z = elevationOfObserver
            tHalf = TimeToRange(maxHeight)
            path.append([x,y,z,0.0])
            pathArray.append(arcpy.Point(x,y,z,0.0))
            path.append([x,y,z + maxHeight,tHalf])
            pathArray.append(arcpy.Point(x,y,z + maxHeight,tHalf))
            path.append([x,y,z,2 * tHalf])
            pathArray.append(arcpy.Point(x,y,z,2 * tHalf))
            dddRange = 0.0 
    
        # add the trajectory path and attributes to the output features
        if debug == True: arcpy.AddMessage("Adding row to output FC...")
        addRows.insertRow([arcpy.Polyline(pathArray,prjWebMercator,True,True),maxHeight,dddRange,tMax,azimuthAngleDegrees,elevationAngleDegrees,initialVelocityMPS])
        del pathArray

    del addRows
    
    # set output and check in extension
    if debug == True: arcpy.AddMessage("Setting output...")
    arcpy.SetParameter(6,outFeature)
    
    # cleaning up temporary datasets
    if debug == True: arcpy.AddMessage("Remove List: " + str(deleteme))
    for junk in deleteme:
       if debug == True:
        arcpy.AddMessage("removing: " + str(junk))
       if arcpy.Exists(junk):
        arcpy.Delete_management(junk)
       

except arcpy.ExecuteError: 
    # Get the tool error messages 
    msgs = arcpy.GetMessages() 
    arcpy.AddError(msgs) 
    print msgs

except:
    # Get the traceback object
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]

    # Concatenate information together concerning the error into a message string
    pymsg = "PYTHON ERRORS:\nTraceback info:\n" + tbinfo + "\nError Info:\n" + str(sys.exc_info()[1])
    msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages(2) + "\n"

    # Return python error messages for use in script tool or Python Window
    arcpy.AddError(pymsg)
    arcpy.AddError(msgs)

    # Print Python error messages for use in Python / Python Window
    print pymsg + "\n"
    print msgs
    
   

