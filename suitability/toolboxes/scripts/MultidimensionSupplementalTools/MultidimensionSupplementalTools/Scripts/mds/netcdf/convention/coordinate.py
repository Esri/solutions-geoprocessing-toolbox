# -*- coding: utf-8 -*-
import mds.ordered_set
import convention


class Coordinate(convention.Convention):
    """
    This class implements the `Coordinate Attribute Convention`_.

    .. _Coordinate Attribute Convention: http://www.unidata.ucar.edu/software/netcdf-java/reference/CoordinateAttributes.html
    """

    @staticmethod
    def conforms(
            dataset):
        return "_Coordinates" in convention.Convention.convention_names(dataset)

    def __init__(self,
            dataset,
            filter_out_nd_coordinates):
        convention.Convention.__init__(self, dataset, filter_out_nd_coordinates)

    def coordinate_variable_names(self,
            variable_name):
        assert variable_name in self.dataset.variables, variable_name
        result = mds.ordered_set.OrderedSet()
        variable = self.dataset.variables[variable_name]
        dimension_names = variable.dimensions

        for dimension_name in dimension_names:
            # TODO Not every dimension has a corresponding variable.
            if dimension_name in self.dataset.variables:
                if self.is_coordinate_axis_variable(dimension_name):
                    result.add(dimension_name)

        return result
    def is_coordinate_variable(self,
            variable_name):
        assert variable_name in self.dataset.variables, variable_name
        variable = self.dataset.variables[variable_name]
        return len(variable.dimensions) == 1 and (variable.dimensions[0] ==
            variable_name or hasattr(variable, "_CoordinateAliasForDimension"))

    def is_x_dimension_variable(self,
            variable):
        result = False
        if hasattr(variable, "_CoordinateAxisType") and \
                variable._CoordinateAxisType in ["GeoX", "Lon"]:
            result = True
        return result

    def is_y_dimension_variable(self,
            variable):
        result = False
        if hasattr(variable, "_CoordinateAxisType") and \
                variable._CoordinateAxisType in ["GeoY", "Lat"]:
            result = True
        return result

    def is_time_dimension_variable(self,
            variable):
        variable = self.dataset.variables[variable] if isinstance(variable,
            basestring) else variable
        return self.is_time_dimension(variable)

    def is_data_variable(self,
            variable_name):
        assert variable_name in self.dataset.variables, variable_name
        return not ((
                self.filter_out_nd_coordinates and
                self.depends_on_nd_coordinate_variable(variable_name)
            ) or \
            self.is_coordinate_variable(variable_name) or \
            self.is_coordinate_transform_variable(variable_name) or \
            self.is_coordinate_axis_variable(variable_name))

    def is_time_dimension(self,
            variable):
        result = False
        if hasattr(variable, "_CoordinateAxisType") and \
                variable._CoordinateAxisType in ["RunTime", "Time"]:
            result = True
        return result

    def is_listed_in_a_coordinate_axes_attribute(self,
            variable_name):
        for variable in self.dataset.variables.itervalues():
            if hasattr(variable, "_CoordinateAxes"):
                if variable_name in variable._CoordinateAxes.split():
                    return True
        return False

    def is_coordinate_axis_variable(self,
            variable_name):
        assert variable_name in self.dataset.variables, variable_name
        variable = self.dataset.variables[variable_name]
        return (
            hasattr(variable, "_CoordinateAxisType") or \
            hasattr(variable, "_CoordinateAliasForDimension") or \
            hasattr(variable, "_CoordinateZisPositive")) or \
            self.is_coordinate_variable(variable_name) or \
            self.is_listed_in_a_coordinate_axes_attribute(variable_name)

    def is_coordinate_system_variable(self,
            variable_name):
        assert variable_name in self.dataset.variables, variable_name
        variable = self.dataset.variables[variable_name]
        return (hasattr(variable, "_CoordinateTransforms") or \
            hasattr(variable, "_CoordinateSystemFor")) or \
            variable_name in self.variable_attribute_values(
                "_CoordinateSystems")

    def is_coordinate_transform_variable(self,
            variable_name):
        assert variable_name in self.dataset.variables, variable_name
        variable = self.dataset.variables[variable_name]
        return (hasattr(variable, "_CoordinateTransformType") or \
            hasattr(variable, "_CoordinateAxisTypes")) or \
            variable_name in self.variable_attribute_values(
                "_CoordinateTransforms")

    def dependent_variable_names(self,
            variable_name):
        assert variable_name in self.dataset.variables

        # TODO Hackish.
        # See if a coordinate transform variable is associated with the
        # data variable.
        variable = self.dataset.variables[variable_name]

        dimension_names = variable.dimensions

        coordinate_axis_types1 = []

        for dimension_name in dimension_names:
            if dimension_name in self.dataset.variables:
                dimension_variable = self.dataset.variables[dimension_name]
                if hasattr(dimension_variable, "_CoordinateAxisType"):
                    coordinate_axis_types1.append(
                        dimension_variable._CoordinateAxisType)

        result = mds.OrderedSet()

        coordinate_axes1 = []
        if hasattr(variable, "_CoordinateAxes"):
            coordinate_axes1 = variable._CoordinateAxes.split()
            for value in coordinate_axes1:
                result.add(value)

        # See if there is a coordinate transform variable with the same
        # coordinate axis types.
        coordinate_transform_variable_names = [name for name in
            self.dataset.variables.keys() if
                self.is_coordinate_transform_variable(name)]

        for coordinate_transform_variable_name in \
                coordinate_transform_variable_names:
            coordinate_transform_variable = self.dataset.variables[
                coordinate_transform_variable_name]
            if hasattr(coordinate_transform_variable, "_CoordinateAxisTypes"):
                coordinate_axis_types2 = \
                    coordinate_transform_variable._CoordinateAxisTypes.split()
                if all([axis_type in coordinate_axis_types1 for axis_type in
                        coordinate_axis_types2]):
                    result.add(coordinate_transform_variable_name)

            if hasattr(coordinate_transform_variable, "_CoordinateAxes"):
                coordinate_axes2 = \
                    coordinate_transform_variable._CoordinateAxes.split()
                if all([axis in coordinate_axes1 for axis in coordinate_axes2]):
                    result.add(coordinate_transform_variable_name)

        # Get rid of the dimension variables.
        return result - dimension_names
