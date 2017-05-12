# -*- coding: utf-8 -*-
import arcpy
import mds
import mds.messages
import numpy
import netCDF4
import os.path
#
# LIMITATIONS:
#   > Attributes:
#   Attribute values are copied wholesale from the original variable.  Hence,
#   if these values describe the the values in the new variable, i.e. as with
#   valid_range, actual_range, unpacked_range, they will be incorrect and should
#   be manually altered.  This affects all statistics types, but is only
#   problematic with the RANGE, STD, SUM, and VARIANCE.
#
class GetVariableStatisticsOverDimension(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Get Variable Statistics Over Dimension"
        self.description = "Calculates statistics for a variable in a " + \
        "multidimensional dataset, such as netCDF or HDF, over a specified" + \
        "dimension. "
        self.canRunInBackground = False
        # Statistics choices
        statistics_numpy = {'MAXIMUM':'max', \
                               'MEAN':'mean', \
                            'MINIMUM':'min', \
                              'RANGE':'ptp', \
                                'STD':'std', \
                                'SUM':'sum', \
                           'VARIANCE':'var'}
        # List of dictionaries of statistics
        # Sublist elements indices:
        #   0: object
        #   1: dictionary defined by 'displayname':'methodname'
        #       where object.methodname() is valid and displayname is what is
        #       shown to the user
        self.statistics = [[numpy.ma, statistics_numpy]]
        self.default_statistic = "MEAN"

    def getParameterInfo(self):
        """Define parameter definitions"""

        parameters = []

        # Input parameter
        parameters.append(arcpy.Parameter(
            displayName="Input File or URL String",
            name="in_file",
            datatype=["DEFile","GPString"],
            parameterType="Required",
            direction="Input"))

        # Variable parameter
        parameters.append(arcpy.Parameter(
            displayName="Variable",
            name="variable",
            datatype="GPString",
            parameterType="Required",
            direction="Input"))

        parameters[-1].parameterDependencies = [parameters[-2].name]

        # Dimension parameter
        parameters.append(arcpy.Parameter(
            displayName="Dimension",
            name="dimension",
            datatype="GPString",
            parameterType="Required",
            direction="Input"))

        parameters[-1].parameterDependencies = [parameters[-2].name]

        # Output parameter
        parameters.append(arcpy.Parameter(
            displayName="Output netCDF File",
            name="out_netcdf_file",
            datatype="DEFile",
            multiValue=False,
            parameterType="Required",
            direction="Output"))

        # Output variable parameter
        parameters.append(arcpy.Parameter(
            displayName="Output Variable Name",
            name="out_variable",
            datatype="GPString",
            multiValue=False,
            parameterType="Optional",
            direction="Output"))

        # Type parameter
        parameters.append(arcpy.Parameter(
            displayName="Statistic Type",
            name="statistic_type",
            datatype="GPString",
            parameterType="Optional",
            direction="Input"))

        parameters[-1].filter.type = "ValueList"
        parameters[-1].filter.list = sorted([key for stat in \
            self.statistics for key in stat[1].keys()])
        parameters[-1].value = self.default_statistic

        return parameters

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

        input_parameter = parameters[0]
        variable_parameter = parameters[1]
        dimension_parameter = parameters[2]
        output_parameter = parameters[3]
        output_var_parameter = parameters[4]
        type_parameter = parameters[5]
        dataset = None

        # Open dataset and populate variable names
        if input_parameter.value is not None:
            try:
                dataset = mds.netcdf.Dataset(input_parameter.valueAsText, '')
            except RuntimeError, exception:
                if "No such file or directory" in str(exception) or \
                    "Invalid argument" in str(exception):
                    input_parameter.setErrorMessage(
                        mds.messages.INPUT_DATASET_DOES_NOT_RESOLVE_TO_FILENAME.format(
                            input_parameter.valueAsText))
                elif "Malformed or inaccessible DAP DDS" in str(exception):
                    input_parameter.setErrorMessage(
                        mds.messages.INPUT_DATASET_URL_MALFORMED.format(
                            input_parameter.valueAsText))
                else:
                    input_parameter.setErrorMessage(
                        mds.messages.INPUT_DATASET_GENERIC_ERROR.format(
                            input_parameter.valueAsText, str(exception)))
            except Exception, exception:
                input_parameter.setErrorMessage(
                    mds.messages.INPUT_DATASET_GENERIC_ERROR.format(
                        input_parameter.valueAsText, str(exception)))
            if dataset is not None:
                # Fill variable list
                variable_parameter.filter.type = "ValueList"
                variable_parameter.filter.list = list(dataset.variable_names())
        else:
            # Clear variable list if no input specified
            variable_parameter.filter.type = "ValueList"
            variable_parameter.filter.list = []
            variable_parameter.value = ""
            # Clear dimension list if no input specified
            dimension_parameter.filter.type = "ValueList"
            dimension_parameter.filter.list = []
            dimension_parameter.value = ""

        # Update dimension list
        if (variable_parameter.value is not None) and (dataset is not None):
            # Fill dimensions list
            dimension_parameter.filter.type = "ValueList"
            dimension_parameter.filter.list = list(
                dataset.variable_dimension_names(variable_parameter.valueAsText))
        else:
            # Clear dimension list if no input specified
            dimension_parameter.filter.type = "ValueList"
            dimension_parameter.filter.list = []
            dimension_parameter.value = ""

        # Ensure an output variable name is entered
        if (output_var_parameter.altered) and (output_var_parameter.value is None):
            output_var_parameter.setErrorMessage(
                '%s: Must input a variable name.' % output_var_parameter.name)

        # Ensure output variable name is not the same as an existing variable's
        if (output_var_parameter.value is not None) and \
            (dataset is not None) and (output_var_parameter.value in \
            dataset.variable_names()):
            output_var_parameter.setErrorMessage(
                '%s: Name cannot be the same as that of an existing variable.' \
                % output_var_parameter.name)

        # Populate a default output variable name and update it with changes
        #   to other parameters as long as the user hasn't modified it themself
        if (variable_parameter.value is not None) and \
            (dimension_parameter.value is not None) and \
            (not output_var_parameter.altered):
            if type_parameter.value is None:
                output_var_parameter.value = variable_parameter.value + \
                    "_MEAN" + dimension_parameter.value
            else:
                output_var_parameter.value = variable_parameter.value + \
                    "_" + type_parameter.value + dimension_parameter.value

        # Ensure output file has a .nc extension
        if output_parameter.value is not None:
            output_filename = output_parameter.valueAsText
            if os.path.splitext(output_filename)[1] != ".nc":
                output_parameter.setErrorMessage(
                    mds.messages.OUTPUT_FILE_EXTENSION_MUST_BE_NC)

        return

    # ---------------------------------------------------------
    # Statistics

    def calculate_statistic(self, variable, dimension, statistic):
        # Apply statistic
        for stat in self.statistics:
            if statistic in stat[1]:
                func = getattr(stat[0], stat[1][statistic])
                break
        else:
            # Default
            func = getattr(numpy.ma, 'mean')
        return func(variable, axis=dimension)

    # ---------------------------------------------------------

    def execute(self, parameters, messages):
        """The source code of the tool."""

        input_parameter = parameters[0]
        variable_parameter = parameters[1]
        dimension_parameter = parameters[2]
        output_parameter = parameters[3]
        output_var_parameter = parameters[4]
        type_parameter = parameters[5]

        dataset_name = input_parameter.valueAsText

        # Open dataset
        try:
            dataset = mds.netcdf.Dataset(dataset_name,'')
        except RuntimeError, exception:
            # Handle errors not detected by updateMessages.
            messages.addErrorMessage(str(exception))
            raise arcpy.ExecuteError

        # Variable of interest
        var1 = dataset.variable(variable_parameter.valueAsText)

        # Dimension of interest
        dim1 = var1.dimensions.index(dimension_parameter.valueAsText)

        # Perform statistic
        result1 = self.calculate_statistic(var1[:], dim1, \
            type_parameter.valueAsText)

        # Collect output dataset information
        output_dims = list(dataset.variable_dimension_names(
            variable_parameter.valueAsText))
        output_dims.remove(dimension_parameter.valueAsText)
        output_dims = tuple(output_dims)
        output_filename = output_parameter.valueAsText
        output_name = output_var_parameter.valueAsText

        # Create new dataset
        dataset.xcopy(dataset.data_variable_names(), output_filename)

        # Create new variable in dataset
        with netCDF4.Dataset(output_filename, mode="a") as newdataset:
            newvar = newdataset.createVariable(output_name, var1.dtype, \
                output_dims)
            for attribute_name in var1.ncattrs():
                newvar.setncattr(attribute_name, var1.getncattr(attribute_name))
            newvar[:] = result1

        # Output new variable name
        arcpy.SetParameter(5, output_name)

        return