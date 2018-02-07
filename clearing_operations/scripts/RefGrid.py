# coding: utf-8
'''
RefGrid.py
'''
import re
import os
import math
import arcpy

#self.inputArea = arcpy.GetParameterAsText(0)

GRID_FIELD_NAME = "Grid"
class ReferenceGrid(object):
  '''
  '''
  GRID_SIZE_LOOKUP = {'GRID_ZONE_DESIGNATOR':1000000,
                          '100000M_GRID':100000,
                          '10000M_GRID':10000,
                          '1000M_GRID':1000,
                          '100M_GRID':100,
                          '10M_GRID':10}
  DEBUG = False
  GRID_FIELD_NAME = "Grid"

  def __init__(self, input_area, grid_type, grid_square_size, large_grid_handling='ALLOW_LARGE_GRIDS'):
    '''
    Reference Grid Constructor
    '''
    self.inputArea = input_area
    self.gridType = grid_type
    self.gridSize = grid_square_size
    self.allowLargeGrids = False
    if large_grid_handling == 'ALLOW_LARGE_GRIDS':
      self.allowLargeGrids = True
    
    return
  
  def __del__(self):
    '''
    Destructor
    '''
    return

  def Build(self, out_features):
    '''
    '''

    def _createFC(out_feature_path, geometry_type, spatial_reference):
      '''
      '''
      feature_class = arcpy.CreateFeatureclass_management(os.path.dirname(out_feature_path),
                                                          os.path.basename(out_feature_path),
                                                          geometry_type,
                                                          "" ,
                                                          "" ,
                                                          "" ,
                                                          spatial_reference)  
      return feature_class

    def _buildHundredGrid(out_features, sq):
      '''
      '''
      features = _createFC(out_features, "POLYGON", sr_wgs_84)
      arcpy.AddField_management(features, GRID_FIELD_NAME,"text") 
      with arcpy.da.InsertCursor(features, ['SHAPE@',GRID_FIELD_NAME]) as cursor:
        for i in range(0,len(sq)):
          cursor.insertRow([sq[i]['clippedPolygon'],
                            sq[i][GRID_FIELD_NAME]])  
      return features

    def _largeGridWarning(area, value):
      return "Area ({0}) exceeds large grid value for {1}. Proceeding with grid construction.".format(area, value)
    
    def _largeGridError(area, value):
      return "Area ({0}) exceeds large grid value for {1}. Use a smaller Input Area or choose a larger Grid Size.".format(area, value)
      
    def checkPolarRegion(inputFeature):
      ''' checks if the input feature class overlaps with the polar regions'''
      sr = arcpy.SpatialReference(4326)
      
      # A list of features and coordinate pairs
      polarNorth = [[-180,84],[-180,90],[180,90],[180,84],[-180,84]]
      polarSouth = [[-180,-90],[-180,-80],[180,-80],[180,-90],[-180,-90]]
      
      northPoly = arcpy.Polygon(arcpy.Array([arcpy.Point(*coords) for coords in polarNorth]),sr)
      southPoly = arcpy.Polygon(arcpy.Array([arcpy.Point(*coords) for coords in polarSouth]),sr)
      
      outsideNorthPolar = northPoly.disjoint(inputFeature.projectAs(sr))
      outsideSouthPolar = southPoly.disjoint(inputFeature.projectAs(sr))
      
      if(not outsideNorthPolar or not outsideSouthPolar):
        arcpy.AddWarning("The GRG extent is within a polar region." + 
          " Cells that fall within the polar region will not be created.")

    out_features = out_features.value
    arcpy.env.overwriteOutput = True
    extent_area = arcpy.Describe(self.inputArea).extent.polygon.area
    if self.DEBUG:
      arcpy.AddMessage("extent_area: {}".format(extent_area))
      arcpy.AddMessage("self.gridSize: {}".format(self.gridSize))
      arcpy.AddMessage("self.GRID_SIZE_LOOKUP.keys(): {}".format(self.GRID_SIZE_LOOKUP.keys()))

    if self.allowLargeGrids is False:
      if   extent_area > 200000.0 and self.gridSize == '10M_GRID':
        arcpy.AddError(_largeGridError(extent_area, self.gridSize))
        return None
      elif extent_area > 20000000.0 and self.gridSize == '100M_GRID':
        arcpy.AddError(_largeGridError(extent_area, self.gridSize))
        return None
      elif extent_area > 2000000000.0 and self.gridSize == '1000M_GRID':
        arcpy.AddError(_largeGridError(extent_area, self.gridSize))
        return None
      elif extent_area > 200000000000.0 and self.gridSize == '10000M_GRID':
        arcpy.AddError(_largeGridError(extent_area, self.gridSize))
        return None
      else:
        pass # fall through condition, nothing to do here
    else:
      if   extent_area > 200000.0 and self.gridSize == '10M_GRID':
          arcpy.AddWarning(_largeGridWarning(extent_area, self.gridSize))
      elif extent_area > 20000000.0 and self.gridSize == '100M_GRID':
          arcpy.AddWarning(_largeGridWarning(extent_area, self.gridSize))
      elif extent_area > 2000000000.0 and self.gridSize == '1000M_GRID':
          arcpy.AddWarning(_largeGridWarning(extent_area, self.gridSize))
      elif extent_area > 200000000000.0 and self.gridSize == '10000M_GRID':
          arcpy.AddWarning(_largeGridWarning(extent_area, self.gridSize))
      else:
          arcpy.AddMessage("Creating Grid zones/latitude bands...")

    #sr_nad_27 = arcpy.SpatialReference(4267) #GCS_North_American_1927
    #sr_nad_83 = arcpy.SpatialReference(4269) #GCS_North_American_1983
    #sr_nad_83_harn = arcpy.SpatialReference(4152) #GCS_North_American_1983_HARN
    sr_wgs_84 = arcpy.SpatialReference(4326)
    

    AOIPoly = arcpy.Describe(self.inputArea).extent.polygon.projectAs(sr_wgs_84)
    
    checkPolarRegion(AOIPoly)

    #create an in memory feature class for the grid zones
    gridZones = _createFC(r"in_memory\GridZones", "POLYGON", sr_wgs_84)
    arcpy.AddField_management(gridZones, GRID_FIELD_NAME,"TEXT")
    arcpy.AddField_management(gridZones,'utmZone',"SHORT")
    arcpy.AddField_management(gridZones,'utmBand',"TEXT")
    with arcpy.da.InsertCursor(gridZones, ['SHAPE@', GRID_FIELD_NAME,'utmZone','utmBand']) as cursor:
      zonesDictionary = _ZonesDictionary()
      for i in zonesDictionary:
        cursor.insertRow([zonesDictionary[i]['polygon'],
                          zonesDictionary[i]['id'],
                          zonesDictionary[i]['utmZone'],
                          zonesDictionary[i]['latitudeZone']])

    #create a utm zone feature class by dissolving the grid zones by there utm zone number
    utmZones = arcpy.Dissolve_management(gridZones, r"in_memory\disslove",["utmZone"])

    #select the grid zones that intersect with the input extent
    arcpy.MakeFeatureLayer_management(gridZones, "gridZones_lyr")
    Selection = arcpy.SelectLayerByLocation_management("gridZones_lyr", "INTERSECT", self.inputArea)
    if self.gridSize == 'GRID_ZONE_DESIGNATOR':
      arcpy.CopyFeatures_management(Selection, out_features)
      arcpy.DeleteField_management(out_features,['utmZone','utmBand'])
      return out_features
    #else:
      #arcpy.CopyFeatures_management(Selection, r"in_memory\Selected")

    # create 100k squares for the input self.inputArea
    arcpy.AddMessage('Creating 100k grid squares...')
    sq = _processZonePolygons(Selection, AOIPoly)

    if self.gridSize == '100000M_GRID':
      return _buildHundredGrid(out_features, sq)
    else:
      sq100k = _buildHundredGrid(r"in_memory\sq100k", sq)

    # only if not 100K
    arcpy.AddMessage("Creating sub 100K grid squares...")
    testValue = self.GRID_SIZE_LOOKUP[self.gridSize]
    currentValue = 10000
    while currentValue >= testValue:
      polys = []
      for i in range(0,len(sq)):
        polys = polys + _handleGridSquares(sq[i], currentValue, AOIPoly)
      sq = []
      sq = sq + polys
      currentValue = currentValue / 10

    output = _createFC(out_features, "POLYGON", sr_wgs_84)
    arcpy.AddField_management(output,GRID_FIELD_NAME,"text") 
    with arcpy.da.InsertCursor(output, ['SHAPE@',GRID_FIELD_NAME]) as cursor:
      for i in range(0,len(polys)):
        cursor.insertRow([polys[i]['clippedPolygon'],
                          polys[i]['text']])
                          
    return output


