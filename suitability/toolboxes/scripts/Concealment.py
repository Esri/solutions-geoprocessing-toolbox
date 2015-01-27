#------------------------------------------------------------------------------
# Copyright 2015 Esri
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
# Concealment.py
#
#
#------------------------------------------------------------------------------
# 1/27/2015 - mf - Added Spatial Reference parameter and set as env.outputCoordinateSystem and added tool validation
#
#------------------------------------------------------------------------------



# IMPORTS ----------------------------------------------------------------
import os, sys, random, time, traceback
import arcpy
from arcpy import env

# ARGUMENTS --------------------------------------------------------------
input_AOI_Feature = arcpy.GetParameterAsText(0)
baseVegetation = arcpy.GetParameterAsText(1)
outConcealment = arcpy.GetParameterAsText(2)
commonSpatialReference = arcpy.GetParameter(3)
commonSpatialReferenceAsText = arcpy.GetParameterAsText(3)


# LOCALS -----------------------------------------------------------------
debug = False
deleteme = []
#
# VITD/FACC veg table
# {<key>:[<description>,<summer_suitability>,<winter_suitability>]}
# Suitability:
#   0:POOR
#   1:FAIR
#   2:GOOD
#

FACC_veg_tab = {"AL020":["Built-Up Area",2,2],
                "BH090":["Land subject to inundation",1,1],
                "BH095":["Marsh/Swamp",1,1],
                "BH135":["Rice Field",0,0],
                "DA020":["Barren Ground",0,0],
                "EA010":["Cropland",1,0],
                "EA020":["Hedgerow",0,0],
                "EA030":["Nursery",1,1],
                "EA031":["Botanical Garden",1,1],
                "EA040":["Orchard/Plantation",1,0],
                "EA050":["Vineyard",1,0],
                "EA055":["Hops",1,0],
                "EB010":["Grassland",0,0],
                "EB015":["Grass/Scrub/Brush",0,0],
                "EB020":["Scrub/Brush/Bush",1,0],
                "EB030":["Land Use/Land Cover (Vegetation)",1,1],
                "EC010":["Bamboo/Cane",2,2],
                "EC015":["Forest",2,0],
                "EC020":["Oasis",0,0],
                "EC030":["Trees",2,0],
                "EC040":["US-Cleared Way/Cut Line/Firebreak UK-Cleared Way/Firebreak",0,0],
                "ED010":["Marsh",1,0],
                "ED020":["Swamp",1,0],
                "EE000":["Miscellaneous Vegetation",1,1],
                "EE010":["Logging Area",0,0],
                "EE020":["Land devoid of vegetation",0,0],
                "AJ085":["Barn",2,2],
                "AM020":["Grain Bin/Silo",2,2],
                "AJ110":["Greenhouse",2,2],
                "AJ080":["Stable",2,2],
                "AK120":["Park",0,0],
                "AJ050":["Windmill",2,2],
                "AL170":["Plaza",1,1],
                "AK040":["Athletic Field",0,0],
                "AL030":["Cemetery",1,1],
                "AJ030":["Stockyard",1,1],
                "DA010":["Bare Ground",0,0],
                "AK100":["Golf Course",1,0],
                "AK170":["Swimming Pool",0,0],
                "AK160":["Stadium",2,2],
                "DB090":["Embankment",0,0],
                "AK060":["Campground",2,1],
                "AK164":["Unknown",0,0],
                "AK070":["Unknown",0,0],
                "AI021":["Unknown",0,0]}


