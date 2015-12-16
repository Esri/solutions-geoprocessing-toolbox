# -*- coding: utf-8 -*-
import os.path
import mds
import mds.date_time
import mds.messages
import mds.netcdf.copy
import time
import netcdf_tool
import arcpy


class OPeNDAPtoNetCDF(netcdf_tool.NetCDFTool):

    @staticmethod
    def initialize_variables_list(
            variables_parameter,
            dataset):
        """
        Initialize *variables_parameter*, given *dataset*.

        This function updates the parameter's filter list.
        """
        if dataset is None:
            variables_parameter.filter.list = []
        else:
            variables_parameter.filter.list = list(
                dataset.data_variable_names())

    @staticmethod
    def update_variables_list(
            variables_parameter,
            dataset):
        """
        Update *variables_parameter*, given *dataset*.

        If the currently selected variables are all present in *dataset*, and
        only one of them is spatial, the filter is updated to only contain
        those data variables that are non-spatial or share the same spatial
        dimensions as the spatial variable currently selected. This prevents
        the user from selecting incompatible variables.

        In all other cases, the current list of selected variables is merged
        with the list of variables in *dataset* and used as the filter.
        """
        assert dataset
        selected_variable_names = mds.OrderedSet(variables_parameter.values)
        new_variable_names = dataset.data_variable_names()

        selected_variables_in_dataset = all([variable_name in new_variable_names
            for variable_name in selected_variable_names])
        one_spatial_variable_selected = selected_variables_in_dataset and \
            len([variable_name for variable_name in selected_variable_names \
                if dataset.is_spatial_variable(variable_name)]) == 1

        if selected_variables_in_dataset and one_spatial_variable_selected:
            filter_list = list(dataset.compatible_data_variable_names(
                iter(selected_variable_names).next()))
            assert len(filter_list) >= 1
        else:
            unknown_variable_names = selected_variable_names - \
                new_variable_names
            filter_list = list(unknown_variable_names | new_variable_names)

        variables_parameter.filter.list = filter_list

    @staticmethod
    def variables_are_compatible(
            variable_names,
            dataset):
        """
        Return whether *variable_names* are compatible.

        Variables are compatible if they share the same spatial dimensions or
        are non-spatial.
        """
        assert dataset
        assert len(variable_names) > 0
        assert all([variable_name in dataset.data_variable_names()
            for variable_name in variable_names])

        # Find name of first spatial variable.
        spatial_variable_name = next((variable_name for variable_name in
            variable_names if dataset.is_spatial_variable(variable_name)), None)

        if spatial_variable_name is not None:
            # Find out if the variable names passed in are all part of the list
            # of compatible data variable names of the spatial variable.
            compatible_data_variable_names = \
                dataset.compatible_data_variable_names(spatial_variable_name)
        else:
            # Find out if the variable names passed in are all part of the list
            # of compatible data variable names of the first variable.
            compatible_data_variable_names = \
                dataset.compatible_data_variable_names(
                    iter(variable_names).next())

        return all([variable_name in compatible_data_variable_names for
            variable_name in variable_names])

    @staticmethod
    def initialize_output_file(
            output_file_parameter,
            dataset_parameter):

        if dataset_parameter.value is None:
            output_file_parameter.value = None
        else:
            dataset_name = dataset_parameter.valueAsText
            filename = "{}.nc".format(os.path.splitext(os.path.basename(
                dataset_name))[0])
            output_file_parameter.value = os.path.join(
                OPeNDAPtoNetCDF.default_output_directory_name(dataset_name),
                    filename)

    @staticmethod
    def initialize_extent(
            extent_parameter,
            dataset,
            variables_parameter):
        if (dataset is not None) and \
                (len(dataset.spatial_data_variable_names()) == 0):
            # Current dataset doesn't contain spatial variables. Disable the
            # extent parameter.
            extent_parameter.value = None
            extent_parameter.enabled = False
        else:
            # Current dataset is not set yet, or it does contain at least one
            # spatial variable. It may not be selected, but the extent
            # parameter should be enabled.
            extent_parameter.enabled = True

            if dataset is None or variables_parameter.values is None:
                extent_parameter.value = None
            else:
                assert len(variables_parameter.values) > 0

                # Find name of first spatial variable.
                spatial_variable_name = next((variable_name for variable_name in
                    variables_parameter.values if variable_name in
                        dataset.data_variable_names() and
                            dataset.is_spatial_variable(variable_name)), None)

                if spatial_variable_name is None:
                    extent_parameter.value = None
                else:
                    # Pick the first variable selected to base the extent
                    # on. If all is well, the extent of all selected variables
                    # is the same.
                    extent = dataset.extent(spatial_variable_name)
                    extent_parameter.value = "{} {} {} {}".format(
                        extent[0], extent[1], extent[2], extent[3])

    @staticmethod
    def initialize_dimensions(
            dimensions_parameter,
            dataset,
            value_selection_method,
            variables_parameter):
        assert value_selection_method in ["BY_VALUE", "BY_INDEX"]
        if dataset is None or variables_parameter.values is None:
            dimensions_parameter.value = None
        else:
            assert len(variables_parameter.values) > 0

            dimension_names = mds.OrderedSet()
            for variable_name in variables_parameter.values:
                # People can pass anything, even names of variables that are
                # not in the dataset.
                if variable_name in dataset.variable_names():
                    dimension_names |= dataset.variable_dimension_names(
                        variable_name)
            dimension_names = mds.order(dimension_names,
                dataset.dimension_names())

            # Find name of first spatial variable.
            spatial_variable_name = next((variable_name for variable_name in
                variables_parameter.values if variable_name in
                    dataset.data_variable_names() and
                        dataset.is_spatial_variable(variable_name)), None)

            if spatial_variable_name is not None:
                space_dimension_names = dataset.space_dimension_names(
                    spatial_variable_name)
                dimension_names = dimension_names - space_dimension_names

            if len(dimension_names) == 0:
                dimensions_parameter.value = None
            else:
                # For each dimension, add a record to the table.
                values = []
                for dimension_name in dimension_names:
                    dimension = dataset.dimension(dimension_name)
                    if len(dimension) > 0:
                        first_index = 0
                        last_index = len(dimension) - 1
                        start_value = first_index
                        end_value = last_index

                        if dimension_name in dataset.variable_names() and \
                                value_selection_method == "BY_VALUE":
                            dimension_variable = dataset.variable(
                                dimension_name)
                            coordinates = dimension_variable[:]
                            start_value = coordinates[start_value]
                            end_value = coordinates[end_value]

                            if len(coordinates.shape) == 1:
                                if dataset.convention.is_time_dimension_variable(
                                        dimension_variable):
                                    start_value, end_value = \
                                        mds.netcdf.coordinates_to_dates([
                                            start_value, end_value],
                                            dimension_variable)
                                    start_value = mds.date_time.to_iso_format(
                                        start_value)
                                    end_value = mds.date_time.to_iso_format(
                                        end_value)

                        values.append([dimension_name, str(start_value),
                            str(end_value)])

                dimensions_parameter.values = values

    def __init__(self):
        self.label = "OPeNDAP to NetCDF"
        self.description = "The OPeNDAP to NetCDF tool will subset and " \
            "download data from web-based servers which support the OPeNDAP " \
            "protocol."
        # self.category =
        self.canRunInBackground = False
        # self.stylesheet =

    def isLicensed(self):
        return True;

    def getParameterInfo(self):
        # Parameter definitions
        parameters = []
        parameters.append(arcpy.Parameter(
            displayName="Input OPeNDAP Dataset",
            name="in_opendap_dataset",
            datatype="GPString",
            multiValue=False,
            parameterType="Required",
            direction="Input"))
        parameters.append(arcpy.Parameter(
            displayName="Variables",
            name="variable",
            datatype="GPString",
            multiValue=True,
            parameterType="Required",
            direction="Input"))
        parameters.append(arcpy.Parameter(
            displayName="Output netCDF File",
            name="out_netcdf_file",
            datatype="DEFile",
            multiValue=False,
            parameterType="Required",
            direction="Output"))
        parameters.append(arcpy.Parameter(
            displayName="Extent",
            name="extent",
            datatype="GPEnvelope",
            multiValue=False,
            parameterType="Optional",
            direction="Input"))
        parameters.append(arcpy.Parameter(
            displayName="Dimensions",
            name="dimension",
            datatype="GPValueTable",
            multiValue=True,
            parameterType="Optional",
            direction="Input"))
        parameters[-1].columns = [
            ["String", "Dimension"],
            ["String", "Start Value"],
            ["String", "End Value"]]
        parameters.append(arcpy.Parameter(
            displayName="Value Selection Method",
            name="value_selection_method",
            datatype="GPString",
            multiValue=False,
            parameterType="Optional",
            direction="Input"))
        parameters[-1].filter.list = ["BY_VALUE", "BY_INDEX"]

        return parameters

    def updateParameters(self,
            parameters):
        # Modify values and properties of parameters before internal validation
        # is performed. This method is called whenever a parameter has been
        # changed.
        class_ = self.__class__
        dataset_parameter = parameters[0]
        variables_parameter = parameters[1]
        output_file_parameter = parameters[2]
        extent_parameter = parameters[3]
        dimensions_parameter = parameters[4]
        value_selection_method_parameter = parameters[5]
        dataset = None

        # Try to open the dataset. Ignore errors.
        try:
            if not dataset_parameter is None:
                dataset = mds.netcdf.Dataset(dataset_parameter.valueAsText,
                    filter_out_nd_coordinates=True)
        except:
            pass

        for parameter in iter(parameters):
            assert not (class_.parameter_must_be_initialized(parameter,
                    dataset_parameter) and
                class_.parameter_must_be_updated(parameter,
                    dataset_parameter)), parameter.name

        # Variables.
        if class_.parameter_must_be_initialized(variables_parameter,
                dataset_parameter):
            class_.initialize_variables_list(variables_parameter, dataset)
        elif class_.parameter_must_be_updated(variables_parameter,
                dataset_parameter):
            if not dataset is None:
                class_.update_variables_list(variables_parameter, dataset)

        # Output file.
        if class_.parameter_must_be_initialized(output_file_parameter,
                dataset_parameter):
            class_.initialize_output_file(output_file_parameter,
                dataset_parameter)

        # Extent.
        if class_.parameter_must_be_initialized(extent_parameter,
                dataset_parameter):
            class_.initialize_extent(extent_parameter, dataset,
                variables_parameter)

        # Value selection method.
        # This one first, so we case use the value when initializing the
        # dimensions.
        if class_.parameter_must_be_initialized(
                value_selection_method_parameter, dataset_parameter):
            value_selection_method_parameter.value = "BY_VALUE"

        # Dimensions.
        if class_.parameter_must_be_initialized(dimensions_parameter,
                dataset_parameter):
            class_.initialize_dimensions(dimensions_parameter, dataset,
                value_selection_method_parameter.valueAsText,
                variables_parameter)

    def updateMessages(self,
            parameters):
        # Modify messages created by internal validation for each parameter.
        # This method is called after internal validation.
        class_ = self.__class__
        dataset_parameter = parameters[0]
        variables_parameter = parameters[1]
        output_file_parameter = parameters[2]
        extent_parameter = parameters[3]
        dimensions_parameter = parameters[4]
        value_selection_method_parameter = parameters[5]

        value_selection_method = mds.SELECT_BY_VALUE if \
            value_selection_method_parameter.valueAsText == "BY_VALUE" else \
                mds.SELECT_BY_INDEX

        dataset = None

        # Dataset.
        if not dataset_parameter.value is None:
            try:
                dataset = mds.netcdf.Dataset(dataset_parameter.valueAsText,
                    filter_out_nd_coordinates=True)
            except RuntimeError, exception:
                if "No such file or directory" in str(exception) or \
                        "Invalid argument" in str(exception):
                    class_.set_error(dataset_parameter,
                        mds.messages.INPUT_DATASET_DOES_NOT_RESOLVE_TO_FILENAME.format(
                            dataset_parameter.valueAsText))
                elif "Malformed or inaccessible DAP DDS" in str(exception):
                    class_.set_error(dataset_parameter,
                        mds.messages.INPUT_DATASET_URL_MALFORMED.format(
                            dataset_parameter.valueAsText))
                else:
                    class_.set_error(dataset_parameter,
                        mds.messages.INPUT_DATASET_GENERIC_ERROR.format(
                            dataset_parameter.valueAsText, str(exception)))
            except Exception, exception:
                class_.set_error(dataset_parameter,
                    mds.messages.INPUT_DATASET_GENERIC_ERROR.format(
                        dataset_parameter.valueAsText, str(exception)))

        # Variables.
        if variables_parameter.values is not None:
            if dataset is not None:
                variable_names_available = dataset.data_variable_names()
                variable_names_requested = mds.OrderedSet(
                    variables_parameter.values)
                unknown_variable_names = variable_names_requested - \
                    variable_names_available
                known_variable_names = variable_names_requested - \
                    unknown_variable_names

                if unknown_variable_names:
                    class_.set_warning(variables_parameter,
                        mds.messages.VARIABLES_DO_NOT_EXIST.format(", ".join(
                            unknown_variable_names), "Input OPeNDAP Dataset"))

                if len(known_variable_names) == 0:
                    class_.set_error(variables_parameter,
                        mds.messages.NONE_OF_VARIABLES_EXISTS)
                elif not class_.variables_are_compatible(
                        known_variable_names, dataset):
                    class_.set_error(variables_parameter,
                        mds.messages.VARIABLES_MUST_SHARE_DIMENSIONS)

                # Determine names of dimensions that are present in the
                # selected variables.
                dimension_names = set()
                for variable_name in known_variable_names:
                    variable = dataset.variable(variable_name)
                    for dimension_name in variable.dimensions:
                        dimension_names.add(dimension_name)

                for dimension_name in dimension_names:
                    if dimension_name in dataset.variable_names():
                        if len(dataset.variable(dimension_name)[:].shape) > 1:
                            class_.set_error(variables_parameter,
                                mds.messages.MULTIDIMENSIONAL_DIMENSIONS_NOT_SUPPORTED.format(
                                    dimension_name))
                            break

        # Output file.
        if output_file_parameter.value is not None:
            output_filename = output_file_parameter.valueAsText
            if os.path.splitext(output_filename)[1] != ".nc":
                class_.set_error(output_file_parameter,
                    mds.messages.OUTPUT_FILE_EXTENSION_MUST_BE_NC)

        # Dimensions.
        # Check whether the selected dimensions are present in the selected
        # variables.
        if dimensions_parameter.value is not None:
            if dataset is not None:
                if variables_parameter.values is not None:
                    # Determine names of dimensions that are present in the
                    # selected variables.
                    dimension_names = set()
                    for variable_name in variables_parameter.values:
                        if variable_name in dataset.dataset.variables:
                            variable = dataset.variable(variable_name)
                            for dimension_name in variable.dimensions:
                                dimension_names.add(dimension_name)

                    for dimension_record in dimensions_parameter.values:
                        # Test whether selected dimensions are present in the
                        # collection just filled.
                        dimension_name = dimension_record[0]
                        if dimension_name not in dimension_names:
                            class_.set_error(dimensions_parameter,
                                mds.messages.DIMENSION_NOT_PRESENT.format(
                                    dimension_record[0]))
                            break
                        elif dimension_name in dataset.variable_names():
                            if len(dataset.variable(dimension_name)[:].shape) > 1:
                                class_.set_error(dimensions_parameter,
                                    mds.messages.MULTIDIMENSIONAL_DIMENSIONS_NOT_SUPPORTED.format(
                                        dimension_name))
                                break

                            if value_selection_method == mds.SELECT_BY_VALUE \
                                    and dataset.convention.is_time_dimension_variable(
                                        dimension_name):
                                # Check format of temporal coordinates.
                                _, start_value, end_value = dimension_record
                                try:
                                    mds.date_time.from_iso_format(start_value)
                                    mds.date_time.from_iso_format(end_value)
                                except ValueError:
                                    class_.set_error(dimensions_parameter,
                                        mds.messages.INVALID_DATE_TIME)
                                    break
                            elif dataset.convention.is_space_dimension_variable(
                                    dimension_name):

                                class_.set_error(dimensions_parameter,
                                    mds.messages.SKIPPING_SPATIAL_DIMENSION)
                                break

    def execute(self,
            parameters,
            messages):
        dataset_name = parameters[0].valueAsText
        variable_names = mds.OrderedSet(parameters[1].values)
        output_filename = parameters[2].valueAsText

        extent = None
        if parameters[3].value is not None:
            extent = [float(value) for value in
                parameters[3].valueAsText.split(" ")]

        dimension_records = parameters[4].values
        value_selection_method = mds.SELECT_BY_VALUE if \
            parameters[5].valueAsText == "BY_VALUE" else mds.SELECT_BY_INDEX
        date_time_string = time.strftime("%m/%d/%Y %H:%M", time.localtime())
        history_message = mds.messages.OPENDAP_TO_NETCDF_HISTORY.format(
            date_time_string, dataset_name)

        try:
            dataset = mds.netcdf.Dataset(dataset_name,
                filter_out_nd_coordinates=True)

            # Get rid of the variable names that are not part of the dataset.
            known_variable_names = \
                variable_names & dataset.data_variable_names()
            assert len(known_variable_names) > 0  # See updateMessages.
            unknown_variable_names = variable_names - known_variable_names

            if unknown_variable_names:
                messages.addWarningMessage(
                    mds.messages.VARIABLES_DO_NOT_EXIST.format(", ".join(
                        unknown_variable_names), "Input OPeNDAP Dataset"))

            mds.netcdf.copy(dataset, known_variable_names, output_filename,
                extent, dimension_records, value_selection_method,
                history_message)
        except RuntimeError, exception:
            # Handle errors not detected by updateMessages.
            messages.addErrorMessage(str(exception))
            raise arcpy.ExecuteError