def _NonPolarGridZone(args):
  # parse and set the UTM zone and latitude zone from the id
  # (i.e. "12S" would parse to ['12', 'S'])  
  r = re.compile("([0-9]+)([a-zA-Z]+)")
  m = r.match(args['id'])  
  id = args['id']
  utmZone = m.group(1)
  latitudeZone = m.group(2)
  
  feature_info = [[args['xmin'], args['ymin']],
                  [args['xmin'], args['ymax']],
                  [args['xmax'], args['ymax']],
                  [args['xmax'], args['ymin']],
                  [args['xmin'], args['ymin']]]
  
  polygon = arcpy.Polygon(arcpy.Array([arcpy.Point(*coords) for coords in feature_info]),arcpy.SpatialReference(4326))
  
  npgz = {"id": id,"utmZone": utmZone,"latitudeZone": latitudeZone,"polygon": polygon}
  
  return npgz


def _ZonesDictionary():
  '''
  The zonesDictionary object has 1197 unique keys (one for eqch MGRS grid zone).
  Rather than load it through a single, large json text file, we build it here programmatically, one time, on the client
  '''
  
  #Per MGRS definition, these are the valid grid zone letters
  # A,B,Y,Z reserved for north and south polar regions as UPS
  zoneLetters = ['C','D','E','F','G','H','J','K','L','M','N','P','Q','R','S','T','U','V','W','X']

  # A dictionary object containing all MGRS zones (excluding any zones that don't exist)
  # this is the object that will be returned (i.e. set as the _ZonesDictionary)
  zonesDictionary = {}

  def ltrZoneToExtent(zoneNum, zoneLtrIndex):
    '''
    Returns the NonPolarGridZone object for the zone.
    NOTE: This is only used during the initial creation of '_ZonesDictionary' object
    @param  {Number zoneNum The MGRS grid zone number
    @param  {Number zoneLtrIndex
    The index of the MGRS grid zone letter (w.r.t. the zoneLetters object)
    @return {module:mgrs-utils~NonPolarGridZone  The NonPolarGridZone object
    @private
    '''    
    zoneLtr = zoneLetters[zoneLtrIndex]
    zoneId = str(zoneNum) + zoneLtr

    #There are several unique MGRS zones which don't follow the standard convention,
    #they are defined here:
    if zoneId == "32X" or zoneId == "34X" or zoneId == "36X":
      #Per the MGRS definition, these zones don't exist
      return
    elif zoneId == "31V":
      #unique sized zone
      nonPolarGridZoneArgs = {"xmin": 0,"ymin": 56,"xmax": 3,"ymax": 64,"id": zoneId}
    elif zoneId == "32V":
      #unique sized zone
      nonPolarGridZoneArgs = {"xmin": 3,"ymin": 56,"xmax": 12,"ymax": 64,"id": zoneId}
    elif zoneId == "31X":
      #unique sized zone
      nonPolarGridZoneArgs = {"xmin": 0,"ymin": 72,"xmax": 9,"ymax": 84,"id": zoneId}
    elif zoneId == "33X":
      #unique sized zone
      nonPolarGridZoneArgs = {"xmin": 9,"ymin": 72,"xmax": 21,"ymax": 84,"id": zoneId}
    elif zoneId == "35X":
      #unique sized zone
      nonPolarGridZoneArgs = {"xmin": 21,"ymin": 72,"xmax": 33,"ymax": 84,"id": zoneId}
    elif zoneId == "37X":
      #unique sized zone
      nonPolarGridZoneArgs = {"xmin": 33,"ymin": 72,"xmax": 42,"ymax": 84,"id": zoneId}
    else:
      #These are the default zones that do follow the standard MGRS convention:
      #Compute the extent attributes of the zone
      xmin = (zoneNum - 1) * 6 - 180
      xmax = zoneNum * 6 - 180
      ymin = zoneLtrIndex * 8 + -80
      ymax = (zoneLtrIndex + 1) * 8  + -80

      #Fix special cases where the numbers need to be adjusted
      #exactly 180 or -180 causes problems, changes it to something close
      xmin = 179.99999999 if xmin == 180 else xmin
      xmin = -179.99999999 if xmin == -180 else xmin;
      xmax = 179.99999999 if xmax == 180 else xmax;
      xmax = -179.99999999 if xmax == -180 else xmax;
      if (ymax == 80):
        #the top row of MGRS grid zones is taller than most, in order to extent to N84°
        ymax  =  84

      nonPolarGridZoneArgs = {"xmin": xmin,"ymin": ymin,"xmax": xmax,"ymax": ymax,"id": zoneId}
    
    #return nonPolarGridZoneArgs
    return _NonPolarGridZone(nonPolarGridZoneArgs)
  
  '''
  Loop through all possible zone number/letter combinations,
  building the NonPolarGridZone object for each
  '''
  for zoneNum in range(1,61):
    for zoneLtr in range(0,len(zoneLetters)):
      nonPolarGridZone = ltrZoneToExtent(zoneNum, zoneLtr)
      if nonPolarGridZone:
        zonesDictionary[nonPolarGridZone["id"]] = nonPolarGridZone       
        
  return zonesDictionary

   