try:
    if debug == True: arcpy.AddMessage("Begin: " + str(time.strftime("%m/%d/%Y  %H:%M:%S", time.localtime())))

    scratch = env.scratchWorkspace
    env.overwriteOutput = True

    installDir = arcpy.GetInstallInfo('desktop')["InstallDir"]
    prjWGS1984 = arcpy.SpatialReference("WGS 1984")
    
    if (commonSpatialReferenceAsText == ""):
        commonSpatialReference = arcpy.Describe(input_AOI_Feature).spatialReference
        arcpy.AddMessage("Using spatial reference of Input Area Of Interest: " + str(commonSpatialReference.name))
    env.outputSpatialReference = commonSpatialReference    
   
    newAOI = os.path.join(scratch,"newAOI")
    arcpy.Project_management(input_AOI_Feature,newAOI,commonSpatialReference)
    input_AOI_Feature = newAOI
    deleteme.append(newAOI)
    prjAOI = arcpy.Describe(input_AOI_Feature).SpatialReference

    # clip vegetation
    prjAOIveg = os.path.join(scratch,"AOIVeg")
    srVeg = arcpy.Describe(baseVegetation).SpatialReference
    arcpy.Project_management(input_AOI_Feature,prjAOIveg,srVeg)
    # clip veg (clip veg_poly from base_veg_poly using envelope)
    vegPoly = os.path.join(scratch,"vegPoly")
    arcpy.AddMessage("Clip veg polys to AOI...")
    arcpy.Clip_analysis(baseVegetation, prjAOIveg, vegPoly)

    # project clipped vegetation back to AOI SR
    if debug == True: arcpy.AddMessage("Projecting clipped veg back to AOI...")
    arcpy.Project_management(vegPoly,outConcealment,prjAOI)

    # remove unnecessary fields in veg
    keepFields = ["fcsubtype","f_code"]
    vegDesc = arcpy.Describe(outConcealment)
    keepFields.append(vegDesc.shapeFieldName)
    keepFields.append(vegDesc.OIDFieldName)
    # fields to keep:
    areaField = vegDesc.areaFieldName
    if areaField != "": keepFields.append(areaField)
    lengthField = vegDesc.lengthFieldName
    if lengthField != "": keepFields.append(lengthField)
    subtypeFieldName = vegDesc.subtypeFieldName
    if subtypeFieldName != "": keepFields.append(subtypeFieldName)

    for child in vegDesc.children:
        if child.datasetType == 'RepresentationClass':
            keepFields.append(child.overrideFieldName)
            keepFields.append(child.ruleIDFieldName)
    keepFields.append("F_CODE")

    # remove any unnecessary fields
    removeFields = []
    fields = arcpy.ListFields(outConcealment)
    for field in fields:
        if not (field.name in keepFields):
            #if debug == True: arcpy.AddMessage("removing " + str(field.name))
            #arcpy.DeleteField_management(outConcealment,field.name)
            removeFields.append(field.name)
    if debug == True: arcpy.AddMessage("Removing unnecessary fields...")
    arcpy.DeleteField_management(outConcealment,removeFields)

    # add suitibilty fields in veg
    if debug == True: arcpy.AddMessage("Adding concealment fields...")
    arcpy.AddField_management(outConcealment,"vegname","TEXT","","",70,"FACC_Vegetation_Type","NULLABLE","NON_REQUIRED")
    arcpy.AddField_management(outConcealment,"sumsuit","LONG",2,"","","Summer_Suitability","NULLABLE","NON_REQUIRED")
    arcpy.AddField_management(outConcealment,"winsuit","LONG",2,"","","Winter_Suitability","NULLABLE","NON_REQUIRED")

    # Add suitiblity values to fields
    arcpy.AddMessage("Updating rows...")
    rows = arcpy.UpdateCursor(outConcealment)
    for row in rows:
        f_code = row.F_CODE
        #if f_code in FACC_veg_tab.keys(): #UPDATE
        if f_code in list(FACC_veg_tab.keys()):
            vegtype = FACC_veg_tab[f_code][0]
            summer = FACC_veg_tab[f_code][1]
            winter = FACC_veg_tab[f_code][2]
            row.vegname = vegtype
            row.sumsuit = summer
            row.winsuit = winter
        rows.updateRow(row)

    # set output
    arcpy.SetParameterAsText(2,outConcealment)


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
    msgs = "ArcPy ERRORS:\n" + arcpy.GetMessages() + "\n"

    # Return python error messages for use in script tool or Python Window
    arcpy.AddError(pymsg)
    arcpy.AddError(msgs)

    # Print Python error messages for use in Python / Python Window
    #print pymsg + "\n" #UPDATE
    print(pymsg + "\n")
    #print msgs #UPDATE
    print(msgs)

finally:

    #### cleanup intermediate datasets
    arcpy.AddMessage("Removing intermediate datasets...")
    for i in deleteme:
        if debug == True: arcpy.AddMessage("Removing: " + str(i))
        arcpy.Delete_management(i)

    if debug == True: arcpy.AddMessage("END: " + str(time.strftime("%m/%d/%Y  %H:%M:%S", time.localtime())))
