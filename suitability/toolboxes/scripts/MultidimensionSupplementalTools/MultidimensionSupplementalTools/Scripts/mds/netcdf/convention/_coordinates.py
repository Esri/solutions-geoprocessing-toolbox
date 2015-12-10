# -*- coding: utf-8 -*-
import mds.ordered_set
import convention


__all__ = [
    "_Coordinates"
]


# http://www.unidata.ucar.edu/software/netcdf-java/reference/CoordinateAttributes.html


class _Coordinates(convention.Convention):

    @staticmethod
    def conforms(
            dataset):
        return "_Coordinates" in convention.Convention.convention_names(dataset)

    def __init__(self,
            dataset,
            filter_out_nd_coordinates):
        convention.Convention.__init__(self, dataset, filter_out_nd_coordinates)

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

    def is_x_dimension(self,
            dimension_name):
        result = False
        if dimension_name in self.dataset.variables:
            result = self.is_x_dimension_variable(self.dataset.variables[
                dimension_name])
        return result

    def is_y_dimension(self,
            dimension_name):
        result = False
        if dimension_name in self.dataset.variables:
            result = self.is_y_dimension_variable(self.dataset.variables[
                dimension_name])
        return result

    def is_spatial_dimension(self,
            dimension_name):
        return self.is_x_dimension(dimension_name) or \
            self.is_y_dimension(dimension_name)

    def is_spatial_variable(self,
            variable_name):
        assert variable_name in self.dataset.variables, variable_name

        # A spatial variable has two dimensions representing the x and y
        # dimensions.
        spatial_dimension_names = []
        variable = self.dataset.variables[variable_name]
        for dimension_name in variable.dimensions:
            if self.is_spatial_dimension(dimension_name):
                spatial_dimension_names.append(dimension_name)
        return len(spatial_dimension_names) == 2

    def is_time_dimension(self,
            variable):
        result = False
        if hasattr(variable, "_CoordinateAxisType") and \
                variable._CoordinateAxisType in ["RunTime", "Time"]:
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

    def is_coordinate_variable(self,
            variable_name):
        assert variable_name in self.dataset.variables, variable_name
        variable = self.dataset.variables[variable_name]
        return len(variable.dimensions) == 1 and (variable.dimensions[0] ==
            variable_name or hasattr(variable, "_CoordinateAliasForDimension"))

    def is_coordinate_axis_variable(self,
            variable_name):
        assert variable_name in self.dataset.variables, variable_name
        variable = self.dataset.variables[variable_name]
        return (hasattr(variable, "_CoordinateAxisType") or \
            hasattr(variable, "_CoordinateAliasForDimension") or \
            hasattr(variable, "_CoordinateZisPositive")) or \
            self.is_coordinate_variable(variable_name) or \
            variable_name in self.variable_attribute_values("_CoordinateAxes")

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

    def spatial_dimension_names(self,
            variable_name):
        assert variable_name in self.dataset.variables, variable_name
        variable = self.dataset.variables[variable_name]
        result = mds.ordered_set.OrderedSet()

        for dimension_name in variable.dimensions:
            if self.is_spatial_dimension(dimension_name):
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

        coordinate_axes1 = []
        if hasattr(variable, "_CoordinateAxes"):
            coordinate_axes1 = variable._CoordinateAxes.split()

        # See if there is a coordinate transform variable with the same
        # coordinate axis types.
        coordinate_transform_variable_names = [name for name in
            self.dataset.variables.keys() if
                self.is_coordinate_transform_variable(name)]

        result = mds.OrderedSet()
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

        return result

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

        # for dimension_name in dimension_names:
        #     variable = self.dataset.variables[dimension_name]
        #     if hasattr(variable, "_CoordinateAxisType") or \
        #             hasattr(variable, "_CoordinateAliasForDimension") or \
        #             hasattr(variable, "_CoordinateZisPositive"):
        #         result.add(dimension_name)
        #     elif self.is_coordinate_variable(dimension_name):
        #         result.add(dimension_name)
        #     else:
        #         data_variable = self.dataset.variables[data_variable_name]

        #         if hasattr(data_variable, "_CoordinateAxes"):
        #             coordinate_variable_names = \
        #                 data_variable._CoordinateAxes.split()
        #             assert len(coordinate_variable_names) >= 2
        #             if dimension_name in coordinate_variable_names:
        #                 result.add(dimension_name)

        # for variable_name in self.dataset.variables:
        #     variable = self.dataset.variables[variable_name]
        #     if hasattr(variable, "_CoordinateAxisType") or \
        #             hasattr(variable, "_CoordinateAliasForDimension") or \
        #             hasattr(variable, "_CoordinateZisPositive"):
        #         result.add(variable_name)
        #     elif self.is_coordinate_variable(variable_name):
        #         # TODO No, loops over ALL variables, not the dimension
        #         # variables. This adds to many variables to the result. We
        #         # only ask for the ones connected to the data_variable_name
        #         result.add(variable_name)
        #     else:
        #         data_variable = self.dataset.variables[data_variable_name]

        #         if hasattr(data_variable, "_CoordinateAxes"):
        #             coordinate_variable_names = \
        #                 data_variable._CoordinateAxes.split()
        #             assert len(coordinate_variable_names) >= 2
        #             if variable_name in coordinate_variable_names:
        #                 result.add(variable_name)

        return result

    def extent(self,
            variable_name):
        assert self.is_spatial_variable(variable_name), variable_name
        assert variable_name in self.dataset.variables, variable_name
        # The variable name passed in must point to a data variable.
        coordinate_variable_names = self.coordinate_variable_names(
            variable_name)

        coordinate_axis_variables = [self.dataset.variables[name] for name in
            coordinate_variable_names]

        x_variable = None
        y_variable = None

        for variable in coordinate_axis_variables:
            if x_variable is None and self.is_x_dimension_variable(variable):
                x_variable = variable
            if y_variable is None and self.is_y_dimension_variable(variable):
                y_variable = variable

        # There are more ways to figure out what the x and y dimension
        # variables are. Check coordinate_variable_names method.
        x_min, x_max = convention.Convention.extent_of_variable(x_variable)
        y_min, y_max = convention.Convention.extent_of_variable(y_variable)
        return [x_min, y_min, x_max, y_max]
