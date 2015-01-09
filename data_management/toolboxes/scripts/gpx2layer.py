'''
Copyright Esri 2010-2014

Tool Name:  GPX to Features
Source Name: GPXtoFeatures.py
Version: ArcGIS 10.1
Author: ESRI

Required Arguments:
         Input GPX File: path to GPX file
         Output Feature Class: path to featureclass which will be created

Description:
         This tool takes a .GPX file (a common output from handheld GPS receivers). The tool will parse all points
         which participate as either a waypoint (WPT) or inside a track as a track point (TRKPT). The output feature class
         will create fields for the shape, time, and elevation and description.
'''

# Imports
try:
  from xml.etree import cElementTree as ElementTree
except:
  from xml.etree import ElementTree

import arcpy
import arcpy.da as da
import os
import numpy

gpxTypes = ['trk', 'rte', 'wpt']

def gpxToPoints(gpxfile, outFC):
    ''' This is called by the __main__ if run from a tool or at the command line
    '''

    # Set the tree to the input GPX file
    #
    tree = ElementTree.parse(gpxfile)

    global TOPOGRAFIX_NS
    TOPOGRAFIX_NS = ''
    TOPOGRAFIX_NS10 = './/{http://www.topografix.com/GPX/1/0}'
    TOPOGRAFIX_NS11 = './/{http://www.topografix.com/GPX/1/1}'

    badPt = 0

    # Inspection of the GPX file will yield and set the appropriate namespace. If 1.0 or 1.1
    # is not found, empty output will be generated
    #
    for ptType in gpxTypes:   
        if tree.findall(TOPOGRAFIX_NS10 + ptType):
            TOPOGRAFIX_NS = TOPOGRAFIX_NS10
        elif tree.findall(TOPOGRAFIX_NS11 + ptType):
            TOPOGRAFIX_NS = TOPOGRAFIX_NS11


    if TOPOGRAFIX_NS == '':
        arcpy.AddIDMessage("Warning", 1202)
            
    
    # Inspect the GPX file to get field lengths and how many points    
    arcpy.SetProgressorLabel("Scanning contents of GPX file")    
        
    howManyElements = 0
    
    # Initialize scanner with max values of 255
    scanner = gpxDetails(255, 255, 255, 255)
    for gType in gpxTypes:      
      for node in tree.findall(TOPOGRAFIX_NS + gType):                     
      
        if gType == 'trk': 
          #howManyElements +=1                 
          scanner.scan(node)
          for node in node.findall(TOPOGRAFIX_NS + 'trkseg'):
            for subnode in node.findall(TOPOGRAFIX_NS + 'trkpt'):
              howManyElements +=1                 
              scanner.scan(subnode)
            
        elif gType == 'rte':
          scanner.scan(node)
          for subnode in node.findall(TOPOGRAFIX_NS + 'rtept'):             
            scanner.scan(subnode)
            howManyElements +=1
            
        else: #wpt             
          scanner.scan(node)
          howManyElements +=1    
    

    # Create the output feature class in WGS84    
    arcpy.CreateFeatureclass_management(os.path.dirname(outFC), os.path.basename(outFC), 'POINT', '', 'DISABLED', 'ENABLED', 4326)


    # Join fields to the feature class, using ExtendTable    
    inarray = numpy.array([],
                      numpy.dtype([('intfield', numpy.int32),
                                   ('Name', '|S' + str(scanner.nameLen)),
                                   ('Descript', '|S' + str(scanner.descLen)),
                                   ('Type', '|S255'),
                                   ('Comment', '|S' + str(scanner.cmtLen)), 
                                   ('Symbol', '|S' + str(scanner.symLen)),
                                   ('DateTimeS', '|S'),
                                   ('Elevation', numpy.float),
                                   ]))
    
    arcpy.da.ExtendTable(outFC, "OID@", inarray, "intfield")


    rowsDA = da.InsertCursor(outFC, ['Name', 'Descript', 'Type', 'Comment', 'Symbol', 'DateTimeS', 'Elevation', 'SHAPE@X', 'SHAPE@Y', 'SHAPE@Z'])

    arcpy.SetProgressor('step', 'Converting GPX points...', 0, howManyElements, 1)
    # Loop over each point in the tree and put the information inside a new row
    #
    for index, trkPoint in enumerate(GeneratePointFromXML(tree)):
        if trkPoint.asPoint() is not None:
            try:              
              rowsDA.insertRow([trkPoint.name, trkPoint.desc, trkPoint.gpxtype, trkPoint.cmt,
                                trkPoint.sym, trkPoint.t, trkPoint.z, trkPoint.x, trkPoint.y, trkPoint.z])              
            except RuntimeError(e):
              arcpy.AddError(str(e))
       
        else:
            badPt +=1
            
        arcpy.SetProgressorPosition(index)

    if badPt > 0:
        arcpy.AddIDMessage("WARNING", 1201, badPt, index + 1)
        
    if tree:
        del tree
    if rowsDA:
        del rowsDA    
        
        
    # Try to create a DateTime field of Date-type for non-shapefile output
    #
    if not outFC.lower().endswith(".shp"):
      try:
        arcpy.ResetProgressor()
        arcpy.SetProgressorLabel("Calculating Datetime field")
        arcpy.ConvertTimeField_management(outFC, 'DateTimeS', 'yyyy-MM-ddTHH:mm:ssZ', "Date_Time")

      except:
        arcpy.AddIDMessage("WARNING", 1227)

        try:
          arcpy.DeleteField_management(outFC, "Date_Time")
        except:
          pass
        
        