def _processZonePolygons(visibleGridZones, extent):
  '''
  Processes an array of visible grid zone and hands them off to the appropriate handler(s)
  '''   
  polys = []
  fields = ['SHAPE@', GRID_FIELD_NAME,'utmZone','utmBand']
  
  with arcpy.da.SearchCursor(visibleGridZones, fields) as cursor:
    for row in cursor:
      gridZoneExtent = row[0].extent    
      lowerLeftUtm = _LLtoUTM(gridZoneExtent.YMin, gridZoneExtent.XMin, row[2], row[3])
      lowerRightUtm = _LLtoUTM(gridZoneExtent.YMin, gridZoneExtent.XMax, row[2], row[3])
      upperRightUtm = _LLtoUTM(gridZoneExtent.YMax, gridZoneExtent.XMax, row[2], row[3])
      upperLeftUtm = _LLtoUTM(gridZoneExtent.YMax, gridZoneExtent.XMin, row[2], row[3])
      
      # using the UTM coordinates, find the min/max values
      # (index 0 of a UTM point is easting, 1 is northing)  
      
      minEasting = min(lowerLeftUtm[0],lowerRightUtm[0], upperRightUtm[0], upperLeftUtm[0])
      maxEasting = max(lowerLeftUtm[0],lowerRightUtm[0], upperRightUtm[0], upperLeftUtm[0])
      minNorthing = min(lowerLeftUtm[1],lowerRightUtm[1], upperRightUtm[1], upperLeftUtm[1]) 
      maxNorthing = max(lowerLeftUtm[1],lowerRightUtm[1], upperRightUtm[1], upperLeftUtm[1])
      
      handlerArgs = {"minE": minEasting,
                      "maxE": maxEasting,
                      "minN": minNorthing,
                      "maxN": maxNorthing,
                      "utmZone": row[2],
                      "latitudeZone": row[3],
                      "polygon": row[0]}                     
      
      polys = polys + _handle100kGrids(handlerArgs, extent)
  return polys


