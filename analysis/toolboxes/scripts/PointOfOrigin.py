
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
# ---------------------------------------------------------------------------
# PointOfOrigin.py
# Created on: 09-16-2013
# Created by: Michael Reynolds
# Description: Triangulates the potential area for the point of origin of enemy
#   indirect fire given three or more known impact points.
# ---------------------------------------------------------------------------

# ====================== HISTORY ===========================================
# 8/4/2014 mfunk: Updates to function in Desktop 10.3 and Pro 11.0, tagged with #UPDATE
#
# ======================Import arcpy module=================================
import os, sys, traceback, math, decimal
import arcpy
from arcpy import env
from arcpy import sa


# ======================ARGUMENTS & LOCALS ===============================
inFeature = arcpy.GetParameterAsText(0)
weaponTable = arcpy.GetParameterAsText(1)
modelField = arcpy.GetParameterAsText(2)
minRangeField = arcpy.GetParameterAsText(4)
maxRangeField = arcpy.GetParameterAsText(5)
models = arcpy.GetParameterAsText(3).split(';')
outWorkspace = arcpy.GetParameterAsText(6)
pooOutPrefix = arcpy.GetParameterAsText(7)
impactOutPrefix = arcpy.GetParameterAsText(8)
impactBufferOutPrefix = arcpy.GetParameterAsText(9)


delete_me = []
DEBUG = True

