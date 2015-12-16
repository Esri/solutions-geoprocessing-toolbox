# -*- coding: utf-8 -*-
import arcpy
import mds
import mds.messages
import numpy

class GetVariableStatistics(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Get Variable Statistics"
        self.description = "Calculates statistics for a variable in a " + \
        "multidimensional dataset, such as netCDF or HDF. "
        self.canRunInBackground = False
        # Statistics choices
        statistics_numpy = {'MAXIMUM':'amax', \
                               'MEAN':'mean', \
                            'MINIMUM':'amin', \
                              'RANGE':'ptp', \
                                'STD':'std', \
                                'SUM':'sum', \
                           'VARIANCE':'var'}
        statistics_categorical = {'MEDIAN':'median', \
                                'MAJORITY':'majority', \
                                  'MINORITY':'minority', \
                                   'VARIETY':'variety'}
        # List of dictionaries of statistics
        # Sublist elements indices:
        #   0: object
        #   1: dictionary defined by 'displayname':'methodname'
        #       where object.methodname() is valid and displayname is what is
        #       shown to the user
        #   2: boolean, indicating whether the given dictionary of statistics
        #       only operates on integer datatypes
        self.statistics = [[numpy, statistics_numpy, False], \
                           [self, statistics_categorical, True]]
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


        # Derived output parameter
        parameters.append(arcpy.Parameter(
            displayName="Statistic",
            name="out_statistic",
            datatype="GPDouble",
            parameterType="Derived",
            direction="Output"))

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
        type_parameter = parameters[2]
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

        # Modify statistic choices based on variable type
        if (variable_parameter.value is not None) and (dataset is not None):
            if variable_parameter.valueAsText in dataset.variable_names():
                var = dataset.variable(variable_parameter.value)
                ispacked = hasattr(var,'scale_factor') or hasattr(var, 'add_offset')
                flag = ('int' in str(var.dtype)) and not ispacked
                type_parameter.filter.type = "ValueList"
                type_parameter.filter.list = sorted([key for stat in \
                    self.statistics if flag or not stat[2] for key in \
                    stat[1].keys()])

        return

    # ---------------------------------------------------------
    # Statistics

    def majority(self, var1):
        # Lowest value is returned in the case of ties.
        vunique = numpy.unique(var1)
        vcounts = numpy.zeros_like(vunique)
        for vindex in range(0, vunique.size):
            vcounts[vindex] = numpy.sum(var1 == vunique[vindex])
        return vunique[numpy.argmax(vcounts)]

    def minority(self, var1):
        # Lowest value is returned in the case of ties.
        vunique = numpy.unique(var1)
        vcounts = numpy.zeros_like(vunique)
        for vindex in range(0, vunique.size):
            vcounts[vindex] = numpy.sum(var1 == vunique[vindex])
        return vunique[numpy.argmax(vcounts)]

    def variety(self, var1):
        return numpy.unique(var1).size

    def calculate_statistic(self, variable, statistic):
        # Apply statistic
        for stat in self.statistics:
            if statistic in stat[1]:
                func = getattr(stat[0], stat[1][statistic])
                break
        else:
            # Default
            func = getattr(numpy, 'mean')
        return func(variable)

    # ---------------------------------------------------------

    def execute(self, parameters, messages):
        """The source code of the tool."""

        input_parameter = parameters[0]
        variable_parameter = parameters[1]
        type_parameter = parameters[2]

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

        # Perform statistic
        result1 = self.calculate_statistic(var1[:], type_parameter.valueAsText)

        # Format output string
        str_modif = "squared " if type_parameter.valueAsText == "VARIANCE" else ""
        str_units = str(var1.units) if hasattr(var1, 'units') else "units"
        str_output = "%s: %s %s%s" % (
            variable_parameter.valueAsText, str(result1), str_modif, str_units)

        # Output results
        arcpy.AddMessage(str_output)
        arcpy.SetParameter(3, result1)

        return