def _handle100kGrids(args, AOI):
  '''
  Creates 100K meter grids
  '''
  zonePolygon = args['polygon']
  utmZone = args['utmZone']
  latitudeZone = args['latitudeZone']
  minE = args['minE']
  maxE = args['maxE']
  minN = args['minN']
  maxN = args['maxN']
  poly100k = [];

  # Loop through northings, starting at the increment just south of minN
  # go through each increment of 100K meters, until maxN is reached
  for n in range(int(math.floor(minN / 100000) * 100000), int(math.ceil(maxN / 100000) * 100000), 100000):
    # Loop through eastings, starting at the increment just west of minE
    # go through each increment of 100K meters, until maxE is reached
    for e in range(int(math.floor(minE / 100000) * 100000), int(math.ceil(maxE / 100000) * 100000), 100000):
      # For each 100k increment of n & e, build a 100k by 100k grid polygon,
      # used for labeling and border graphics

      # find the label of the 100K grid
      text = "{0}{1}{2}".format(utmZone,latitudeZone, _findGridLetters(utmZone, 10000000 + (n + 50000) if (n + 50000) < 0 else  n + 50000, e + 50000))
      
      # Build the 100k grid boundary
      ring = []
      
      # start at the bottom left corner, and work north to
      # the top left corner (in 25k m increments)
      # this is a faster way of densifying the line, since it
      # will appear to be curved on the map
      
      for i in range(n, n + 100000, 25000):
        pt = _UTMtoLL(i, e, utmZone)
        if i == n:
          BL = arcpy.PointGeometry(arcpy.Point(pt['lon'], pt['lat']),arcpy.SpatialReference(4326))
        ring.append([pt['lon'], pt['lat']])
      
      
      # continue adding points to the polygon, working from the
      # top left to top right corner 
      
      for i in range(e, e + 100000, 25000):
        pt = _UTMtoLL(n + 100000, i, utmZone)
        ring.append([pt['lon'], pt['lat']])

      # continue adding points to the polygon, working from the
      # top right to bottom right corner
      
      for i in range(n + 100000, n , -25000):
        pt = _UTMtoLL(i, e + 100000, utmZone);
        ring.append([pt['lon'], pt['lat']]);
      
      BR = arcpy.PointGeometry(arcpy.Point(pt['lon'], pt['lat']),arcpy.SpatialReference(4326))      
      # continue adding points to the polygon, working from
      # the bottom right to the bottom left corner (to close the polygon)
      
      for i in range(e + 100000, e, -25000):
        pt = _UTMtoLL(n, i, utmZone)
        ring.append([pt['lon'], pt['lat']])

      # create the polygon, from the ring created above
      polygon = arcpy.Polygon(arcpy.Array([arcpy.Point(*coords) for coords in ring]),arcpy.SpatialReference(4326))
      
      # we need to rotate the drawn extent to match the angle of the grid (so that we can square the grid off)
      angle = BL.angleAndDistanceTo(BR)
      #arcpy.AddMessage(angle)  

      # now that the 100k grid polygon exists, clip it by the grid zone polygon
      clippedPolygon = polygon.intersect(zonePolygon,4)      
                
      # after being clipped above, they may no longer exist
      # (i.e. they were not within the bounds of the zone)
      # if this is the case, skip the rest and move on to the next increment of n or e
      if not clippedPolygon:
        continue
        
      # now check the clipped polygon touches the AOI drawn
      if not AOI.disjoint(polygon):
        gridPolygon = {"clippedPolygon": clippedPolygon,
                          "unclippedPolygon": polygon,
                          "xmin": e,
                          "ymin": n,
                          "xmax": (e + 100000),
                          "ymax": (n + 100000),
                          "utmZone": utmZone,
                          "latitudeZone": latitudeZone,
                          GRID_FIELD_NAME: text}
          
        poly100k.append(gridPolygon)

  return poly100k


