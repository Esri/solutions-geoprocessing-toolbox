import arcpy

debug = False

class MakeNetCDFTrajectoryPointsLayer(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Make NetCDF Trajectory Points Layer"
        self.description = "Makes a feature layer from a netCDF file which " \
        "contains trajectory data (e.g. a flight or ship path)."
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        # First parameter
        param0 = arcpy.Parameter(
            displayName="Input netCDF File",
            name="in_netcdf",
            datatype="DEFile",
            parameterType="Required",
            direction="Input")

        # Second parameter
        param1 = arcpy.Parameter(
            displayName="Variables",
            name="in_variables",
            datatype="GPString",
            multiValue = True,
            parameterType="Required",
            direction="Input")

        # Third parameter
        param2 = arcpy.Parameter(
            displayName="Output Feature Layer",
            name="out_feature_layer",
            datatype="GPString",
            parameterType="Required",
            direction="Input")

        # Dummpy Parameter to Force Output NetCDF Layer to be added to the
        # display.
        param3 = arcpy.Parameter(
            displayName="Output Feature Layer",
            name="dummy_feature_layer",
            datatype="GPFeatureLayer",
            parameterType="Derived",
            direction="Output")

        params = [param0, param1, param2, param3]
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        # Create list of possible variables for second parameter.
        if parameters[0].value:
            ncFP = arcpy.NetCDFFileProperties(parameters[0].valueAsText)
            parameters[1].filter.list = ncFP.getVariables()
        # Populate the output layer name parameter with a reasonable default
        # (i.e. the name of the first variable chosen with _layer appended
        # to it.)
        if parameters[1].value and not parameters[2].altered:
            variable_name_list = str(parameters[1].valueAsText).split(';')
            out_layer_name = variable_name_list[0] + "_Layer"
        # Generate a unique layer name
            i = 1
            temp_name = out_layer_name
            while arcpy.Exists(temp_name):
                temp_name = out_layer_name + str(i)
                i += 1
            out_layer_name = temp_name
            parameters[2].value = out_layer_name

        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
    # Multivalue parameter 1 contains variable names. Split them into a list.
        selectedVars = []
        if parameters[1].value:
            ncFP = arcpy.NetCDFFileProperties(parameters[0].valueAsText)
            selectedVars = []
            selectedVars = str(parameters[1].valueAsText).split(';')

        # For each selected variable, get its dimension.  Build a list
        dimList = []
        [dimList.append(ncFP.getDimensionsByVariable(v.replace("'", ""))) \
            for v in selectedVars]

        # Verify the all variables have the same exact dimensions
        if not all(x == dimList[0] for x in dimList):
            msg1 = "All selected variables must share the same dimensions."
            parameters[1].setErrorMessage(msg1)

        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        # Describe the supplied netCDF File.
        ncFP = arcpy.NetCDFFileProperties(parameters[0].valueAsText)
        selectedVars = parameters[1].valueAsText.split(';')

        # Coordinate variables can be identified via values of their standard
        # name attribute or values of their untis attribute.

        XCoordNamesList = ["longitude","projection_x_coordinate",
                            "grid_longitude"]
        YCoordNamesList = ["latitude","projection_y_coordinate",
                           "grid_longitude"]
        XUnitNamesList = ["degrees_east", "degree_east", "degree_E",
                           "degrees_E", "degreeE", "degreesE" ]
        YUnitNamesList = ["degrees_north","degree_north","degree_N",
                              "degrees_N","degreeN","degreesN"]
        XAxisNameList = ["X"]
        YAxisNameList = ["Y"]


        # Case #1: Trajectory variable can be identified under two conditions;
        # the presence of a attribute name of 'positive' on a variable or
        # the presence of the units variable with a units of pressure (pascal).

        x_variable = ''
        y_variable = ''
        ZVariable = ''

        if (not x_variable) or (not y_variable):
            try:
                coordAttributeValue = ncFP.getAttributeValue(str(selectedVars[0]),
                    "coordinates")
                coordVariables = coordAttributeValue.split(' ')
                for element in coordVariables:
                    try:
                        ZAttribute = ncFP.getAttributeValue(element,
                        "positive")
                        if ZAttribute.upper() == 'UP' or ZAttribute.upper() \
                        == 'DOWN':
                            ZVariable = element
                    except:
                        pass

                    try: SNattributeValue = ncFP.getAttributeValue(element,
                        "standard_name")
                    except: SNattributeValue = "missing"

                    try:
                        UNattributeValue = ncFP.getAttributeValue(element,
                        "units")
                        if UNattributeValue.upper() == 'PASCAL':
                            ZVariable = element
                    except:
                        UNattributeValue = "missing"

                    try: AXattributeValue = ncFP.getAttributeValue(element,
                        "axis")
                    except: AXattributeValue = "missing"

                    if SNattributeValue in XCoordNamesList:
                        x_variable = element
                    if SNattributeValue in YCoordNamesList:
                        y_variable = element
                    if UNattributeValue in XUnitNamesList:
                        x_variable = element
                    if UNattributeValue in YUnitNamesList:
                        y_variable = element
                    if AXattributeValue in XAxisNameList:
                        x_variable = element
                    if AXattributeValue in YAxisNameList:
                        y_variable = element

            except:
                CoordAttributeValue = "missing"

        # Convert the python list of selected variable into a single
        # (comma delimited) string if necessary.

        if selectedVars.count > 1:
            variable_list = ','.join([str(x) for x in selectedVars])
        else:
            variable_list = selectedVars[0]

        # Set the row dimensions parameter of the Make NetCDF Feature Layer tool
        # to the trajectory dimension name.

        try:
            dimNames = ncFP.getDimensionsByVariable(selectedVars[0])
            row_dimension = str(dimNames[-1])
        except:
            row_dimension = ""

        if (x_variable) and (y_variable) and (row_dimension):
            if (debug):
                arcpy.AddWarning("netCDFFile Name: %s" % \
                    parameters[0].valueAsText)
                arcpy.AddWarning("Variable List: %s" % variable_list)
                arcpy.AddWarning("x_variable: %s" % x_variable)
                arcpy.AddWarning("y_variable: %s" % y_variable)
                arcpy.AddWarning("Output Feature Layer: %s " % \
                    parameters[2].valueAsText)
                arcpy.AddWarning("Row Dimensions: %s " % row_dimension)
                arcpy.AddWarning("Z Variable: %s " % ZVariable)

            result1 = arcpy.MakeNetCDFFeatureLayer_md(parameters[0].valueAsText,
                                            variable_list,
                                            x_variable,
                                            y_variable,
                                            parameters[2].valueAsText,
                                            row_dimension,
                                            ZVariable)

            # Force the netCDF Feature Layer to be added to the display
            arcpy.SetParameter(3,result1)
        else:
            if (not x_variable) or (not y_variable):
                msg1 = "Unable to automatically determine x and y variables " \
                   + "from the netCDF file. Use Make NetCDF Feature Layer tool."
                arcpy.AddError(msg1)
            if (not row_dimension):
                msg1 = "Unable to automatically determine row dimension " \
                     + "variable(s) from the netCDF file. Use Make NetCDF " \
                    + "Feature Layer tool."
                arcpy.AddError(msg1)
        return
