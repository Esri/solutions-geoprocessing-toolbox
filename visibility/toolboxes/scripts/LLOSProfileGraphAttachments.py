
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

#
# LLOSProfileGraphAttachments.py
#
# Takes a LLOS output FC and adds a profile graph as an attachment to each line

import os, sys, traceback
import pylab
import arcpy

inputFeatures = arcpy.GetParameterAsText(0)

debug = False
deleteme = []
scratchFolder = arcpy.env.scratchFolder
scratchGDB = arcpy.env.scratchGDB
#pylab.use('AGG')

try:
    rawLOS = {} 
    # Current: {<SourceOID> : [<TarIsVis>, [<observerD=0.0>,<observerZ>],
    #                                      [<targetD>,<targetZ>],
    #                                      [<segmentList>]]]}
    #
    #             where
    #           [<segment>] is [<visibilityCode>,[d0,...,dN],[z0,...,zN]]
        
    # Unique sight lines
    sightLineIDs = []
    rows = arcpy.da.SearchCursor(inputFeatures,["SourceOID","OID@"])
    for row in rows:
        thisID = row[0]
        if thisID not in sightLineIDs:
            sightLineIDs.append(thisID)
    del rows
    if debug == True: arcpy.AddMessage("sightLineIDs list: " + str(sightLineIDs))
    arcpy.AddMessage("Found " + str(len(sightLineIDs)) + " unique sight line IDs ...")
    
    arcpy.AddField_management(inputFeatures,"pngname","TEXT")
    expression = '"profile" + str(!SourceOID!)'
    arcpy.CalculateField_management(inputFeatures,"pngname",expression, "PYTHON")
    
    # get visible and non-visible lines for each LLOS
    for currentID in sightLineIDs:
        whereclause = (""""SourceOID" = %s""" % currentID)
        tarIsViz = None
        rows = arcpy.da.SearchCursor(inputFeatures,["OID@","SHAPE@", "SourceOID", "TarIsVis","VisCode","ObsZ","TgtZ","OID_OBSERV","OID_TARGET"],whereclause)
        startX = None
        startY = None
        tgtD = 0.0
        line = 0
        segmentList = []
        for row in rows:
            
            oid = row[0]
            geometry = row[1]
            sourceOID = row[2]
            targetIsViz = row[3]
            visibilityCode = row[4]
            obsD = 0.0
            obsZ = row[5]
            tgtZ = row[6]
            obsID = row[7]
            tgtID = row[8]
            
            partNum = 0
            point = 0
            partCount = geometry.partCount
            if debug == True: arcpy.AddMessage("OID: " + str(oid))
            # go through parts in the line
            
            for part in geometry:
                if debug == True: arcpy.AddMessage("Line: " + str(line) + " Part: " + str(partNum) + " PointCount: " + str(len(part)))
                segment = []
                partD = []
                partZ = []
                for pnt in part:
                    if (line == 0) and (partNum == 0) and (point == 0): # if it is the very first point in the LLOS
                        startX = pnt.X
                        startY = pnt.Y
                        if debug == True: arcpy.AddMessage("startX,startY: " + str(startX) + "," + str(startY))
                        distFromStart = 0
                        partD.append(0.0)
                        partZ.append(pnt.Z)

                    else: # for all other points in the LLOS
                        distFromStart = math.sqrt((pnt.X - startX)**2 + (pnt.Y - startY)**2)
                        if distFromStart > tgtD:
                            tgtD = distFromStart
                        partD.append(distFromStart)
                        partZ.append(pnt.Z)
                    point += 1
                    if debug == True: arcpy.AddMessage("Adding parts to segment ...")
                    segment = [visibilityCode,partD,partZ]
                    #if debug == True: arcpy.AddMessage("\nsegment: " + str(segment) + "\n")
                partNum += 1
                if debug == True: arcpy.AddMessage("Adding segment to segment list ...")
                segmentList.append(segment)
            line += 1
        del rows
        rawLOS[currentID] = [targetIsViz,[obsD,obsZ,obsID],[tgtD,tgtZ,tgtID],segmentList]
        
    if debug == True: arcpy.AddMessage("rawLOS: " + str(rawLOS))
    
    # build a graph for each LLOS
    graphLocationDict = {}
    arcpy.AddMessage("Building graphs for lines ...")
    #for llosID in rawLOS.keys(): #UPDATE
    for llosID in list(rawLOS.keys()):
            
            graphInputList = rawLOS[llosID] # get the values for the current llos
    # Current: {<SourceOID> : [<TarIsVis>, [<observerD=0.0>,<observerZ>],
    #                                      [<segmentList0>,...,<segmentListN>]]}
            
            targetVisibility = graphInputList[0]
            observer = graphInputList[1]
            obsD = observer[0]
            obsZ = observer[1]
            obsID = observer[2]
            target = graphInputList[2]
            tgtD = target[0]
            tgtZ = target[1]
            tgtID = target[2]
            segmentList = graphInputList[3]
            arcpy.AddMessage("Building graph from observer " + str(obsID) + " to target " + str(tgtID) + " ..." )
            # plot the line of sight
            pylab.plot([obsD,tgtD],[obsZ,tgtZ],'k--',linewidth=1)
            
            # plot the visible profile
            for segment in segmentList:
                if segment[0] == 1 and len(segment[1]) != 0: # for visible segments - plot in green
                    pylab.plot(segment[1],segment[2],'g',linewidth=1)
                if segment[0] == 2 and len(segment[1]) != 0: # for non-visible segments - plot in red
                    pylab.plot(segment[1],segment[2],'r',linewidth=1)
                
            # titles & labels
            if (targetVisibility == 1):
                pylab.title("Target " + str(tgtID) + " is VISIBLE to observer " + str(obsID))
            else:
                pylab.title("Target " + str(tgtID) + " is NOT VISIBLE to observer " + str(obsID))
                
            pylab.ylabel("Elevation above sea level")
            pylab.xlabel("Distance to target")
            pylab.grid(True)
            
            # save the graph to a PNG file in the scratch folder
            graphPath = os.path.join(scratchFolder,r"profile" + str(llosID) + r".png")
            if debug == True: arcpy.AddMessage("graphPath: " + str(graphPath))
            pylab.savefig(graphPath, dpi=900)
            pylab.cla() # clear the graph???
            
            graphLocationDict[llosID] = graphPath
            deleteme.append(graphPath)
        
    # TODO: start an update cursor
    arcpy.AddMessage("Enabling attachments ...")
    arcpy.EnableAttachments_management(inputFeatures)
    
    matchTable = os.path.join(scratchGDB,"matchTable")
    deleteme.append(matchTable)
    arcpy.AddMessage("Building match table ...")
    arcpy.GenerateAttachmentMatchTable_management(inputFeatures,scratchFolder,matchTable,"pngname","*.png","ABSOLUTE")
    
    arcpy.AddMessage("Attaching profile graphs to sightlines ...")
    inOIDField = arcpy.Describe(inputFeatures).OIDFieldName
    arcpy.AddAttachments_management(inputFeatures,inOIDField,matchTable,"MatchID","Filename")
    
        
    # cleanup
    arcpy.AddMessage("Removing scratch data ...")
    for ds in deleteme:
        if arcpy.Exists(ds):
            arcpy.Delete_management(ds)
            if debug == True: arcpy.AddMessage(str(ds))
            
            
    # output
    arcpy.SetParameter(1,inputFeatures)


except arcpy.ExecuteError:
    error = True
    # Get the tool error messages 
    msgs = arcpy.GetMessages() 
    arcpy.AddError(msgs) 
    #print msgs #UPDATE
    print(msgs)

except:
    # Get the traceback object
    error = True
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
    