def _handleGridSquares(poly, interval, AOI):
  '''
  This method is similar in nature to the 'handle100kGrids' method,
  Thus, much of this code is similar to the 'handle100kGrids' method.
  '''
  clippedPoly = poly['clippedPolygon']
  latitudeZone = poly['latitudeZone']
  utmZone = poly['utmZone']
  GZD = poly[GRID_FIELD_NAME]
  minE = poly['xmin']
  maxE = poly['xmax']
  minN = poly['ymin']
  maxN = poly['ymax']    
  polyOut = []
  
  for n in range(int(math.floor(minN / interval) * interval), int(maxN), int(interval)):    
    for e in range(int(math.floor(minE / interval) * interval), int(maxE), int(interval)):  
      ring = []
      
      ptBL = _UTMtoLL(n, e, utmZone)
      ring.append([ptBL['lon'], ptBL['lat']])
      ptTL = _UTMtoLL(n + interval, e, utmZone)
      ring.append([ptTL['lon'], ptTL['lat']])
      ptTR = _UTMtoLL(n + interval, e + interval, utmZone)
      ring.append([ptTR['lon'], ptTR['lat']])
      ptBR = _UTMtoLL(n, e + interval, utmZone)
      ring.append([ptBR['lon'], ptBR['lat']])
      # close off poly
      ring.append([ptBL['lon'], ptBL['lat']])
            
      polygon = arcpy.Polygon(arcpy.Array([arcpy.Point(*coords) for coords in ring]),arcpy.SpatialReference(4326))
            
      clippedPolygon = polygon.intersect(clippedPoly,4)      
      
      if not clippedPolygon:
        continue      
            
      if not AOI.disjoint(polygon):
        text = "{0}{1}".format(GZD,_padZero(e % 100000 / interval,  5 - 
          math.log10(interval)) + _padZero(((10000000 + n) if minN < 0 else n) % 100000 / interval, 5 - 
          math.log10(interval)))        
              
        gridPolygon = {"clippedPolygon": clippedPolygon,
          "unclippedPolygon": polygon,
          "clippedPolygon": clippedPolygon,
          "xmin": e,
          "ymin": n,
          "xmax": e + interval,
          "ymax": n + interval,
          "x": _padZero(e % 100000 / interval,  5 - math.log10(interval)),
          "y": _padZero(((10000000 + n) if minN < 0 else n) % 100000 / interval,5 - math.log10(interval)),
          "utmZone": utmZone,
          "latitudeZone": latitudeZone,
          GRID_FIELD_NAME: GZD,
          "text": text}
          
        polyOut.append(gridPolygon)

      
  return polyOut
    
  
