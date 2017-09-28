# -*- coding: utf-8 -*-
import netCDF4
import mds.constants
# import mds.date_time
import mds.ordered_set
import mds.math
import mds.netcdf.convention


class Dataset(object):
    """
    Constructs an instance based on a *name* and an optional default
    *favor_convention_class*

    filter_out_nd_coordinates
        See :py:func:`mds.netcdf.convention.select_convention`.

    favor_convention_class
        See :py:func:`mds.netcdf.convention.select_convention`.

    This class is implemented using `netCDF4.Dataset <http://netcdf4-python.googlecode.com/svn/trunk/docs/netCDF4.Dataset-class.html>`_ from the
    `netcdf4-python package <https://code.google.com/p/netcdf4-python/>`_.
    If you need functionality that isn't available in this class' interface,
    then you can use the layered *dataset* instance::

       dimensions = dataset.dataset.dimensions
    """

    def __init__(self,
            name,
            filter_out_nd_coordinates,
            favor_convention_class=None):
        self.name = name
        self.dataset = netCDF4.Dataset(filename=self.name, mode="r")
        self.convention = mds.netcdf.convention.select_convention(
            self.dataset, filter_out_nd_coordinates,
            favor_class=favor_convention_class if favor_convention_class
                is not None else mds.netcdf.convention.CF)

        if self.convention is None:
            raise RuntimeError("Convention rules are not implemented")

    def __del__(self):
        if hasattr(self, "dataset"):
            self.dataset.close()

    # Revamp when necessary.
    # def __enter__(self):
    #     print "enter!"

    # def __exit__(self, exc_type, exc_val, exc_tb):
    #     print "exit!"
    #     if hasattr(self, "dataset"):
    #         self.dataset.close()
    #     return False

    def attribute_names(self):
        """
        OrderedSet of names of global attributes in the dataset.
        """
        return mds.ordered_set.OrderedSet(self.dataset.ncattrs())

    def attribute(self,
            attribute_name):
        """
        Return attribute with name *attribute_name*.
        """
        assert attribute_name in self.attribute_names(), attribute_name
        return getattr(self.dataset, attribute_name)

    def dimension_names(self):
        """
        OrderedSet of names of dimensions in the dataset.
        """
        return mds.ordered_set.OrderedSet(self.dataset.dimensions.keys())

    def dimension(self,
            dimension_name):
        """
        Return dimension with name *dimension_name*.

        A dimension with name *dimension_name* must be present in the dataset.

        The dimension returned is a `netCDF4.Dimension <http://netcdf4-python.googlecode.com/svn/trunk/docs/netCDF4.Dimension-class.html>`_
        instance.
        """
        assert dimension_name in self.dataset.dimensions, \
            "{} not in {}".format(dimension_names,
                self.dataset.dimensions.keys())
        return self.dataset.dimensions[dimension_name]

    def variable_names(self):
        """
        OrderedSet of names of variables in the dataset.

        The set includes the names of dimension variables.
        """
        return mds.ordered_set.OrderedSet(self.dataset.variables.keys())

    def variable(self,
            variable_name):
        """
        Return variable with name *variable_name*.

        A variable with name *variable_name* must be present in the dataset.

        The variable returned is a `netCDF4.Variable <http://netcdf4-python.googlecode.com/svn/trunk/docs/netCDF4.Variable-class.html>`_
        instance.
        """
        assert variable_name in self.dataset.variables, \
            "{} not in {}".format(variable_name, self.dataset.variables.keys())
        return self.dataset.variables[variable_name]

    def data_variable_names(self):
        """
        Return an :py:class:`mds.ordered_set.OrderedSet` with the names of the
        data variables.
        """
        return self.convention.data_variable_names()

    def spatial_data_variable_names(self):
        """
        Return an OrderedSet with the names of the spatial data variables.
        """
        return self.convention.spatial_data_variable_names()

    def temporal_data_variable_names(self):
        """
        Return an OrderedSet with the names of the temporal data variables.
        """
        return self.convention.temporal_data_variable_names()

    def variable_dimension_names(self,
            variable_name):
        """
        Return the names of `variable_name`'s dimensions.

        A variable may depend multiple times on the same dimension, so we
        return a tuple with the names instead of an OrderedSet.
        """
        assert variable_name in self.dataset.variables, variable_name
        variable = self.dataset.variables[variable_name]
        return variable.dimensions

    def space_dimension_names(self,
            variable_name):
        """
        Return an OrderedSet with the names of *variable_name*'s spatial
        dimensions.
        """
        return self.convention.space_dimension_names(variable_name)

    def non_space_dimension_names(self,
            variable_name):
        """
        Return an OrderedSet with the names of *variable_name*'s non-spatial
        dimensions.
        """
        dimension_names = self.variable_dimension_names(variable_name)
        space_dimension_names = self.convention.space_dimension_names(
            variable_name)
        return tuple(name for name in dimension_names if not name in
            space_dimension_names)

    def time_dimension_names(self,
            variable_name):
        """
        Return an OrderedSet with the names of *variable_name*'s temporal
        dimensions.
        """
        return self.convention.time_dimension_names(variable_name)

    def is_spatial_variable(self,
            variable_name):
        """
        Return whether variable *variable_name* is spatial.

        A variable is considered spatial if it has two dimensions representing
        the x and y dimensions.
        """
        return self.convention.is_spatial_variable(variable_name)

    def is_temporal_variable(self,
            variable_name):
        """
        Return whether variable *variable_name* is temporal.
        """
        return self.convention.is_temporal_variable(variable_name)

    def compatible_data_variable_names(self,
            variable_name):
        """
        Return an OrderedSet with the names of data variables that are
        compatible with data variable *variable_name*.

        See also :py:meth:`.convention.Convention.compatible_data_variable_names`.
        """
        return self.convention.compatible_data_variable_names(variable_name)

    def dependent_variable_names(self,
            variable_name):
        return self.convention.dependent_variable_names(variable_name)

    def extent(self,
            variable_name):
        """
        Return *variable_names*'s spatial extent.

        The result is a list with four values: ``[x_min, y_min, x_max, y_max]``.
        """
        return self.convention.extent(variable_name)

    def spatial_dimension_slices(self,
            variable_name,
            extent):
        return self.convention.spatial_dimension_slices(variable_name, extent)

    def dimension_slice(self,
            dimension_name,
            start_value,
            end_value,
            value_selection_method):
        assert dimension_name in self.dataset.dimensions

        dimension = self.dataset.dimensions[dimension_name]
        assert len(dimension) > 0

        if value_selection_method == mds.constants.SELECT_BY_INDEX or \
                dimension_name not in self.variable_names():
            # A start value index points to the first value.
            # An end value index points to the last value.
            # A start slice index points to the first value.
            # An end slice index points to the one-past-the-last value.
            start_value, end_value = int(start_value), int(end_value)
            assert start_value <= end_value
            start_index = mds.math.clamp(0, start_value, len(dimension))
            end_index = mds.math.clamp(0, end_value, len(dimension)) + 1
            slice_ = (start_index, end_index)
        elif value_selection_method == mds.constants.SELECT_BY_VALUE:
            assert dimension_name in self.dataset.variables
            dimension_variable = self.dataset.variables[dimension_name]
            coordinates = dimension_variable[:]
            # TODO We don't support slicing nD coordinate variables yet.
            assert len(coordinates.shape) == 1

            slice_ = mds.math.values_to_slice(coordinates, start_value,
                end_value)
        else:
            assert False

        assert slice_[0] <= slice_[1]
        return slice_

    def xcopy(self,
            variable_names,
            output_filename,
            extent=None,
            dimension_selections=[],
            value_selection_method=mds.constants.SELECT_BY_VALUE,
            history_message=None):
        """
        Copy the variables *variable_names* from the layered dataset to a
        netCDF file named *output_filename*, honoring the spatial *extent* and
        *dimension_selections* passed in. If no spatial variable is selected,
        the value of *extent* is discarded.

        The *extent* passed in must be an sequence containing
        ``[x_min, y_min, x_max, y_max]``. If not provided, the full extent is
        copied.

        The *dimension_selections* passed in must be an iterable of sequences
        containing ``[dimension_name, start_value, end_value]``. Dimensions
        not present in *dimension_selections* will be copied in full.

        The interpretation of the ``start_value`` and ``end_value`` stored in
        each dimension selection depends on the value of
        *value_selection_method*. This argument must be one of the
        selection methods defined in :mod:`mds`.

        The *history_message* is written to the netCDF file. The value is
        appended to the value of the global history attribute. If no value is
        passed, the history attribute, if present, is not changed.
        """
        assert len(variable_names) > 0
        assert all([variable_name in self.data_variable_names() for
            variable_name in variable_names])

        variable_names = list(variable_names)
        first_spatial_variable_name = next((variable_name for variable_name in
            variable_names if self.is_spatial_variable(variable_name)),
            None)

        if extent is None and not first_spatial_variable_name is None:
            # No extent passed in. Use the extent of the first spatial variable
            # selected.
            extent = self.extent(first_spatial_variable_name)
        elif extent is not None and first_spatial_variable_name is None:
            # None of the selected variables is spatial.
            extent = None

        if dimension_selections is None:
            dimension_selections = []

        # Create target dataset with same format as source.
        new_dataset = netCDF4.Dataset(output_filename, mode="w",
            clobber=True, format=self.dataset.file_format)

        # Copy global attributes.
        for attribute_name in self.dataset.ncattrs():
            new_dataset.setncattr(attribute_name, self.dataset.getncattr(
                attribute_name))

        if history_message is not None:
            history_messages = []
            if "history" in new_dataset.ncattrs():
                history_messages = new_dataset.history.split("\n")
            history_messages.append(history_message)
            new_dataset.history = "\n".join(history_messages)

        new_dataset.Source_Software = "Esri ArcGIS"

        # List of lists with dependent variables.
        dependent_variable_names = [self.dependent_variable_names(
            variable_name) for variable_name in variable_names]
        # Flattened list.
        dependent_variable_names = [variable_name for name_list in
            dependent_variable_names for variable_name in name_list]
        assert all([variable_name not in variable_names for variable_name in
            dependent_variable_names])
        variable_names += dependent_variable_names

        # Set of names of dimensions used by the variables passed in.
        dimension_names = mds.ordered_set.OrderedSet()
        for variable_name in variable_names:
            dimension_names |= self.variable_dimension_names(variable_name)

        # Dictionary with slice by dimension name.
        # Initialize the slices by the full range of values.
        dimension_slices = {dimension_name: (0,
            len(self.dataset.dimensions[dimension_name])) for dimension_name in
                dimension_names}

        if not first_spatial_variable_name is None:
            # Add slice of spatial dimensions.
            assert not extent is None
            dimension_slices.update(self.spatial_dimension_slices(
                first_spatial_variable_name, extent))
        assert all([dimension_name in dimension_names for dimension_name in
            dimension_slices.keys()])

        # Update (non-spatial) dimensions with user defined slicing settings.
        for dimension_selection in dimension_selections:
            dimension_name, start_value, end_value = dimension_selection

            if dimension_name in self.variable_names():
                dimension_variable = self.variable(dimension_name)

                if value_selection_method == mds.SELECT_BY_VALUE and \
                        self.convention.is_time_dimension_variable(
                            dimension_variable):
                    # User passed in iso formatted date/time strings. Convert
                    # these to datetime instances and subsequently to dimension
                    # coordinates.
                    start_value = mds.date_time.from_iso_format(start_value)
                    end_value = mds.date_time.from_iso_format(end_value)
                    time_variable = self.variable(dimension_name)
                    start_value, end_value = mds.netcdf.dates_to_coordinates([
                        start_value, end_value], time_variable)

            dimension_slices[dimension_name] = self.dimension_slice(
                dimension_name, start_value, end_value, value_selection_method)

        # About to write dimensions and variables. First order variable and
        # dimension names like in the source dataset.
        dimension_names = list(mds.ordered_set.order(dimension_names,
            self.dimension_names()))
        variable_names = list(mds.ordered_set.order(set(variable_names),
            self.variable_names()))

        # Copy dimensions.
        for dimension_name in dimension_names:
            new_dataset.createDimension(dimension_name,
                dimension_slices[dimension_name][1] -
                    dimension_slices[dimension_name][0] if not
                        self.dimension(dimension_name).isunlimited() else None)

        def init_variable(
                variable,
                variable_name):
            new_variable = new_dataset.createVariable(variable_name,
                datatype=variable.dtype, dimensions=variable.dimensions)
            for attribute_name in variable.ncattrs():
                new_variable.setncattr(attribute_name, variable.getncattr(
                    attribute_name))
            return new_variable

        def copy_variable(
                variable,
                variable_name):
            new_variable = init_variable(variable, variable_name)

            # When copying, there is no need to scale the values. It is
            # better not to because it results in small differences due to
            # casting.
            variable.set_auto_maskandscale(False)
            new_variable.set_auto_maskandscale(False)

            slices_ = [slice(*dimension_slices[dimension_name]) for
                dimension_name in variable.dimensions]

            new_variable[:] = variable[slices_] if slices_ else variable[:]

        for dimension_name in dimension_names:
            if dimension_name in self.dataset.variables:
                variable = self.dataset.variables[dimension_name]
                copy_variable(variable, dimension_name)

        for variable_name in variable_names:
            assert not variable_name in self.dataset.dimensions
            variable = self.dataset.variables[variable_name]
            copy_variable(variable, variable_name)

        new_dataset.close()
