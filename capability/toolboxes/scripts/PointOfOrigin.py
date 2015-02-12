# ---------------------------------------------------------------------------
# PointOfOrigin.py
# Created on: 09-16-2013
# Created by: Michael Reynolds
# Description: Triangulates the potential area for the point of origin of enemy
#   indirect fire given three or more known impact points.
# ---------------------------------------------------------------------------
# 2/6/2015 - mf - Update for user-selected coordinate system, and arcpy.mp for ArcGIS Pro 1.0, and output features
#

# ======================Import arcpy module=================================
import os, sys, traceback, math, decimal
import arcpy
from arcpy import env

# ======================ARGUMENTS & LOCALS ===============================
inFeature = arcpy.GetParameterAsText(0) # Feature Set
weaponTable = arcpy.GetParameterAsText(1) # Table View
modelField = arcpy.GetParameterAsText(2) # Field
minRangeField = arcpy.GetParameterAsText(3) # Field
maxRangeField = arcpy.GetParameterAsText(4) # Field
selectedWeaponModels = arcpy.GetParameterAsText(5).split(';') # String?

outWorkspace = arcpy.GetParameterAsText(6) # Workspace
pooOutPrefix = arcpy.GetParameterAsText(7) # String
impactOutPrefix = arcpy.GetParameterAsText(8) # String
impactBufferOutPrefix = arcpy.GetParameterAsText(9) #String

# Need to set some tool outputs
outputImpactFeatures = None
outputPointsOfOriginFeatures = [] # Feature Class - multiple
outputImpactRangeFeatures = [] # Feature Class - multiple

outputCoordinateSystem = arcpy.GetParameter(13) # Coordinate System
outputCoordinateSystemAsText = arcpy.GetParameterAsText(13) # String

delete_me = []
DEBUG = True
desktopVersion = ["10.2.2","10.3"]
proVersion = ["1.0"]