class classGPXPoint(object):
    ''' Object to gather GPX information '''

    name = ''
    desc = ''
    cmt = ''
    sym = ''
    gpxtype = 'WPT'
    x = None
    y = None
    z = 0
    t = ''


    def __init__(self, node, gpxtype, name, desc, cmt, sym):
        self.name = name
        self.desc = desc
        self.cmt = cmt
        self.sym = sym
        self.gpxtype = gpxtype
        self.y = node.attrib.get('lat')
        self.x = node.attrib.get('lon')
        self.z = node.find(TOPOGRAFIX_NS + 'ele').text if node.find(TOPOGRAFIX_NS + 'ele') is not None else '0.0'
        self.t = node.find(TOPOGRAFIX_NS + 'time').text or '' if node.find(TOPOGRAFIX_NS + 'time') is not None else ''


    def asPoint(self):
        ''' Try to float X/Y. If conversion to a float fails, the X/Y is not valid and return NONE. '''

        try:
            self.x = float(self.x.replace(',','.'))
            self.y = float(self.y.replace(',','.')) 
            self.z = float(self.z.replace(',','.'))
            
            return self.x, self.y, self.z        

        except:
            return None
 
def getLength(node, t):
  i = 255
  try:
    if node.find(TOPOGRAFIX_NS + t).text:  
      i = len(node.find(TOPOGRAFIX_NS + t).text)
  except:
      pass
  return i  

class gpxDetails(object):    
  ''' Object to get max lengths for attributes '''
  
  def __init__(self, nameLen, descLen, cmtLen, symLen):
      self.nameLen = nameLen
      self.descLen = descLen
      self.cmtLen = cmtLen
      self.symLen = symLen 
      
  def scan(self, node):
    
    nameTest = getLength(node, 'name')
    descTest = getLength(node, 'desc')
    cmtTest = getLength(node, 'cmt')
    symTest = getLength(node, 'sym')

    if nameTest > self.nameLen: self.nameLen = nameTest
    if descTest > self.descLen: self.descLen = descTest
    if cmtTest > self.cmtLen: self.cmtLen = cmtTest
    if symTest > self.symLen: self.symLen = symTest
          

def GeneratePointFromXML(tree):
    ''' 1) Inspect the tree for either TRK or WPT
           TRK's have a sub node of TRKPT which are examined.
        2) Yield the information back to insertcursor from the classGPXPoint object.    '''
    name = ''
    desc = ''
    cmt = ''
    sym = ''

    def _getNameDesc(node, name, desc, cmt, sym):
        name = node.find(TOPOGRAFIX_NS + 'name').text or name if node.find(TOPOGRAFIX_NS + 'name') is not None else name
        desc = node.find(TOPOGRAFIX_NS + 'desc').text or desc if node.find(TOPOGRAFIX_NS + 'desc') is not None else desc
        cmt = node.find(TOPOGRAFIX_NS + 'cmt').text or cmt if node.find(TOPOGRAFIX_NS + 'cmt') is not None else cmt
        sym = node.find(TOPOGRAFIX_NS + 'sym').text or sym if node.find(TOPOGRAFIX_NS + 'sym') is not None else sym
        return name, desc, cmt, sym

    for node in tree.findall(TOPOGRAFIX_NS + 'trk'):
        name, desc, cmt, sym = _getNameDesc(node, name, desc, cmt, sym)
        for node in node.findall(TOPOGRAFIX_NS + 'trkpt'):
            name, desc, cmt, sym = _getNameDesc(node, name, desc, cmt, sym)
            yield (classGPXPoint(node, 'TRKPT', name, desc, cmt, sym))
         
    for node in tree.findall(TOPOGRAFIX_NS + 'rte'):
        name, desc, cmt, sym = _getNameDesc(node, name, desc, cmt, sym)
        for node in node.findall(TOPOGRAFIX_NS + 'rtept'):
            name, desc, cmt, sym = _getNameDesc(node, name, desc, cmt, sym)
            yield (classGPXPoint(node, 'RTEPT', name, desc, cmt, sym))

    for node in tree.findall(TOPOGRAFIX_NS + 'wpt'):
        name, desc, cmt, sym = _getNameDesc(node, name, desc, cmt, sym)
        yield classGPXPoint(node, 'WPT', name, desc, cmt, sym)


if __name__ == "__main__":
    ''' Gather tool inputs and pass them to gpxToPoints(file, outputFC) '''

    gpx = arcpy.GetParameterAsText(0)
    outFC = arcpy.GetParameterAsText(1)
    gpxToPoints(gpx, outFC)