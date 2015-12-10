# -*- coding: utf-8 -*-
import netCDF4
import mds.ordered_set


def initialize_dataset_copy(
        dataset,
        output_filename):
    # Create target dataset with same format as source.
    new_dataset = netCDF4.Dataset(output_filename, mode="w",
        clobber=True, format=dataset.dataset.file_format)

    # Copy global attributes.
    for attribute_name in dataset.dataset.ncattrs():
        new_dataset.setncattr(attribute_name, dataset.dataset.getncattr(
            attribute_name))

    new_dataset.Source_Software = "Esri ArcGIS"

    return new_dataset


def set_history_message(
        dataset,
        history_message):
    dataset.history = history_message.strip()


def append_history_message(
        dataset,
        history_message):
    if hasattr(dataset, "history"):
        history_message = "{}\n{}".format(dataset.history.strip(),
            history_message)
    set_history_message(dataset, history_message)


def dependent_variable_names(
        dataset,
        variable_names):
    """
    Return ordered set of variable names that  variables *variable_names*
    depend on. The set is ordered according to the order of dimensions in
    *dataset*.
    """
    # List of lists with dependent variables.
    result = [dataset.dependent_variable_names(variable_name) for
        variable_name in variable_names]
    # Flattened list.
    result = [variable_name for name_list in result for variable_name in
        name_list]
    assert all([variable_name not in variable_names for variable_name in
        result])
    return mds.ordered_set.order(set(result), dataset.variable_names())


def dependent_dimension_names(
        dataset,
        variable_names):
    """
    Return ordered set of dimension names that variables *variable_names*
    depend on. The set is ordered according to the order of dimensions in
    *dataset*.
    """
    result = mds.ordered_set.OrderedSet()
    for variable_name in variable_names:
        result |= dataset.variable_dimension_names(variable_name)
    return mds.ordered_set.order(result, dataset.dimension_names())


def init_variable(
        variable,
        new_dataset,
        variable_name):
    new_variable = new_dataset.createVariable(variable_name,
        datatype=variable.dtype, dimensions=variable.dimensions)
    for attribute_name in variable.ncattrs():
        new_variable.setncattr(attribute_name, variable.getncattr(
            attribute_name))
    return new_variable
