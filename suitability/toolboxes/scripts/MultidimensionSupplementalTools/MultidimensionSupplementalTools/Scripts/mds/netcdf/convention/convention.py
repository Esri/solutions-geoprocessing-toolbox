# -*- coding: utf-8 -*-
import mds.math
import mds.ordered_set


class Convention(object):

    @staticmethod
    def convention_names(
            dataset):
        result = []
        for attribute_name in ["Conventions", "conventions"]:
            if hasattr(dataset, attribute_name):
                names = getattr(dataset, attribute_name)
                # http://www.unidata.ucar.edu/software/netcdf/conventions.html:
                # The value of the `Conventions' attribute may be a
                # single text string containing a list of the convention
                # names separated by blank space (recommended) or commas
                # (if a convention name contains blanks)
                separator = "," if names.find(",") != -1 else None
                result = [name.strip() for name in names.split(separator)]
                break
        return result

    @staticmethod
    def extent_of_variable(
            variable):
        assert not variable is None
        assert len(variable.shape) == 1
        assert len(variable) > 0
        first, last = variable[0], variable[-1]
        return min(first, last), max(first, last)

    def __init__(self,
            dataset,
            filter_out_nd_coordinates):
        self.dataset = dataset
        self.filter_out_nd_coordinates = filter_out_nd_coordinates

    def coordinate_variable_names(self,
            variable_name):
        assert variable_name in self.dataset.variables, variable_name
        result = mds.ordered_set.OrderedSet()
        variable = self.dataset.variables[variable_name]
        dimension_names = variable.dimensions

        for dimension_name in dimension_names:
            if dimension_name in self.dataset.variables:
                if self.is_coordinate_variable(dimension_name):
                    result.add(dimension_name)

        return result

    def is_space_dimension_variable(self,
            dimension_name):
        result = False

        if dimension_name in self.dataset.variables and \
                self.is_coordinate_variable(dimension_name):
            variable = self.dataset.variables[dimension_name]
            result = self.is_x_dimension_variable(variable) or \
                self.is_y_dimension_variable(variable)

        return result

    def space_dimension_names(self,
            variable_name):
        assert variable_name in self.dataset.variables, variable_name
        variable = self.dataset.variables[variable_name]
        result = mds.ordered_set.OrderedSet()

        for dimension_name in variable.dimensions:
            if self.is_space_dimension_variable(dimension_name):
                result.add(dimension_name)

        return result

    def time_dimension_names(self,
            variable_name):
        assert variable_name in self.dataset.variables, variable_name
        variable = self.dataset.variables[variable_name]
        result = mds.ordered_set.OrderedSet()

        for dimension_name in variable.dimensions:
            if self.is_time_dimension_variable(dimension_name):
                result.add(dimension_name)

        return result

    def data_variable_names(self):
        result = mds.ordered_set.OrderedSet()
        for variable_name in self.dataset.variables:
            if self.is_data_variable(variable_name):
                result.add(variable_name)
        return result

    def spatial_data_variable_names(self):
        result = [variable_name for variable_name in
            self.data_variable_names() if
                self.is_spatial_variable(variable_name)]
        return mds.ordered_set.OrderedSet(result)

    def temporal_data_variable_names(self):
        result = [variable_name for variable_name in
            self.data_variable_names() if
                self.is_temporal_variable(variable_name)]
        return mds.ordered_set.OrderedSet(result)

    def is_spatial_variable(self,
            variable_name):
        assert variable_name in self.dataset.variables, variable_name

        # A spatial variable has two dimensions representing the x and y
        # dimensions.
        space_dimension_names = []
        variable = self.dataset.variables[variable_name]
        for dimension_name in variable.dimensions:
            if dimension_name in self.dataset.variables and \
                    self.is_space_dimension_variable(dimension_name):
                space_dimension_names.append(dimension_name)
        return len(space_dimension_names) == 2

    def is_temporal_variable(self,
            variable_name):
        assert variable_name in self.dataset.variables, variable_name
        variable = self.dataset.variables[variable_name]
        return any([self.is_time_dimension_variable(dimension_name) for
            dimension_name in variable.dimensions if dimension_name in
            self.dataset.variables])

    def extent(self,
            variable_name):
        assert self.is_spatial_variable(variable_name), variable_name
        coordinate_variable_names = self.coordinate_variable_names(
            variable_name)
        coordinate_variables = [self.dataset.variables[name] for name in
            coordinate_variable_names]
        x_variable = None
        y_variable = None

        for variable in coordinate_variables:
            if x_variable is None and self.is_x_dimension_variable(variable):
                x_variable = variable
            if y_variable is None and self.is_y_dimension_variable(variable):
                y_variable = variable

        x_min, x_max = self.extent_of_variable(x_variable)
        y_min, y_max = self.extent_of_variable(y_variable)
        return [x_min, y_min, x_max, y_max]

    def variable_attribute_values(self,
            attribute_name):
        result = []
        for variable in self.dataset.variables.values():
            if hasattr(variable, attribute_name):
                result.append(getattr(variable, attribute_name))
        return result

    def spatial_dimension_slices(self,
            variable_name,
            extent):
        space_dimension_names = list(self.space_dimension_names(
            variable_name))
        assert len(space_dimension_names) == 2, "{}: {}".format(
            variable_name, space_dimension_names)
        assert all(dimension_name in self.dataset.variables for dimension_name
            in space_dimension_names)

        spatial_dimension_variables = [self.dataset.variables[dimension_name]
            for dimension_name in space_dimension_names]
        if self.is_x_dimension_variable(spatial_dimension_variables[0]):
            assert self.is_y_dimension_variable(spatial_dimension_variables[1])
            x_index = 0
            y_index = 1
        else:
            assert self.is_x_dimension_variable(spatial_dimension_variables[1])
            assert self.is_y_dimension_variable(spatial_dimension_variables[0])
            x_index = 1
            y_index = 0

        result = {}
        result[space_dimension_names[x_index]] = mds.math.values_to_slice(
            spatial_dimension_variables[x_index][:], extent[0], extent[2])
        result[space_dimension_names[y_index]] = mds.math.values_to_slice(
            spatial_dimension_variables[y_index][:], extent[1], extent[3])
        return result

    def compatible_data_variable_names(self,
            variable_name):
        """
        Return OrderedSet with names of data variables that are compatible with
        data variable *variable_name*.

        If variable *variable_name* is a spatial data variable, compatible
        variables are those data variables that are not spatial or that are
        spatial and share the same spatial dimensions.

        If variable *variable_name* is not a spatial data variable, compatible
        variables are all data variables.

        The result includes *variable_name*.
        """
        result = mds.ordered_set.OrderedSet()
        data_variable_names = self.data_variable_names()
        assert variable_name in data_variable_names, variable_name

        if not self.is_spatial_variable(variable_name):
            result = data_variable_names
        else:
            space_dimension_names = self.space_dimension_names(
                variable_name)
            for data_variable_name in data_variable_names:
                if not self.is_spatial_variable(data_variable_name):
                    result.add(data_variable_name)
                else:
                    if set(self.space_dimension_names(data_variable_name)) \
                            == set(space_dimension_names):
                        result.add(data_variable_name)

        return result

    def depends_on_nd_coordinate_variable(self,
            variable_name):
        # Return True if one of the coordinate variables is nD.
        coordinate_variable_names = self.coordinate_variable_names(
            variable_name)

        result = False
        for coordinate_variable_name in coordinate_variable_names:
            coordinate_variable = self.dataset.variables[
                coordinate_variable_name]
            if len(coordinate_variable.shape) > 1:
                result = True
                break

        return result