try:
    
    # For the model and all outputs remove special characters and replace spaces with underscores    
    scrubbedPooOutPrefix = ''.join(e for e in pooOutPrefix if (e.isalnum() or e == " " or e == "_"))
    scrubbedPooOutPrefix = scrubbedPooOutPrefix.replace(" ", "_")
    scrubbedImpactOutPrefix = ''.join(e for e in impactOutPrefix if (e.isalnum() or e == " " or e == "_"))
    scrubbedImpactOutPrefix = scrubbedImpactOutPrefix.replace(" ", "_")
    scrubbedImpactBufferOutPrefix = ''.join(e for e in impactBufferOutPrefix if (e.isalnum() or e == " " or e == "_"))
    scrubbedImpactBufferOutPrefix = scrubbedImpactBufferOutPrefix.replace(" ", "_")

    env.overwriteOutput = True
    GCS_WGS_1984 = arcpy.SpatialReference(r"WGS 1984")
    webMercator = arcpy.SpatialReference(r"WGS 1984 Web Mercator (Auxiliary Sphere)")
    env.overwriteOutput = True
    scratch = env.scratchWorkspace
    
    #Project doesn't like in_memory featureclasses, copy to scratch
    copyInFeatures = os.path.join(scratch,"copyInFeatures")
    arcpy.CopyFeatures_management(inFeature,copyInFeatures)
    delete_me.append(copyInFeatures)
    
    layerSymLocation = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'layers'))
    
    #UPDATE
    gisVersion =  arcpy.GetInstallInfo()["Version"]
    #mxd = arcpy.mapping.MapDocument('CURRENT')
    if DEBUG == True: arcpy.AddMessage("Version: " + str(gisVersion))
    mxd,df,aprx,mp = None,None,None,None
    if gisVersion == "10.3.0" or gisVersion == "10.2.0":   #This is ArcMap 10.3
    #TODO replace with regex & check for 10.?.?
         mxd = arcpy.mapping.MapDocument("CURRENT")
         df = arcpy.mapping.ListDataFrames(mxd)[0]
    else:  #This Is Pro
         aprx = arcpy.mapping.ArcGISProject("CURRENT")
         mp = aprx.listMaps()[0]
    
    
    arcpy.AddMessage("Projecting input points to Web Mercator ...")
    prjImpactPoints = os.path.join(outWorkspace, scrubbedImpactOutPrefix + 'prj')
    #TODO: should think about something other than Web Mercator, local AzEd or UTM?
    arcpy.Project_management(copyInFeatures,prjImpactPoints,webMercator)
    delete_me.append(prjImpactPoints)
    
    arcpy.AddMessage("Adding MGRS to input points ...")
    prjImpactCCN = os.path.join(outWorkspace, scrubbedImpactOutPrefix)
    arcpy.AddXY_management(prjImpactPoints)
    arcpy.ConvertCoordinateNotation_management(prjImpactPoints, prjImpactCCN, "Point_X", "Point_Y", "SHAPE", "MGRS")
        
    #UPDATE
    layerToAdd = None
    if not df == None:
        if DEBUG == True: arcpy.AddMessage("ARCMAP: Adding Impact Points")
        layerToAdd = arcpy.mapping.Layer(prjImpactCCN)
        arcpy.ApplySymbologyFromLayer_management(layerToAdd, layerSymLocation + "\Impact Point Centers.lyr")
        arcpy.mapping.AddLayer(df, layerToAdd, "AUTO_ARRANGE")
    else:
        if DEBUG == True:
            arcpy.AddMessage("PRO: Adding Impact Points")
            arcpy.AddMessage("prjImpactCCN: " + str(prjImpactCCN))
            arcpy.AddMessage("exists?: " + str(arcpy.Exists(prjImpactCCN)))
            arcpy.AddMessage("scrubbedImpactOutPrefix: " + str(scrubbedImpactOutPrefix))
        
        #layerToAdd = arcpy.management.MakeFeatureLayer(prjImpactCCN)[0]
        #layerToAdd = arcpy.management.MakeFeatureLayer(prjImpactCCN,scrubbedImpactOutPrefix)[0]
        layerToAdd = arcpy.MakeFeatureLayer_management(prjImpactCCN,scrubbedImpactOutPrefix)[0]
        #arcpy.AddMessage("layerToAdd: " + str(layerToAdd.name)) #ERROR: "NoneType object has no attribute 'name'
        #arcpy.management.MakeFeatureLayer(prjImpactCCN,scrubbedImpactOutPrefix)
        
        #arcpy.management.ApplySymbologyFromLayer(layerToAdd, layerSymLocation + "\Impact Point Centers.lyr") # ERROR IF I USE THIS
      
        #mp.addLayer(layerToAdd,"AUTO_ARRANGE") # ERROR IF I USE THIS
        #mp.addLayer(prjImpactCCN,"AUTO_ARRANGE") # ERROR IF I USE THIS
        
        arcpy.AddMessage("map layers: " + str(mp.listLayers()))
        for i in mp.listLayers():
            arcpy.AddMessage(str(i) + ": " + str(i.name))
            
        arcpy.AddMessage("+++++++++++++++++++++++++++++++++++++++++")
   

    #Loop through the weapons and create create the Point of Origin for each
    for index in range(len(models)):
        model = models[index]
        scrubbedModel = ''.join(e for e in model if (e.isalnum() or e == " " or e == "_"))
        scrubbedModel = scrubbedModel.replace(" ", "_")
        if DEBUG == True: 
           arcpy.AddMessage("Model: " + model) 
           arcpy.AddMessage("Scrubbed Model: " + scrubbedModel) 
        arcpy.AddMessage("Getting impact points ....")
        shapefieldname = arcpy.Describe(prjImpactPoints).ShapeFieldName
        rows = arcpy.SearchCursor(inFeature)
        finalIntersect = os.path.join(scratch,"finalIntersect")
        lastIntersect = os.path.join(scratch,"lastIntersect")
        counter = 0     
        #Set the minimum and maximum range based on the selected weapon system
        where = modelField + " = " + model
        fields = minRangeField + "," + maxRangeField
        cursor = arcpy.SearchCursor(weaponTable, where, None,fields)
        
        #record = cursor.next() #UPDATE
        record = next(cursor)        
                
        minRange =  record.getValue(minRangeField)
        maxRange =  record.getValue(maxRangeField)  
        arcpy.AddMessage("Getting Range for: " + model)
        arcpy.AddMessage("Minimum Range: " + str(minRange))
        arcpy.AddMessage("Maximum Range: " + str(maxRange)) 
        # get a list of impact points
        impactPoints = []        
        for row in rows:                   
            counter += 1                      
            feat = row.getValue(shapefieldname)   
            arcpy.AddMessage("Buffering Impact Point: " + model + "_" + str(counter))     
            # for each impact point, Create a layer conataing the max and min range rings  
            impactMaxBuffer = os.path.join(env.scratchWorkspace,"Impact_Max_" + str(counter) + "_" + scrubbedModel)
            impactMinBuffer = os.path.join(env.scratchWorkspace,"Impact_Min_" + str(counter) + "_" + scrubbedModel)
            impactPointBuffer = os.path.join(env.scratchWorkspace,"Impact_Point_" + str(counter) + "_" + scrubbedModel) 
            arcpy.Buffer_analysis(feat,impactMaxBuffer,maxRange)        
            arcpy.Buffer_analysis(feat,impactMinBuffer,minRange)  
            arcpy.Erase_analysis(impactMaxBuffer, impactMinBuffer, impactPointBuffer)      
            #Add this impact point to the list to be intersected.
            impactPoints.append(impactPointBuffer);
            #Project the buffer
            impactPointClassName = scrubbedImpactBufferOutPrefix + "_" + str(counter) + "_" + scrubbedModel
            impactPointOut = os.path.join(outWorkspace,impactPointClassName)
            arcpy.Project_management(impactPointBuffer,impactPointOut,GCS_WGS_1984)            
            
            #UPDATE
            if not df == None:
                layerToAdd = arcpy.mapping.Layer(impactPointOut)
                arcpy.ApplySymbologyFromLayer_management(layerToAdd, layerSymLocation + "\ImpactRange.lyr")
            else:
                layerToAdd = arcpy.MakeFeatureLayer_management(impactPointOut)[0]
                arcpy.ApplySymbologyFromLayer_management(impactPointOut, layerSymLocation + "\ImpactRange.lyr")           
            
            #UPDATE
            if not df == None:
                arcpy.mapping.AddLayer(df, layerToAdd, "AUTO_ARRANGE")
            else:
                mp.addLayer(layerToAdd)
            
            delete_me.append(impactMaxBuffer)
            delete_me.append(impactMinBuffer)
            delete_me.append(impactPointBuffer)
        #Intersect the impact points
        arcpy.Intersect_analysis(impactPoints,finalIntersect,"","","")      
        delete_me.append(finalIntersect)
        del rows    
        #Project the Point of Oigin area
        featureClassName = scrubbedPooOutPrefix + "_" + scrubbedModel
        output_poo = os.path.join(outWorkspace,featureClassName)
        arcpy.Project_management(finalIntersect,output_poo,GCS_WGS_1984)
        
        #UPDATE
        if not df == None:
            layerToAdd = arcpy.mapping.Layer(output_poo)
        else:
            layerToAdd = arcpy.MakeFeatureLayer_management(output_poo)[0]
            
        arcpy.ApplySymbologyFromLayer_management(layerToAdd, layerSymLocation + "\PointOfOrigin.lyr")
        
        #UPDATE
        if not df == None:
            arcpy.mapping.AddLayer(df, layerToAdd, "AUTO_ARRANGE")
        else:
            mp.addLayer(layerToAdd)
  
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
    for i in delete_me:
        if DEBUG == True: arcpy.AddMessage("Removing: " + str(i))
        arcpy.Delete_management(i)
    if DEBUG == True: arcpy.AddMessage("Done")