def _LLtoUTM (lat, lon, zoneNumber, zoneBand):
  '''
  Converts lat/lon to UTM coords
  Output is in the input array utmcoords
  utmcoords[0] = easting
  utmcoords[1] = northing (NEGATIVE value in southern hemisphere)
  utmcoords[2] = zone
  '''
  k0 = 0.9996 #scale factor of central meridian
  #WGS84
  er = 6378137.0
  e2 = 0.006694379990
  #NAD 83
  #   er = 6378137;
  #   e2 = 0.00669438002290079
  e2ps = e2 / (1 - e2)
  
  lonTemp = (lon + 180) - math.floor((lon + 180) / 360) * 360 - 180;
  latRad = lat * math.pi / 180
  lonRad = lonTemp * math.pi / 180
  
  lonOrigin = (zoneNumber - 1) * 6 - 180 + 3 # +3 puts origin in middle of zone
  lonOriginRad = lonOrigin * math.pi / 180
  
  #compute the UTM Zone from the latitude and longitude
  UTMZone = str(zoneNumber) + "" + zoneBand + " "
  N = er / math.sqrt(1 - e2 * math.sin(latRad) * math.sin(latRad))
  T = math.tan(latRad) * math.tan(latRad)
  C = e2ps * math.cos(latRad) * math.cos(latRad)
  A = math.cos(latRad) * (lonRad - lonOriginRad)
  M = er * ((1 - e2 / 4 - 3 * (e2 * e2) / 64 - 5 * (e2 * e2 * e2) / 256) *
    latRad - (3 * e2 / 8 + 3 * e2 * e2 / 32 + 45 * e2 * e2 * e2 / 1024) *
    math.sin(2 * latRad) + (15 * e2 * e2 / 256 + 45 * e2 * e2 * e2 / 1024) *
    math.sin(4 * latRad) - (35 * e2 * e2 * e2 / 3072) * math.sin(6 * latRad))
  UTMEasting = (k0 * N * (A + (1 - T + C) * (A * A * A) / 6 +
    (5 - 18 * T + T * T + 72 * C - 58 * e2ps) * (A * A * A * A * A) / 120) + 500000.0)
  UTMNorthing = (k0 * (M + N * math.tan(latRad) * ((A * A) / 2 +
    (5 - T + 9 * C + 4 * C * C) * (A * A * A * A) / 24 + (61 - 58 * T +
      T * T + 600 * C - 330 * e2ps) * (A * A * A * A * A * A) / 720)))
  UTMcoordinates = UTMZone + " " + str(round(UTMEasting))
  if UTMNorthing < 0:
    UTMcoordinates = UTMcoordinates + "mE " + str(round(10000000 + UTMNorthing)) + "mN"
  else:
    UTMcoordinates = UTMcoordinates + "mE " + str(round(UTMNorthing)) + "mN"
  
  return [UTMEasting, UTMNorthing, zoneNumber];


