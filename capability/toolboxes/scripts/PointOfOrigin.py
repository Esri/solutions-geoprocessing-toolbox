# ---------------------------------------------------------------------------
# PointOfOrigin.py
# Created on: 09-16-2013
# Created by: Michael Reynolds
# Description: Triangulates the potential area for the point of origin of enemy
#   indirect fire given three or more known impact points.
# ---------------------------------------------------------------------------
# 2/6/2015 - mf - Update for user-selected coordinate system, and arcpy.mp for ArcGIS Pro 1.0, and output features
# 7/1/2015 - ps - Update for data_time suffix for the Group Layer result.
# 7/2/2015 - ps - Added Transparency for "Point of Origin Results" group layer polygons.
# 7/2/2015 - ps - Added checks for layerSymLocation for post "Share as Template", or restored "Share Project Package"
# 7/3/2015 THIS RAN SUCCESSFULLY WITH THE MOD's mentioned.  Clean GDB's for scratch and results seem to be required if run multiple times.
# 7/6/2015 Added logic to check for Desktop, or Pro 1.0 in order to call cursor() properly for respective version.
# 7/8/2015 Review "locals", delete more locals.
# ---------------------------------------------------------------------------
# Have not added the renamining of Grouped layer with date_time suffix,
# Have not changed true curves to polygons

# ======================Import arcpy module=================================
import os, sys, traceback, math, decimal, time
#import arcpy
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

# Will use a time stamp on the grouped layer for keeping track of multiple runs; prefix should distinguish Feature Classes?
timestr = time.strftime("%Y%m%d_%H%M")


delete_me = []
#DEBUG = False
DEBUG = True
desktopVersion = ["10.2.2","10.3"]
proVersion = ["1.0", "1.1"]

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
            
    return
#------------------------------------------------------------------------------
if DEBUG == True:
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
        gisVersion = arcpy.GetInstallInfo()["Version"]
        if gisVersion in desktopVersion or gisVersion == "1.0":
            record = cursor.next() # this is method for Pro 1.0.2
        else:
            record = next(cursor) # Python 3 method - but only works in Pro 1.1
        minRange =  record.getValue(minRangeField)
        maxRange =  record.getValue(maxRangeField)
        if DEBUG == True:
            arcpy.AddMessage("Minimum Range: " + str(minRange))
            arcpy.AddMessage("Maximum Range: " + str(maxRange))
            
        del cursor, record

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
    # 2. Layers restored from Share "Project Template" - in folder at same level as script /project_loc/pointoforigindetection.py and /project_loc/layers)
    elif os.path.isdir(os.path.abspath(os.path.join(os.path.dirname(__file__), 'layers'))) and \
         os.path.isfile(os.path.abspath(os.path.join(os.path.dirname(__file__), 'layers', 'Impact_Point_Centers.lyrx'))):
        layerSymLocation = os.path.abspath(os.path.join(os.path.dirname(__file__), 'layers'))
    #
    # 3. Layers in root level of project at same level as script (i.e /project_loc/pointoforigindetection.py and /project_loc/PointOfOrigin.lyrx)
    elif os.path.isdir(os.path.abspath(os.path.join(os.path.dirname(__file__), ))) and \
         os.path.isfile(os.path.abspath(os.path.join(os.path.dirname(__file__), 'Impact_Point_Centers.lyrx'))):
        layerSymLocation = os.path.abspath(os.path.join(os.path.dirname(__file__),''))
    #
    # 4. commondata\userdata
    # Layers restored from Share as "New Project Package"  - location (i.e /project_loc/pointoforigindetection.py and /project_loc/commondata/userdata/PointOfOrigin.lyrx)
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
    if gisVersion in desktopVersion: #This is ArcGIS Desktkop 10.3 or 10.2.2
        mxd = None
        try:    # what if we are running this from ArcCatalog with no MXD?
            mxd = arcpy.mapping.MapDocument('CURRENT')
        except:  # if so, then just skip this part...
            arcpy.AddWarning("Tool is not run in ArcMap, skipping symbolization scheme.")
        else:   # otherwise lets add the stuff to our current data frame in our map.
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
    elif gisVersion in proVersion: #This Is  ArcGIS Pro  1.0.2 or 1.1
        arcpy.AddMessage("Working in ArcGIS Pro " + str(gisVersion))
        aprx = arcpy.mp.ArcGISProject(r"current")
        m = aprx.listMaps()[0]
        
        # make top group layer
        arcpy.AddMessage("Adding Top Group Layer...")
        groupLayerPath = os.path.join(layerSymLocation,"New_Group_Layer.lyrx")

        initialGroupLayer = arcpy.mp.LayerFile(groupLayerPath).listLayers()[0]
        initialGroupLayer.name = "Point Of Origin Results"
        m.addLayer(initialGroupLayer,"AUTO_ARRANGE")
        topGroupLayer = m.listLayers("Point Of Origin Results")[0]
        
               
        # Try to Add timestr to initialGroupLayer - has been hanging when using this, but not until "Adding Impact Points..." ?
        #igl_timestr = "Point Of Origin Results_" + timestr
        #initialGroupLayer.name = igl_timestr
        #m.addLayer(initialGroupLayer,"AUTO_ARRANGE")
        #topGroupLayer = m.listLayers(igl_timestr)[0]
              
        initialGroupLayer = None
        #del initialGroupLayer # this line hangs tool dialog.(this line is not used, but appears there is a typo "initialGroupayer" in original code?)
        
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
        #m.addLayerToGroup(topGroupLayer,impactPointLayer,"TOP")
        #if DEBUG == True: arcpy.AddMessage("impactPointLayer5")
        
        ipName = "Impact points"

        if DEBUG == True:
            arcpy.AddMessage("Check locals() at before MakeFeatureLayer ")
            mydict = dict(locals())
            CheckVariables(mydict)
        if DEBUG == True: arcpy.AddMessage("arcpy.MakeFeatureLayer(...) ** Hang's here **")
        
        results = arcpy.MakeFeatureLayer_management(outputImpactPointFeatures,ipName).getOutput(0)

        #  Applying symbology to result points before adding to Group works better than after adding to group
        if DEBUG == True: arcpy.AddMessage("ApplySymbologyFromLayer")
        arcpy.ApplySymbologyFromLayer_management(results,impactPointLayerFilePath) # for some reason this guy doesn't apply the symbology


        if DEBUG == True: arcpy.AddMessage("m.addLayerToGroup(...)")
        m.addLayerToGroup(topGroupLayer,results,"TOP")

