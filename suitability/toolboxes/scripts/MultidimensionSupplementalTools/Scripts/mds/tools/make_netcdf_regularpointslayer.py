import arcpy

debug = False

class MakeNetCDFRegularPointsLayer(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Make NetCDF Regular Points Layer"
        self.description = "Makes a point feature layer from a netCDF file " \
        "which contains regularly spaced points."
        self.canRunInBackground = False
        return

    def getParameterInfo(self):
        """Define parameter definitions"""
        #Define parameter definitions

        # First parameter
        param0 = arcpy.Parameter(
            displayName="Input netCDF File",
            name="in_netcdf",
            datatype="File",
            parameterType="Required",
            direction="Input")

        # Second parameter
        param1 = arcpy.Parameter(
            displayName="Variables",
            name="in_variables",
            datatype="String",
            multiValue = True,
            parameterType="Required",
            direction="Input")

        # Third parameter
        param2 = arcpy.Parameter(
            displayName="Output Feature Layer",
            name="out_feature_layer",
            datatype="String",
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
        if parameters[0].value and arcpy.Exists(parameters[0].valueAsText):
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
            parameters[1].setErrorMessage("All selected variables must share " +
                "the same dimensions.")
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""

        # Describe the supplied netCDF File.
        ncFP = arcpy.NetCDFFileProperties(parameters[0].valueAsText)
        selectedVars = parameters[1].valueAsText.split(';')

        # Coordinate variables can be identified via values of their standard
        # name attribute or values of their untis attribute.

        XCoordNamesList = ["longitude", "projection_x_coordinate",
                            "grid_longitude"]
        YCoordNamesList = ["latitude", "projection_y_coordinate",
                           "grid_longitude"]
        XUnitNamesList = ["degrees_east", "degree_east", "degree_E",
                           "degrees_E", "degreeE", "degreesE" ]
        YUnitNamesList = ["degrees_north", "degree_north", "degree_N",
                              "degrees_N", "degreeN", "degreesN"]
        XAxisNameList = ["X"]
        YAxisNameList = ["Y"]

        # Case 1: Independent latitude, Longitude, Vertical and Time Axes
        # Get the dimensions associated with the first variable.  We can use a
        # single variable because tool validation guarentees that all the
        # selected variables have the same dimensions.
        dimNames = ncFP.getDimensionsByVariable(str(selectedVars[0]))
        x_variable = ""
        y_variable = ""
        for dimension in dimNames:
            # Per CF 1.6 (Chapter 5, preamble): "All of a variable's dimensions
            # that are latitude, longitude, vertical, or time dimensions must
            # have corresponding coordinate variables, i.e., one-dimensional
            # variables with the same name as the dimension."
            # Identify the coordinate variable by its standard name or units.

            try:
                SNattributeValue = ncFP.getAttributeValue(dimension,
                    "standard_name")
            except:
                SNattributeValue = "missing"

            try:
                UNattributeValue = ncFP.getAttributeValue(dimension, "units")
            except:
                UNattributeValue = "missing"

            try:
                AXattributeValue = ncFP.getAttributeValue(dimension,"axis")
            except:
                AXattributeValue = "missing"

            if SNattributeValue in XCoordNamesList:
                x_variable = dimension
            if SNattributeValue in YCoordNamesList:
                y_variable = dimension
            if UNattributeValue in XUnitNamesList:
                x_variable = dimension
            if UNattributeValue in YUnitNamesList:
                y_variable = dimension
            if AXattributeValue in XAxisNameList:
                x_variable = dimension
            if AXattributeValue in YAxisNameList:
                y_variable = dimension

        # Set the row dimensions parameter of the Make NetCDF Feature Layer tool
        # to the names of the latitude and longitude dimensions
        rowDimensions = ""
        rowDimensions = x_variable + ";" + y_variable


        # Case #2: 2 dimensional lat/long coordinate variable
        # If unsuccessful in locating variable for x and y coordinates based on
        # latitude and longitude, check to see if variable of interest is
        # georeferenced via a 2 dimensional lat/long coordinate variable

        # Coordinate Variable Method will only work if CDL conforms to the
        # CF 1.6 convention (section 2.4) that "All other dimensions should,
        # whenever possible, be placed to the left of the spatiotemporal
        # dimensions."

        if (not x_variable) or (not y_variable):
            try:
                coordAttributeValue = ncFP.getAttributeValue(str(selectedVars[0]),
                    "coordinates")
                coordVariables = coordAttributeValue.split(' ')
                for element in coordVariables:
                    try:
                        SNattributeValue = ncFP.getAttributeValue(element,
                            "standard_name")
                    except:
                        SNattributeValue = "missing"

                    try:
                        UNattributeValue = ncFP.getAttributeValue(element,
                            "units")
                    except:
                        UNattributeValue = "missing"

                    try:
                        AXattributeValue = ncFP.getAttributeValue(element,
                            "axis")
                    except:
                        AXattributeValue = "missing"

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

                # Set the row dimensions parameter of the Make NetCDF Feature
                # Layer tool to the names of the coordinate variables
                dimNames = ncFP.getDimensionsByVariable(str(selectedVars[0]))
                rowDimensions = str(dimNames[-1]) + ";" + str(dimNames[-2])


            except:
                CoordAttributeValue = "missing"

        # Convert the python list of selected variables into a single
        # (comma delimited string if necessary.
        if selectedVars.count > 1:
            variable_list = ','.join([str(x) for x in selectedVars])
        else:
            variable_list = selectedVars[0]

        if (x_variable) and (y_variable):
            if (debug):
                arcpy.AddWarning("netCDFFile Name: %s" \
                    % parameters[0].valueAsText)
                arcpy.AddWarning("Variable List: %s" % variable_list)
                arcpy.AddWarning("x_variable: %s" % x_variable)
                arcpy.AddWarning("y_variable: %s" % y_variable)
                arcpy.AddWarning("Output Feature Layer: %s " \
                    % parameters[2].valueAsText)
                arcpy.AddWarning("Row Dimensions: %s " % rowDimensions)

            result1 = arcpy.MakeNetCDFFeatureLayer_md(parameters[0].valueAsText,
                                            variable_list,
                                            x_variable,
                                            y_variable,
                                            parameters[2].value,
                                            rowDimensions)
            # Force the netCDF Feature Layer to be added to the display
            arcpy.SetParameter(3, result1)
        else:
            arcpy.AddError("Unable to automatically determine x and y " +
                "variables from the netCDF file. Use Make NetCDF " +
                "Feature Layer tool.")
        return