def _UTMtoLL(UTMNorthing, UTMEasting, UTMZoneNumber):
  '''
  convert UTM coords to decimal degrees
  Expected Input args:
  UTMNorthing   : northing-m (numeric), eg. 432001.8
  southern hemisphere NEGATIVE from equator ('real' value - 10,000,000)
  UTMEasting    : easting-m  (numeric), eg. 4000000.0
  UTMZoneNumber : 6-deg longitudinal zone (numeric), eg. 18
  '''
  k0 = 0.9996
  # WGS 84
  er = 6378137.0
  e2 = 0.006694379990
  # NAD 83:
  #   er = 6378137;
  #   e2 = 0.00669438002290079
  
  e2ps = e2 / (1 - e2)
  E1 = (1 - math.sqrt(1 - e2)) / (1 + math.sqrt(1 - e2))
  #remove 500,000 meter offset for longitude
  xUTM = float(UTMEasting) - 500000.0
  yUTM = float(UTMNorthing)
  zoneNumber = int(UTMZoneNumber)
  #origin longitude for the zone (+3 puts origin in zone center)
  lonOrigin = (zoneNumber - 1) * 6 - 180 + 3
  # M is the true distance along the central meridian from the Equator to phi
  # (latitude)
  M = yUTM / k0
  mu = M / (er * (1 - e2 / 4 - 3 * e2 * e2 / 64 - 5 * e2 * e2 * e2 / 256))
  #phi1 is the "footprint latitude" or the latitude at the central meridian which
  #has the same y coordinate as that of the point (phi (lat), lambda (lon) ).
  phi1Rad = mu + (3 * E1 / 2 - 27 * E1 * E1 * E1 / 32) * math.sin(2 * mu) + (21 * E1 * E1 / 16 -
    55 * E1 * E1 * E1 * E1 / 32) * math.sin(4 * mu) + (151 * E1 * E1 * E1 / 96) * math.sin(6 * mu)
  phi1 = phi1Rad * 180.0 / math.pi
  #Terms used in the conversion equations
  N1 = er / math.sqrt(1 - e2 * math.sin(phi1Rad) * math.sin(phi1Rad))
  T1 = math.tan(phi1Rad) * math.tan(phi1Rad)
  C1 = e2ps * math.cos(phi1Rad) * math.cos(phi1Rad)
  R1 = er * (1 - e2) / math.pow(1 - e2 * math.sin(phi1Rad) * math.sin(phi1Rad), 1.5)
  D = xUTM / (N1 * k0)
  #Calculate latitude, in decimal degrees
  lat = phi1Rad - (N1 * math.tan(phi1Rad) / R1) * (D * D / 2 -
    (5 + 3 * T1 + 10 * C1 - 4 * C1 * C1 - 9 * e2ps) *
    D * D * D * D / 24 + (61 + 90 *
    T1 + 298 * C1 + 45 * T1 * T1 - 252 * e2ps - 3 * C1 * C1) * D * D * D * D * D * D / 720)
  lat = lat * 180.0 / math.pi
  #Calculate longitude, in decimal degrees
  lon = (D - (1 + 2 * T1 + C1) * D * D * D / 6 + (5 - 2 * C1 + 28 * T1 -
    3 * C1 * C1 + 8 * e2ps + 24 * T1 * T1) * D * D * D * D * D / 120) / math.cos(phi1Rad)
  lon = lonOrigin + lon * 180.0 / math.pi
  ret = {}
  ret['lat'] = lat
  ret['lon'] = lon
  return ret
     

