import arcpy
import os
thisFolder = os.path.dirname(__file__)
scriptFolder = os.path.join(thisFolder, r"scripts")
sys.path.append(scriptFolder)
import ERG
#reload(ERG)


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        self.label = "ERG Tools"
        self.alias = "erg"

        # List of tool classes associated with this toolbox
        self.tools = [ERGByChemical, ERGByPlacard]


class ERGByChemical(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)"""
        self.label = "ERG By Chemical"
        self.description = "Generates 2 feature classes (polygon and polyline) that together describe the action zones defined by ERG, based on the chemical name supplied"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""

        # First parameter
        param0 = arcpy.Parameter(
            displayName="Incident Point",
            name="in_features",
            datatype="GPFeatureRecordSetLayer",
            parameterType="Required",
            direction="Input")

        # get the symbology / schema for the point from the layer file
        param0.value = os.path.join(thisFolder, r"layers\Incident Point.lyr")
        
        # Second parameter
        param1 = arcpy.Parameter(
            displayName="Material Type",
            name="material_type",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        # grab the list of materials from a dbf file
        dbfFile = os.path.join(thisFolder, r"tooldata\ERG2016LookupTable.dbf")
        expression = arcpy.AddFieldDelimiters(dbfFile, 'IDNum') + ' > 0 AND NOT ' + arcpy.AddFieldDelimiters(dbfFile, 'BLEVE') + ' = \'Yes\''
        matList = [row[0] for row in arcpy.da.SearchCursor(dbfFile, ["Material"], where_clause=expression)]
        param1.filter.type = "ValueList"
        param1.filter.list = sorted(set(matList))

        if len(matList) > 0:
            param1.value = matList[0]
        
        # Third parameter
        param2 = arcpy.Parameter(
            displayName="Wind Bearing (direction blowing to, 0 - 360)",
            name="wind_bearing",
            datatype="GPLong",
            parameterType="Required",
            direction="Input")

        param2.filter.type = "Range"
        param2.filter.list = [0, 360]
        param2.value = 0

        # Fourth parameter
        param3 = arcpy.Parameter(
            displayName="Day or Night incident",
            name="time_of_day",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        param3.filter.type = "ValueList"
        param3.filter.list = ["Day", "Night"]
        param3.value = "Day"
        
        # Fifth parameter
        param4 = arcpy.Parameter(
            displayName="Large or Small spill",
            name="spill_size",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        param4.filter.type = "ValueList"
        param4.filter.list = ["Large", "Small"]
        param4.value = "Large"
        
        # Sixth parameter
        param5 = arcpy.Parameter(
            displayName="Output Area Features",
            name="output_areas",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Output")
        
        param5.value = arcpy.CreateScratchName("ERGByChemicalAreas", "", "FeatureClass", arcpy.env.scratchGDB)

        # Define the schema
        templateLoc = os.path.join(thisFolder, r"tooldata\Templates.gdb")
        
        d1 = arcpy.Describe(templateLoc + "\\ERGAreas")
        param5.schema.featureTypeRule = "AsSpecified"
        param5.schema.featureType = "Simple"
        param5.schema.geometryTypeRule = "AsSpecified"
        param5.schema.geometryType = "Polygon"
        param5.schema.additionalFields = d1.fields

        # set the symbology for the areas from the layer file
        param5.symbology = os.path.join(thisFolder, r"layers\ERGareas.lyr")

        # Seventh parameter
        param6 = arcpy.Parameter(
            displayName="Output Line Features",
            name="output_lines",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Output")

        param6.value = arcpy.CreateScratchName("ERGByChemicalLines", "", "FeatureClass", arcpy.env.scratchGDB)

        # Define the schema
        d2 = arcpy.Describe(templateLoc + "\\ERGLines")
        param6.schema.featureTypeRule = "AsSpecified"
        param6.schema.featureType = "Simple"
        param6.schema.geometryTypeRule = "AsSpecified"
        param6.schema.geometryType = "Polyline"
        param6.schema.additionalFields = d2.fields
        
       # set the symbology for the lines from the layer file
        param6.symbology = os.path.join(thisFolder, r"layers\ERGlines.lyr")

        params = [param0, param1, param2, param3, param4, param5, param6]

        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        # Ensure the given feature class names are valid
        if (parameters[5].value):
            fcName5 = os.path.basename(parameters[5].valueAsText)
            if (fcName5.lower() != (arcpy.ValidateTableName(fcName5)).lower()):
                parameters[5].setErrorMessage("Invalid Feature Class Name!")
        if (parameters[6].value):
            fcName6 = os.path.basename(parameters[6].valueAsText)
            if (fcName6.lower() != (arcpy.ValidateTableName(fcName6)).lower()):
                parameters[6].setErrorMessage("Invalid Feature Class Name!")
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        # Get the paths to the ERG lookup file and the Template location
        ergDbf = os.path.join(thisFolder, r"tooldata\ERG2016LookupTable.dbf")
        templateLoc = os.path.join(thisFolder, r"tooldata\Templates.gdb")

        # Ensure the point of spill is in a projected coord system
        spillPoint = ERG.GetProjectedPoint(parameters[0].valueAsText)
        if (spillPoint == None):
            arcpy.AddError("NO SPILL POINT! This tool requires a spill point to be supplied")
            return
        
        # Look up the ERG for the relevant distances, given the input parameters
        iid, pad, materials, guidenum = ERG.LookUpERG(parameters[1].valueAsText, "", parameters[4].valueAsText, parameters[3].valueAsText, ergDbf)
        if (iid == 0 or pad == 0):
            arcpy.AddWarning("The Initial Isolation Distance and/or the Protective Action Distance is zero. " + \
                    "Output features will not be created. The selected material may be from Table 3 " + \
                    "of the Emergency Response Guidebook, which is currently not supported.")
            return
            
        # Generate the output FCs and output them
        ERG.MakeERGFeatures(spillPoint, parameters[2].valueAsText, iid, pad, materials, guidenum, parameters[4].valueAsText,
                            parameters[3].valueAsText, parameters[5].valueAsText, parameters[6].valueAsText, templateLoc)
                
        return

class ERGByPlacard(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "ERG By Placard"
        self.description = "Generates 2 feature classes (polygon and polyline) that together describe the action zones defined by the ERG, based on the placard ID supplied"
        self.canRunInBackground = False        

    def getParameterInfo(self):
        """Define parameter definitions"""

        # First parameter
        param0 = arcpy.Parameter(
            displayName="Incident Point",
            name="in_features",
            datatype="GPFeatureRecordSetLayer",
            parameterType="Required",
            direction="Input")

        # get the symbology / schema for the point from the layer file
        param0.value = os.path.join(thisFolder, r"layers\Incident Point.lyr")
        
        # Second parameter
        param1 = arcpy.Parameter(
            displayName="Placard ID",
            name="placard_id",
            datatype="GPString",
            parameterType="Required",
            direction="Input")
        
        # grab the list of materials from a dbf file
        dbfFile = os.path.join(thisFolder, r"tooldata\ERG2016LookupTable.dbf")
        expression = arcpy.AddFieldDelimiters(dbfFile, 'IDNum') + ' > 0 AND NOT ' + arcpy.AddFieldDelimiters(dbfFile, 'BLEVE') + ' = \'Yes\''
        placList = [row[0] for row in arcpy.da.SearchCursor(dbfFile, ["IDNum"], where_clause=expression)]
        param1.filter.type = "ValueList"
        param1.filter.list = sorted(set(placList))

        if len(placList) > 0:
            param1.value = placList[0]

        # Third parameter
        param2 = arcpy.Parameter(
            displayName="Wind Bearing (direction blowing to, 0 - 360)",
            name="wind_bearing",
            datatype="GPLong",
            parameterType="Required",
            direction="Input")

        param2.filter.type = "Range"
        param2.filter.list = [0, 360]
        param2.value = 0

        # Fourth parameter
        param3 = arcpy.Parameter(
            displayName="Day or Night incident",
            name="time_of_day",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        param3.filter.type = "ValueList"
        param3.filter.list = ["Day", "Night"]
        param3.value = "Day"
        
        # Fifth parameter
        param4 = arcpy.Parameter(
            displayName="Large or Small spill",
            name="spill_size",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        param4.filter.type = "ValueList"
        param4.filter.list = ["Large", "Small"]
        param4.value = "Large"
        
        # Sixth parameter
        param5 = arcpy.Parameter(
            displayName="Output Area Features",
            name="output_areas",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Output")
        
        param5.value = arcpy.CreateScratchName("ERGByPlacardAreas", "", "FeatureClass", arcpy.env.scratchGDB)

        # Define the schema
        templateLoc = os.path.join(thisFolder, r"tooldata\Templates.gdb")
        
        d1 = arcpy.Describe(templateLoc + "\\ERGAreas")
        param5.schema.featureTypeRule = "AsSpecified"
        param5.schema.featureType = "Simple"
        param5.schema.geometryTypeRule = "AsSpecified"
        param5.schema.geometryType = "Polygon"
        param5.schema.additionalFields = d1.fields

        # set the symbology for the areas from the layer file
        param5.symbology = os.path.join(thisFolder, r"layers\ERGareas.lyr")

        # Seventh parameter
        param6 = arcpy.Parameter(
            displayName="Output Line Features",
            name="output_lines",
            datatype="DEFeatureClass",
            parameterType="Required",
            direction="Output")

        param6.value = arcpy.CreateScratchName("ERGByPlacardLines", "", "FeatureClass", arcpy.env.scratchGDB)

        # Define the schema
        d2 = arcpy.Describe(templateLoc + "\\ERGLines")
        param6.schema.featureTypeRule = "AsSpecified"
        param6.schema.featureType = "Simple"
        param6.schema.geometryTypeRule = "AsSpecified"
        param6.schema.geometryType = "Polyline"
        param6.schema.additionalFields = d2.fields
        
       # set the symbology for the lines from the layer file
        param6.symbology = os.path.join(thisFolder, r"layers\ERGlines.lyr")

        params = [param0, param1, param2, param3, param4, param5, param6]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""

        # Ensure the given feature class names are valid
        if (parameters[5].value):
            fcName5 = os.path.basename(str(parameters[5].value))
            if (fcName5.lower() != (arcpy.ValidateTableName(fcName5)).lower()):
                parameters[5].setErrorMessage("Invalid Feature Class Name!")
        if (parameters[6].value):
            fcName6 = os.path.basename(str(parameters[6].value))
            if (fcName6.lower() != (arcpy.ValidateTableName(fcName6)).lower()):
                parameters[6].setErrorMessage("Invalid Feature Class Name!")
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        # Get the paths to the ERG lookup file and the Template location
        ergDbf = os.path.join(thisFolder, r"tooldata\ERG2016LookupTable.dbf")
        templateLoc = os.path.join(thisFolder, r"tooldata\Templates.gdb")

        # Ensure the point of spill is in a projected coord system
        spillPoint = ERG.GetProjectedPoint(parameters[0].valueAsText)
        if (spillPoint == None):
            arcpy.AddError("NO SPILL POINT! This tool requires a spill point to be supplied")
            return
        
        # Look up the ERG for the relevant distances, given the input parameters
        iid, pad, materials, guidenum = ERG.LookUpERG("", parameters[1].valueAsText, parameters[4].valueAsText, parameters[3].valueAsText, ergDbf)
        if (iid == 0 or pad == 0):
            arcpy.AddWarning("The Initial Isolation Distance and/or the Protective Action Distance is zero. " + \
                    "Output features will not be created. The selected material may be from Table 3 " + \
                    "of the Emergency Response Guidebook, which is currently not supported.")
            return
        
        # Generate the output FCs and output them
        ERG.MakeERGFeatures(spillPoint, parameters[2].valueAsText, iid, pad, materials, guidenum, parameters[4].valueAsText,
                            parameters[3].valueAsText, parameters[5].valueAsText, parameters[6].valueAsText, templateLoc)
        
        return
    