# ---------------------------------------------------------------------------
# PointOfOrigin.py
# Created on: 09-16-2013
# Created by: Michael Reynolds
# Description: Triangulates the potential area for the point of origin of enemy
#   indirect fire given three or more known impact points.
# ---------------------------------------------------------------------------
# 2/6/2015 - mf - Update for user-selected coordinate system, and arcpy.mp for ArcGIS Pro 1.0, and output features
# 7/1/2015 - ps - Update for date_time suffix for the Group Layer result.
# 7/2/2015 - ps - Added Transparency for "Point of Origin Results" group layer polygons.
# 7/2/2015 - ps - Added checks for layerSymLocation for post "Share as Template", or restored "Share Project Package"
# 7/6/2015 - ps Added logic to check for Desktop, or Pro 1.0 in order to call cursor() properly for respective version.
# 7/8/2015 - ps Review "locals", delete more locals.
# 7/9/2015 - ps Modified  script to include function CheckVariables() which displays "locals()" when DEBUG is turned on.
# 7/13/2015 - ps Added logic to hold Group Layer Result with a time string appended to the Group Layer name.
# 7/14/2015 - ps Noticed that issue with hang at MakeFeatureLayer_management is related to Pro's Indexing and/or the Windows process ArcGISCleanup.exe
# 7/16/2015 - ps Added option to uncheck True Curve, results in densified polygon which can be projected on the fly more readily that True Curve
# Using Build 3308 (1.1.1 release)
# 10/19/2015 - ps Restructured to use method ins Utilities.py  - try block "from arcpy import mp" in GetApplication() function.
#
# ---------------------------------------------------------------------------
# Have NOT changed overall structure of script to use Functions()
#
#
# ======================Import arcpy module=================================
import os, sys, traceback, math, decimal, time
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
outputUseTrueCurve = arcpy.GetParameterAsText(14) # boolean string (true or false)

# Will use a time stamp on the grouped layer for keeping track of multiple runs; prefix should distinguish Feature Classes?
timestr = time.strftime("%Y%m%d_%H%M")


delete_me = []
DEBUG = False
#DEBUG = True

app_found = 'NOT_SET'
toolbox10xSuffix = "_10.3"

#desktopVersion = ["10.2.2","10.3","10.3.1"]
proVersion = ["1.0", "1.1", "1.2"]

#------------------------------------------------------------------------------
# check which variables are still set...cleanup variables...
def CheckVariables(inDict):

    if DEBUG == True:
        func_mydict = inDict
        myList = []
        mydict = dict(locals()) # would like to sort this using OrderedDict


        # sorted list keys,values - method/function
        dictlist = []
        for keys,values in func_mydict.items():
            temp = [keys,values]
            dictlist.append(temp)
        dictlist.sort()
        for listItem in dictlist:
            arcpy.AddMessage(str(listItem))

            print(listItem)
        arcpy.AddMessage(" ********************************************** ")

    return

#------------------------------------------------------------------------------

def GetApplication():
    '''Return app environment as: ARCMAP, ARCGIS_PRO, OTHER'''

    global app_found
    if app_found != 'NOT_SET':
            return app_found

    try:
        from arcpy import mp
    except ImportError:
        try:
            from arcpy import mapping
            mxd = arcpy.mapping.MapDocument("CURRENT")
            app_found = "ARCMAP"
            return app_found
        except:
            app_found = "OTHER"
            return app_found
    try:
        aprx = arcpy.mp.ArcGISProject('CURRENT')
        app_found = "ARCGIS_PRO"
        return app_found
    except:
        app_found = "OTHER"
        return app_found
#------------------------------------------------------------------------------

#------------------------------------------------------------------------------