def _findGridLetters (zoneNum, northing, easting):
  '''
  Retrieve the square identification for a given coordinate pair & zone
  See "lettersHelper" function documentation for more details.
  '''
  zoneNum = int(zoneNum)
  northing = float(northing)
  easting = float(easting)
  row = 1
  #northing coordinate to single-meter precision
  north_1m = round(northing)
  # Get the row position for the square identifier that contains the point
  while north_1m >= 100000:
    north_1m = north_1m - 100000
    row = row + 1
  # cycle repeats (wraps) after 20 rows
  row = row % 20
  col = 0
  # easting coordinate to single-meter precision
  east_1m = round(easting)
  # Get the column position for the square identifier that contains the point
  while east_1m >= 100000:
    east_1m = east_1m - 100000
    col = col + 1
  #cycle repeats (wraps) after 8 columns
  col = col % 8
  
  return _lettersHelper(_findSet(zoneNum), row, col);


def _lettersHelper(set, row, col):
  '''
  Retrieve the Square Identification (two-character letter code), for the
  given row, column and set identifier
  '''
  # handle case of last row
  
  if row == 0:
    row = 20 - 1
  else:
    row = row - 1
  # handle case of last column
  if col == 0:
    col = 8 - 1
  else:
    col = col - 1
  
  if set == 1:
    l1 = "ABCDEFGH" # column ids
    l2 = "ABCDEFGHJKLMNPQRSTUV" # row ids
  elif set == 2:
    l1 = "JKLMNPQR"
    l2 = "FGHJKLMNPQRSTUVABCDE"
  elif set == 3:
    l1 = "STUVWXYZ"
    l2 = "ABCDEFGHJKLMNPQRSTUV"
  elif set == 4:
    l1 = "ABCDEFGH"
    l2 = "FGHJKLMNPQRSTUVABCDE"
  elif set == 5:
    l1 = "JKLMNPQR"
    l2 = "ABCDEFGHJKLMNPQRSTUV"
  else:
    l1 = "STUVWXYZ"
    l2 = "FGHJKLMNPQRSTUVABCDE"
  
  return l1[col] + l2[row]


def _findSet(zoneNum):
  '''
  There are six unique sets, corresponding to individual grid numbers in
  sets 1-6, 7-12, 13-18, etc. Set 1 is the same as sets 7, 13, ..;
  Set 2 is the same as sets 8, 14, ..
  '''
  zoneNum = int(zoneNum)
  zoneNum = zoneNum % 6
  if zoneNum == 0:
    return 6
  elif zoneNum == 1:
    return 1
  elif zoneNum == 2:
    return 2
  elif zoneNum == 3:
    return 3
  elif zoneNum == 4:
    return 4
  elif zoneNum == 5:
    return 5
  else:
    return -1


def _padZero(number, width):
  number = str(int(number))
  while len(number) < width:
    number = "0" + number
  return number


def _testing():
    return


# MAIN =============================================
if __name__ == "__main__":
    _testing()
