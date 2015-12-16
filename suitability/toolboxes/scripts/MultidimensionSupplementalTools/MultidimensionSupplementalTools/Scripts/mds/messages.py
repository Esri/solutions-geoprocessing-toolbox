# -*- coding: utf-8 -*-

INPUT_DATASET_DOES_NOT_RESOLVE_TO_FILENAME = \
    "Input OPeNDAP Dataset: URL {} does not resolve to a filename."
INPUT_DATASET_URL_MALFORMED = \
    "Input OPeNDAP Dataset: URL {} is malformed or references inaccessible " \
    "data."
INPUT_DATASET_GENERIC_ERROR = \
    "Input OPeNDAP Dataset: URL {}: {}."

INPUT_FILE_DOES_NOT_EXIST = \
    "Input File or URL String: Dataset {} does not exist or is not supported."
INPUT_FILE_GENERIC_ERROR = \
    "Input File: URL {}: {}."

VARIABLES_DO_NOT_EXIST = \
    "Variables: {} do not exist in the {}."
NONE_OF_VARIABLES_EXISTS = \
    "Variables: No valid fields specified."
VARIABLES_MUST_SHARE_DIMENSIONS = \
    "Variables: All spatial variables must share the same spatial dimensions."

OUTPUT_FILE_EXTENSION_MUST_BE_NC = \
    "Output netCDF File: Output file extension must be .nc."

DIMENSION_NOT_PRESENT = \
    "Dimensions: Dimension {} not present in selected variable(s)."
MULTIDIMENSIONAL_DIMENSIONS_NOT_SUPPORTED = \
    "Dimensions: Dimension {} depends on multiple dimensions. This is not supported."
INVALID_DATE_TIME = \
    "Dimensions: Invalid date/time value."
SKIPPING_SPATIAL_DIMENSION = \
    "Dimensions: Spatial coordinate variables may not be used as " \
    "dimensions. Select spatial coordinates using the Extent parameter."

OPENDAP_TO_NETCDF_HISTORY = \
    "Created {} by ArcGIS OPeNDAP to NetCDF tool using the following " \
    "OPeNDAP URL: {}"
TEMPORAL_AGGREGATION_HISTORY = \
    "Created {} by ArcGIS using the folowing command: {}"