if DEBUG == "True":
    arcpy.AddMessage("Check locals at begining ")
    mydict = dict(locals())
    CheckVariables(mydict)

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
    if scratch == None:
        scratch = 'in_memory'
        env.scratchWorkspace = 'in_memory'


    if outputCoordinateSystemAsText == '':
        outputCoordinateSystem = arcpy.Describe(inFeature).spatialReference
        arcpy.AddWarning("Spatial Reference is not defined. Using Spatial Reference of Impact Points: " + str(outputCoordinateSystem .name))
    env.outputCoordinateSystem = outputCoordinateSystem

    arcpy.AddMessage("Building impact points...")
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
        arcpy.AddMessage("Getting Range for: " + selectedModel)
        if DEBUG == True:
           arcpy.AddMessage("Model: " + selectedModel)
           arcpy.AddMessage("Scrubbed Model: " + scrubbedModel)


        #Set the minimum and maximum range based on the selected weapon system
        where = modelField + " = " + selectedModel
        fields = minRangeField + "," + maxRangeField
        cursor = arcpy.SearchCursor(weaponTable, where, None,fields)

        appEnvironment = GetApplication()

        gisVersion = arcpy.GetInstallInfo()["Version"]
        gisBuild = arcpy.GetInstallInfo()["BuildNumber"]

        if appEnvironment == 'ARCMAP':
            record = cursor.next() # this is method for Pro 1.0.2,
        else:
            if appEnvironment == 'ARCGIS_PRO':
                record = next(cursor) # Python 3 method - but only works in Pro 1.1 later builds.

        minRange =  record.getValue(minRangeField)
        maxRange =  record.getValue(maxRangeField)
        if DEBUG == True:
            arcpy.AddMessage("Minimum Range: " + str(minRange))
            arcpy.AddMessage("Maximum Range: " + str(maxRange))

        del cursor, record

        # combine buffers of all impact points -
        # Consider not using True Curves, or Densifying/Generalizing Buffers into non-True Curve Polygons for Project-on-the-Fly
        impactPointBuffersList = []
        inFields = ["OID@","SHAPE@"]
        rows = arcpy.da.SearchCursor(outputImpactPointFeatures,inFields)
        for row in rows:
            oid = row[0]
            feat = row[1]
            arcpy.AddMessage("Buffering Impact Point OID " + str(oid) + " for " + selectedModel)

            # buffer the max distance from point - check if True Curves are not wanted
            impactMaxBuffer = os.path.join(env.scratchWorkspace,"Impact_Max_" + str(oid) + "_" + scrubbedModel)
            if outputUseTrueCurve == "true":
                if DEBUG == True: arcpy.AddMessage("Using True Curve" )
                arcpy.Buffer_analysis(feat,impactMaxBuffer,maxRange)
                delete_me.append(impactMaxBuffer)
            if outputUseTrueCurve == "false":
                if DEBUG == True: arcpy.AddMessage("Densifying True Curve to regular polygon" )
                arcpy.Buffer_analysis(feat,impactMaxBuffer,maxRange)
                arcpy.Densify_edit(impactMaxBuffer, "ANGLE","", "", "0.75")
                delete_me.append(impactMaxBuffer)

            # buffer the min distance from point
            impactMinBuffer = os.path.join(env.scratchWorkspace,"Impact_Min_" + str(oid) + "_" + scrubbedModel)
            if outputUseTrueCurve == "true":
                if DEBUG == True: arcpy.AddMessage("Using True Curve" )
                arcpy.Buffer_analysis(feat,impactMinBuffer,minRange)
                delete_me.append(impactMinBuffer)
            if outputUseTrueCurve == "false":
                if DEBUG == True: arcpy.AddMessage("Densifying True Curve to regular polygon" )
                arcpy.Buffer_analysis(feat,impactMinBuffer,minRange)
                arcpy.Densify_edit(impactMinBuffer, "ANGLE","", "", "0.75")
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
        del rows, row, indexWeaponModel
    # model loop ends here, on to next model

    # now for symbology...
    if DEBUG == True: arcpy.AddMessage("Possible locations - examine some paths for locations of layer .lyrx files")
    if DEBUG == True: arcpy.AddMessage("layerSymLocation1 : " + os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    if DEBUG == True: arcpy.AddMessage("layerSymLocation2 : " + os.path.join(os.path.dirname(__file__)))
    if DEBUG == True: arcpy.AddMessage("layerSymLocation3 : " + os.path.abspath(os.path.join(os.path.dirname(__file__))))
    if DEBUG == True: arcpy.AddMessage("layerSymLocation4 : " + os.path.abspath(os.path.join(os.path.dirname(__file__), 'commondata', 'userdata')))

    # now for symbology, check to see if this where layers might be located due to "Share as Project Template", or "Export Project Package"...

    # 1. Layers in folder parallel to folder with script - standard as developed -  (i.e. /project_loc/scripts and /project_loc/layers)
    if os.path.isdir(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'layers'))) and  \
       os.path.isfile(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'layers', 'Impact_Point_Centers.lyrx'))):
        layerSymLocation = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'layers'))
    #
    # 2. Layers restored into folder at same level as script /project_loc/pointoforigindetection.py and /project_loc/layers)
    elif os.path.isdir(os.path.abspath(os.path.join(os.path.dirname(__file__), 'layers'))) and \
         os.path.isfile(os.path.abspath(os.path.join(os.path.dirname(__file__), 'layers', 'Impact_Point_Centers.lyrx'))):
        layerSymLocation = os.path.abspath(os.path.join(os.path.dirname(__file__), 'layers'))
    #
    # 3. Layers in root level of project at same level as script (i.e /project_loc/pointoforigindetection.py and /project_loc/PointOfOrigin.lyrx)
    elif os.path.isdir(os.path.abspath(os.path.join(os.path.dirname(__file__), ))) and \
         os.path.isfile(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Impact_Point_Centers.lyrx'))):
        layerSymLocation = os.path.abspath(os.path.join(os.path.dirname(__file__),''))
    #
    # 4. commondata\userdata - most common
    # Layers restored from Share as "Project template" (and "Share as Project Package" - location (i.e /project_loc/pointoforigindetection.py and /project_loc/commondata/userdata/PointOfOrigin.lyrx)
    elif os.path.isdir(os.path.abspath(os.path.join(os.path.dirname(__file__), 'commondata', 'userdata'))) and \
         os.path.isfile(os.path.abspath(os.path.join(os.path.dirname(__file__), 'commondata', 'userdata', 'Impact_Point_Centers.lyrx'))):
        layerSymLocation = os.path.abspath(os.path.join(os.path.dirname(__file__), 'commondata', 'userdata'))
    #
    # else it can't find layers
    else:
        arcpy.AddWarning("Cannot find location of required layer files (.lyrx), cannot continue")
    #
    if DEBUG == True: arcpy.AddMessage("Using layerSymLocation: " + str(layerSymLocation))
    gisVersion = arcpy.GetInstallInfo()["Version"]
    if DEBUG == True: arcpy.AddMessage(r"gisVersion: " + str(gisVersion))

    try:
        #else: #Update for automated test
        if appEnvironment == 'ARCMAP':
            arcpy.AddMessage("Using ArcMap")
            from arcpy import mapping
            mxd = arcpy.mapping.MapDocument('CURRENT')
            df = arcpy.mapping.ListDataFrames(mxd)[0]
            isPro = False

    except:  # if "OTHER" , then just skip this part...
            arcpy.AddWarning("Tool is not run in ArcMap, skipping symbolization scheme.")

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

            del df
            del mxd

    # if Pro:
    #if gisVersion == "1.0": #Pro: #Update for automated test
    if appEnvironment == "ARCGIS_PRO":
        from arcpy import mp
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        mapList = aprx.listMaps()[0]
        isPro = True

        # make top group layer
        arcpy.AddMessage("Adding Top Group Layer...")
        groupLayerPath = os.path.join(layerSymLocation,"New_Group_Layer.lyrx")
        arcpy.AddMessage("Added Top Group Layer...")

        # Add date/timestring to initialGroupLayer - older build were hanging when using this, at point of "Adding Impact Points..." ?
        if DEBUG == True: arcpy.AddMessage("Using time string on mapList.addlayer...")
        initialGroupLayer = arcpy.mp.LayerFile(groupLayerPath).listLayers()[0]
        initialGroupLayer_timestr = "Point Of Origin Results_" + timestr
        initialGroupLayer.name = initialGroupLayer_timestr
        mapList.addLayer(initialGroupLayer,"AUTO_ARRANGE")
        if DEBUG == True: arcpy.AddMessage(" mapList.addlayer succeeded...")
        topGroupLayer = mapList.listLayers(initialGroupLayer_timestr)[0]

        initialGroupLayer = None
        #del initialGroupLayer # this line hangs tool dialog.  (pks - this line is not used, but appears there is a typo "initialGroupayer" in original code?)

        ## add the impact points
        arcpy.AddMessage("Adding Impact Points ...")
        #if DEBUG == True: arcpy.AddMessage("impactPointLayer1")
        impactPointLayerFilePath = os.path.join(layerSymLocation,"Impact_Point_Centers.lyrx")
        #if DEBUG == True: arcpy.AddMessage("impactPointLayer1a")
        #impactPointLayer = arcpy.mp.LayerFile(impactPointLayerFilePath).listLayers()[0] # this line hangs tool dialog...
        #if DEBUG == True: arcpy.AddMessage("impactPointLayer2")
        #impactPointLayer.dataSource = outputImpactPointFeatures
        #if DEBUG == True: arcpy.AddMessage("impactPointLayer3")
        #impactPointLayer.name = "Impact points"
        #if DEBUG == True: arcpy.AddMessage("impactPointLayer4")
        #mapList.addLayerToGroup(topGroupLayer,impactPointLayer,"TOP")
        #if DEBUG == True: arcpy.AddMessage("impactPointLayer5")

        ipName = "Impact points" + "_" + timestr

        if DEBUG == True:
            arcpy.AddMessage("Check locals() before MakeFeatureLayer ")
            mydict = dict(locals())
            CheckVariables(mydict)
        if DEBUG == True: arcpy.AddMessage("arcpy.MakeFeatureLayer(...) ** Hang's here **" )

        # ---> issue with: results = arcpy.MakeFeatureLayer_management(outputImpactPointFeatures,ipName).getOutput(0) <---
        try:
            if arcpy.Exists(outputImpactPointFeatures): # This describe is attempt to verify outputImpactPointFeatures is valid
                # Create a Describe object from the feature class - put this in DEBUG when all is stable.
                desc = arcpy.Describe(outputImpactPointFeatures)

                if DEBUG == True:
                    # Print some feature class properties of outputImpactPointFeatures
                    #
                    arcpy.AddMessage("Feature Type:  " + desc.featureType)
                    arcpy.AddMessage("Shape Type :   " + desc.shapeType)
                    arcpy.AddMessage("Spatial Index: " + str(desc.hasSpatialIndex))
                    arcpy.AddMessage("shapeFieldName:     " + desc.shapeFieldName)
                    arcpy.AddMessage("ShapeType:     " + desc.shapeType)

                if DEBUG == True: arcpy.AddMessage("Current outputImpactPointFeatures exist, proceeding with MakeFeatureLayer_management")
                results = arcpy.MakeFeatureLayer_management(outputImpactPointFeatures,ipName, None, None).getOutput(0)
                #results = arcpy.management.MakeFeatureLayer("imp_2000", "Impact Points_2015_1645", None, None, "OID OID VISIBLE NONE;Shape Shape VISIBLE NONE;POINT_X POINT_X VISIBLE NONE;POINT_Y POINT_Y VISIBLE NONE;MGRS_2 MGRS_2 VISIBLE NONE;MGRS MGRS VISIBLE NONE")
            else:
                arcpy.AddMessage("Error: " + outputImpactPointFeatures + " does not exist")
        except Exception:
            e = sys.exc_info()[1]
            arcpy.AddError(e.args[0])


# ['results', <arcpy._mp.Layer object at 0x0000000063221DA0>] - this is a layer object, cannot check .status or -> ErrorInfo: 'Layer' object has no attribute 'status'
# tried sleeping until "result" status has succeeded... http://pro.arcgis.com/en/pro-app/arcpy/classes/result.htm -
# tried change "results" to "result".

        #  Applying symbology to result points before adding to Group works better than after adding to group

        if DEBUG == True: arcpy.AddMessage("ApplySymbologyFromLayer")
        arcpy.ApplySymbologyFromLayer_management(results,impactPointLayerFilePath) # for some reason this guy does not always work prior to adding apply the symbology
        #arcpy.ApplySymbologyFromLayer_management(ipName,impactPointLayerFilePath) # for some reason this guy does work prior to adding apply the symbology

        ## following did not work, seems to want the "results" Layer Object.
        ##arcpy.MakeFeatureLayer_management(outputImpactPointFeatures,impactPointLayerFilePath) # for some reason this guy doesn't apply the symbology


        if DEBUG == True: arcpy.AddMessage("mapList.addLayerToGroup(...)")
        mapList.addLayerToGroup(topGroupLayer,results,"TOP")
        #mapList.addLayerToGroup(topGroupLayer,ipName,"TOP")

##        if DEBUG == True: arcpy.AddMessage("ApplySymbologyFromLayer")
##        arcpy.ApplySymbologyFromLayer_management(results,impactPointLayerFilePath) # for some reason this guy doesn't apply the symbology

        # for all items in the combinedPooDict
        for model in modelOriginsDict:
            arcpy.AddMessage("Adding model: " + str(model))

            # make a group layer for each model
            initialGroupLayer = arcpy.mp.LayerFile(groupLayerPath).listLayers()[0]
            initialGroupLayer.name = model
            mapList.addLayerToGroup(topGroupLayer,initialGroupLayer,"BOTTOM")
            modelGroupLayer = mapList.listLayers(model)[0]
            initialGroupLayer = None

            # get range and POO data from this model
            modelData = modelOriginsDict[model]

            # make layer for combined area and add to model layer
            combinedDict = modelData[1]
            combinedAreaLayer = arcpy.mp.LayerFile(os.path.join(layerSymLocation, "PointOfOrigin.lyrx")).listLayers()[0]
            combinedAreaLayer.dataSource = combinedDict["combined"]
            combinedAreaLayer.name = model + " Point Of Origin"
            mapList.addLayerToGroup(modelGroupLayer,combinedAreaLayer,"BOTTOM")

            initialGroupLayer = arcpy.mp.LayerFile(groupLayerPath).listLayers()[0]
            rangeLayerName = model + " Ranges by Impact OID"
            initialGroupLayer.name = rangeLayerName
            mapList.addLayerToGroup(modelGroupLayer,initialGroupLayer,"BOTTOM")
            rangeGroupLayer = mapList.listLayers(rangeLayerName)[0]
            initialGroupLayer = None

            # Add the individual ranges to the range group layer
            modelRanges = modelData[0]['ranges']
            for r in modelRanges:
                rangeToAdd = arcpy.mp.LayerFile(os.path.join(layerSymLocation, "ImpactRange.lyrx")).listLayers()[0]
                rangeToAdd.dataSource = r
                rangeToAdd.name = os.path.basename(r)
                mapList.addLayerToGroup(rangeGroupLayer,rangeToAdd,"BOTTOM")

            # Set Transparency of result Group Layers to "50"
            if modelGroupLayer.supports("TRANSPARENCY"):
                modelGroupLayer.transparency = 50

        del aprx, mapList

    else:
        arcpy.AddWarning(r"...Could not determine version.\n   Looking for ArcMap " + str(desktopVersion) + ", or ArcGIS Pro " + str(proVersion) + ".\n   Found " + str(gisVersion))

    # Set tool output
    if DEBUG == True: arcpy.AddMessage("Setting output parameters...")
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

    # check which variables are still set...cleanup variables...
    if DEBUG == True:
        arcpy.AddMessage("Check locals at end script run ")
        mydict = dict(locals())
        CheckVariables(mydict)
#eof