##        if DEBUG == True: arcpy.AddMessage("ApplySymbologyFromLayer")
##        arcpy.ApplySymbologyFromLayer_management(results,impactPointLayerFilePath) # for some reason this guy doesn't apply the symbology
        
        # for all items in the combinedPooDict 
        for model in modelOriginsDict:
            arcpy.AddMessage("Adding model: " + str(model))
            
            # make a group layer for each model
            initialGroupLayer = arcpy.mp.LayerFile(groupLayerPath).listLayers()[0]
            initialGroupLayer.name = model
            m.addLayerToGroup(topGroupLayer,initialGroupLayer,"BOTTOM")
            modelGroupLayer = m.listLayers(model)[0]
            initialGroupLayer = None
            
            # get range and POO data from this model
            modelData = modelOriginsDict[model]
            
            # make layer for combined area and add to model layer
            combinedDict = modelData[1]
            combinedAreaLayer = arcpy.mp.LayerFile(os.path.join(layerSymLocation, "PointOfOrigin.lyrx")).listLayers()[0]
            combinedAreaLayer.dataSource = combinedDict["combined"]
            combinedAreaLayer.name = model + " Point Of Origin"
            m.addLayerToGroup(modelGroupLayer,combinedAreaLayer,"BOTTOM")
            
            initialGroupLayer = arcpy.mp.LayerFile(groupLayerPath).listLayers()[0]
            rangeLayerName = model + " Ranges by Impact OID"
            initialGroupLayer.name = rangeLayerName
            m.addLayerToGroup(modelGroupLayer,initialGroupLayer,"BOTTOM")
            rangeGroupLayer = m.listLayers(rangeLayerName)[0]
            initialGroupLayer = None
            
            # Add the individual ranges to the range group layer
            modelRanges = modelData[0]['ranges']
            for r in modelRanges:
                rangeToAdd = arcpy.mp.LayerFile(os.path.join(layerSymLocation, "ImpactRange.lyrx")).listLayers()[0]
                rangeToAdd.dataSource = r
                rangeToAdd.name = os.path.basename(r)
                m.addLayerToGroup(rangeGroupLayer,rangeToAdd,"BOTTOM")

            # Set Transparency of result Group Layers to "50"
            if modelGroupLayer.supports("TRANSPARENCY"):
                modelGroupLayer.transparency = 50
                
        del aprx, m
        
        
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

    
    # delete some local variables
    del results, initialGroupLayer, combinedDict, modelGroupLayer
    del ipName, outputImpactPointFeatures, outputImpactFeatures, outputPointsOfOriginFeatures

    # check which variables are still set...cleanup variables...
    if DEBUG == True:
        arcpy.AddMessage("Check locals at end script run ")
        mydict = dict(locals())
        CheckVariables(mydict)
##eof