try:       
    # For the model and all outputs remove special characters and replace spaces with underscores    
    scrubbedPooOutPrefix = ''.join(e for e in pooOutPrefix if (e.isalnum() or e == " " or e == "_"))
    scrubbedPooOutPrefix = scrubbedPooOutPrefix.replace(" ", "_")
    scrubbedImpactOutPrefix = ''.join(e for e in impactOutPrefix if (e.isalnum() or e == " " or e == "_"))
    scrubbedImpactOutPrefix = scrubbedImpactOutPrefix.replace(" ", "_")
    scrubbedImpactBufferOutPrefix = ''.join(e for e in impactBufferOutPrefix if (e.isalnum() or e == " " or e == "_"))
    scrubbedImpactBufferOutPrefix = scrubbedImpactBufferOutPrefix.replace(" ", "_")

    env.overwriteOutput = True    
    scratch = env.scratchWorkspace
    
    if outputCoordinateSystemAsText == '':
        outputCoordinateSystem = arcpy.Describe(inFeature).spatialReference
        arcpy.AddWarning("Spatial Reference is not defined. Using Spatial Reference of Impact Points: " + str(outputCoordinateSystem .name))
    env.outputCoordinateSystem = outputCoordinateSystem
    
    #Project doesn't like in_memory featureclasses, copy to scratch
    copyInFeatures = os.path.join(scratch,"copyInFeatures")
    outputImpactPointFeatures = os.path.join(outWorkspace,scrubbedImpactOutPrefix)
    arcpy.CopyFeatures_management(inFeature,copyInFeatures)
    delete_me.append(copyInFeatures)   
    arcpy.AddXY_management(copyInFeatures)
    arcpy.ConvertCoordinateNotation_management(copyInFeatures,outputImpactPointFeatures, "Point_X", "Point_Y", "SHAPE", "MGRS")
    delete_me.append(copyInFeatures)

    modelOriginsDict = {} #modelOriginsDict[scrubbedModel] = [{"ranges":impactPointBuffersList},{"combined":output_poo}]

    #Loop through the weapons and create create the Point of Origin for each
    for indexWeaponModel in range(len(selectedWeaponModels)):
        
        selectedModel = selectedWeaponModels[indexWeaponModel]
        scrubbedModel = ''.join(e for e in selectedModel if (e.isalnum() or e == " " or e == "_"))
        scrubbedModel = scrubbedModel.replace(" ", "_")
        
        if DEBUG == True: 
           arcpy.AddMessage("Model: " + selectedModel) 
           arcpy.AddMessage("Scrubbed Model: " + scrubbedModel)
           
        arcpy.AddMessage("Getting impact points ....")
        
        #Set the minimum and maximum range based on the selected weapon system
        where = modelField + " = " + selectedModel
        fields = minRangeField + "," + maxRangeField
        cursor = arcpy.SearchCursor(weaponTable, where, None,fields)
        record = cursor.next()
        minRange =  record.getValue(minRangeField)
        maxRange =  record.getValue(maxRangeField)
        arcpy.AddMessage("Getting Range for: " + selectedModel)
        arcpy.AddMessage("Minimum Range: " + str(minRange))
        arcpy.AddMessage("Maximum Range: " + str(maxRange))

        # combine buffers of all impact points
        impactPointBuffersList = []
        inFields = ["OID@","SHAPE@"]
        rows = arcpy.da.SearchCursor(outputImpactPointFeatures,inFields)
        for row in rows:                   
            oid = row[0]
            feat = row[1]
            arcpy.AddMessage("Buffering Impact Point OID " + str(oid) + " for " + selectedModel)
            
            # buffer the max distance from point
            impactMaxBuffer = os.path.join(env.scratchWorkspace,"Impact_Max_" + str(oid) + "_" + scrubbedModel)            
            arcpy.Buffer_analysis(feat,impactMaxBuffer,maxRange)
            delete_me.append(impactMaxBuffer)
            
            # buffer the min distance from point
            impactMinBuffer = os.path.join(env.scratchWorkspace,"Impact_Min_" + str(oid) + "_" + scrubbedModel)
            arcpy.Buffer_analysis(feat,impactMinBuffer,minRange)
            delete_me.append(impactMinBuffer)
            
            # Find the area within the model weapon areas min and max ranges
            impactPointClassName = scrubbedImpactBufferOutPrefix + "_" + str(oid) + "_" + scrubbedModel
            impactPointOut = os.path.join(outWorkspace,impactPointClassName)
            arcpy.Erase_analysis(impactMaxBuffer, impactMinBuffer, impactPointOut)
            arcpy.AddField_management(impactPointOut,"ImpactID","LONG","","","","Impact OID")
            arcpy.CalculateField_management(impactPointOut,"ImpactID",oid,"PYTHON_9.3")
            arcpy.AddField_management(impactPointOut,"Model","TEXT","","","","Weapon Model")
            arcpy.CalculateField_management(impactPointOut,"Model",selectedModel,"PYTHON_9.3")
            arcpy.AddField_management(impactPointOut,"MinRange","DOUBLE","","","","Minimum Range")
            arcpy.CalculateField_management(impactPointOut,"MinRange",minRange,"PYTHON_9.3")
            arcpy.AddField_management(impactPointOut,"MaxRange","DOUBLE","","","","Maximum Range")
            arcpy.CalculateField_management(impactPointOut,"MaxRange",maxRange,"PYTHON_9.3")
            
            #Add this area to the list to be intersected.
            impactPointBuffersList.append(impactPointOut);
            #Add this area to the output list
            outputImpactRangeFeatures.append(impactPointOut)
        # impact point loop ends here, on to next point
        
        #Intersect the areas of all impact points for this model
        featureClassName = scrubbedPooOutPrefix + "_" + scrubbedModel
        output_poo = os.path.join(outWorkspace,featureClassName)
        arcpy.Intersect_analysis(impactPointBuffersList,output_poo,"","","")
        arcpy.AddField_management(output_poo,"Model","TEXT","","","","Weapon Model")
        arcpy.CalculateField_management(output_poo,"Model",selectedModel,"PYTHON_9.3")
        outputPointsOfOriginFeatures.append(output_poo)

        modelOriginsDict[scrubbedModel] = [{"ranges":impactPointBuffersList},{"combined":output_poo}]
        del rows
    # model loop ends here, on to next model
    
    # now for symbology...
    layerSymLocation = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'layers'))
    gisVersion = arcpy.GetInstallInfo()["Version"]
    if DEBUG == True: arcpy.AddMessage(r"gisVersion: " + str(gisVersion))
    if gisVersion in desktopVersion: #This is ArcMap 10.3 or 10.2.2

        mxd = arcpy.mapping.MapDocument('CURRENT')
        df = arcpy.mapping.ListDataFrames(mxd)[0]
        
        # make group layer and add it to the map
        groupLayerPath = os.path.join(layerSymLocation,"New Group Layer.lyr")
        initialGroupLayer = arcpy.mapping.Layer(groupLayerPath)
        initialGroupLayer.name = "Point Of Origin Results"
        arcpy.mapping.AddLayer(df,initialGroupLayer)
        del initialGroupLayer
        
        # get a reference to the group layer in the map
        topGroupLayer = arcpy.mapping.ListLayers(mxd,"Point Of Origin Results",df)[0]
        
        # add the impact points
        impactPointLayer = arcpy.mapping.Layer(outputImpactPointFeatures)
        impactPointLayer.name = "Impact points"
        arcpy.ApplySymbologyFromLayer_management(impactPointLayer, os.path.join(layerSymLocation, "Impact Point Centers.lyr"))
        arcpy.mapping.AddLayerToGroup(df,topGroupLayer, impactPointLayer,"TOP")
        
        # for all items in the combinedPooDict
        for model in modelOriginsDict:
            
            # make a group layer for each model
            initialGroupLayer = arcpy.mapping.Layer(groupLayerPath)
            initialGroupLayer.name = model
            arcpy.mapping.AddLayerToGroup(df,topGroupLayer,initialGroupLayer,"BOTTOM")
            modelGroupLayer = arcpy.mapping.ListLayers(mxd,model,df)[0]
            del initialGroupLayer
            
            # get range and POO data from this model
            modelData = modelOriginsDict[model]
        
            # make layer for combined area and add to model layer
            combinedDict = modelData[1]
            combinedAreaLayer = arcpy.mapping.Layer(combinedDict["combined"]) #combined
            combinedAreaLayer.name = model + " Point Of Origin"
            arcpy.ApplySymbologyFromLayer_management(combinedAreaLayer, os.path.join(layerSymLocation, "PointOfOrigin.lyr"))
            arcpy.mapping.AddLayerToGroup(df,modelGroupLayer,combinedAreaLayer,"BOTTOM")
            
            # make Range group layer
            initialGroupLayer = arcpy.mapping.Layer(groupLayerPath)
            rangeLayerName = model + " Ranges by Impact OID"
            initialGroupLayer.name = rangeLayerName
            arcpy.mapping.AddLayerToGroup(df,modelGroupLayer,initialGroupLayer,"BOTTOM")
            rangeGroupLayer = arcpy.mapping.ListLayers(mxd,rangeLayerName,df)[0]
            del initialGroupLayer
            
            # Add the individual ranges to the range group layer
            modelRanges = modelData[0]['ranges'] #ranges
            for r in modelRanges:
                rangeToAdd = arcpy.mapping.Layer(r)
                arcpy.ApplySymbologyFromLayer_management(rangeToAdd, os.path.join(layerSymLocation, "ImpactRange.lyr"))
                arcpy.mapping.AddLayerToGroup(df,rangeGroupLayer,rangeToAdd,"BOTTOM")
        
        del mxd, df
    
    # if Pro:
    elif gisVersion in proVersion: #This Is  ArcGIS Pro  1.0+
        aprx = arcpy.mp.ArcGISProject(r"current")
        m = aprx.listMaps()[0]
        
        # make top group layer
        if DEBUG == True: arcpy.AddMessage("groupLayerPath1")
        groupLayerPath = os.path.join(layerSymLocation,"New Group Layer.lyr")
        if DEBUG == True: arcpy.AddMessage("groupLayerPath2")
        initialGroupLayer = arcpy.mp.LayerFile(groupLayerPath).listLayers()[0]
        if DEBUG == True: arcpy.AddMessage("groupLayerPath3")
        initialGroupLayer.name = "Point Of Origin Results"
        if DEBUG == True: arcpy.AddMessage("groupLayerPath4")
        m.addLayer(initialGroupLayer,"AUTO_ARRANGE")
        if DEBUG == True: arcpy.AddMessage("groupLayerPath5")
        topGroupLayer  = m.listLayers("Point Of Origin Results")[0]
        if DEBUG == True: arcpy.AddMessage("groupLayerPath6")
        #del initialGroupLayer  #Pro tool dialog is unresponsive here....
        initialGroupLayer = None
        
        # add the impact points
        if DEBUG == True: arcpy.AddMessage("impactPointLayer1")
        impactPointLayerList= arcpy.mp.LayerFile(os.path.join(layerSymLocation,"Impact Point Centers.lyr")).listLayers()
        if DEBUG == True: arcpy.AddMessage("impactPointLayer1a")
        impactPointLayer = impactPointLayerList[0] #Pro tool dialog is unresponsive her
        if DEBUG == True: arcpy.AddMessage("impactPointLayer2")
        impactPointLayer.dataSource = outputImpactPointFeatures
        if DEBUG == True: arcpy.AddMessage("impactPointLayer3")
        impactPointLayer.name = "Impact points"
        if DEBUG == True: arcpy.AddMessage("impactPointLayer4")
        m.addLayerToGroup(topGroupLayer,impactPointLayer,"TOP")
        if DEBUG == True: arcpy.AddMessage("impactPointLayer5")
        
        # for all items in the combinedPooDict 
        for model in modelOriginsDict:
            if DEBUG == True: arcpy.AddMessage("model: " + str(model))
            
            # make a group layer for each model
            initialGroupLayer = arcpy.mp.LayerFile(groupLayerPath).listLayers()[0]
            initialGroupLayer.name = model
            m.addLayerToGroup(topGroupLayer,initialGroupLayer,"BOTTOM")
            modelGroupLayer = m.listLayers(model)[0]
            initialGroupLayer = None
            #del initialGroupLayer
            
            # get range and POO data from this model
            modelData = modelOriginsDict[model]
            
            # make layer for combined area and add to model layer
            combinedDict = modelData[1]
            combinedAreaLayer = arcpy.mp.LayerFile(os.path.join(layerSymLocation, "PointOfOrigin.lyr")).listLayers()[0]
            combinedAreaLayer.dataSource = combinedDict["combined"]
            combinedAreaLayer.name = model + " Point Of Origin"
            m.addLayerToGroup(modelGroupLayer,combinedAreaLayer,"BOTTOM")
            
            initialGroupLayer = arcpy.mp.LayerFile(groupLayerPath).listLayers()[0]
            rangeLayerName = model + " Ranges by Impact OID"
            initialGroupLayer.name = rangeLayerName
            m.addLayerToGroup(modelGroupLayer,initialGroupLayer,"BOTTOM")
            rangeGroupLayer = m.listLayers(rangeLayerName)[0]
            initialGroupLayer = None
            #del initialGroupLayer
            
            # Add the individual ranges to the range group layer
            modelRanges = modelData[0]['ranges']
            for r in modelRanges:
                rangeToAdd = arcpy.mp.LayerFile(os.path.join(layerSymLocation, "ImpactRange.lyr")).listLayers()[0]
                rangeToAdd.dataSource = r
                rangeToAdd.name = os.path.basename(r)
                m.addLayerToGroup(rangeGroupLayer,rangeToAdd,"BOTTOM")
        del aprx, m
        
    else:
        arcpy.AddWarning(r"...Could not determine version.\n   Looking for ArcMap " + str(desktopVersion) + ", or ArcGIS Pro " + str(proVersion) + ".\n   Found " + str(gisVersion))

    # Set tool output
    arcpy.SetParameter(10,outputImpactPointFeatures) #Single
    arcpy.SetParameter(11,outputPointsOfOriginFeatures) #Multiple?
    arcpy.SetParameter(12,outputImpactRangeFeatures) #Multiple?
    if DEBUG == True: arcpy.AddMessage("Done.")
  
except arcpy.ExecuteError: 
    # Get the tool error messages 
    msgs = arcpy.GetMessages() 
    arcpy.AddError(msgs) 
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
    print(pymsg + "\n")
    print(msgs)

finally:
    # cleanup intermediate datasets
    if DEBUG == True: arcpy.AddMessage("Removing intermediate datasets...")
    for i in delete_me:
        if DEBUG == True: arcpy.AddMessage("Removing: " + str(i))
        arcpy.Delete_management(i)
    if DEBUG == True: arcpy.AddMessage("Done")

