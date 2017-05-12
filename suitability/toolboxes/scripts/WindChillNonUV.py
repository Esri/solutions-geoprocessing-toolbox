# Name: Windchill_non_uv

# Description: Raster function that calculates wind chill using a single variable for windspeed.

# Date Edited: 24/03/2015

#----------------------------------------------------------------------------------------------------------------------

import numpy as np


class Windchill_non_uv():

    def __init__(self):
        self.name = "Wind Chill Function"
        self.description = "This function computes wind chill on the Fahrenheit scale given wind speed and air temperature."
        self.tempunits = "celsius"
        self.windunits = "mps"

    def getParameterInfo(self):
        return [
            {
                'name': 'temperature',  # Needs to be edited by user to match name of varaiable in their dataset
                'dataType': 'raster',
                'value': None,
                'required': True,
                'displayName': "Temperature Raster",
                'description': "A single-band raster where pixel values represent ambient air temperature in Fahrenheit."
            },
            {
                'name': 'units',
                'dataType': 'string',
                'value': 'Kelvin', # Needs to be edited by the user to match what their units are for the temperature variable.
                'required': True,
                'domain': ('Celsius', 'Fahrenheit', 'Kelvin'),
                'displayName': "Temperature Measured In",
                'description': "The unit of measurement associated with the temperature raster."
            },
            {
                'name': 'units2',
                'dataType': 'string',
                'value': 'mps', # Needs to be edited by the user to match what their units are for the wind speed variable.
                'required': True,
                'domain': ('mps', 'mph', 'kmph', 'knots'),
                'displayName': "Temperature Measured In",
                'description': "The unit of measurement associated with the temperature raster."
            },
            {
                'name': 'ws',  # Needs to be edited by user to match name of varaiable in their dataset
                'dataType': 'raster',
                'value': None,
                'required': True,
                'displayName': "Wind-speed Raster",
                'description': "A single-band raster where pixel values represent wind speed measured in miles per hour."
            },
        ]


    def getConfiguration(self, **scalars):
        return {
          'inheritProperties': 4 | 8,               # inherit all but the pixel type and NoData from the input raster
          'invalidateProperties': 2 | 4 | 8,        # invalidate statistics & histogram on the parent dataset because we modify pixel values.
          'inputMask': False                        # Don't need input raster mask in .updatePixels(). Simply use the inherited NoData.
        }


    def updateRasterInfo(self, **kwargs):
        kwargs['output_info']['bandCount'] = 1      # output is a single band raster
        kwargs['output_info']['statistics'] = ({'minimum': -90, 'maximum': 40}, )   # we know nothing about the stats of the outgoing raster.
        kwargs['output_info']['histogram'] = ()     # we know nothing about the histogram of the outgoing raster.
        kwargs['output_info']['pixelType'] = 'f4'

# Getting and then setting the Temprature Units for use later

        if kwargs.get('units').lower() == 'celsius':
            self.tempunits = 'celsius'
        elif kwargs.get('units').lower() == 'farenheit':
            self.tempunits = 'farenheit'
        elif kwargs.get('units').lower() == 'kelvin':
            self.tempunits = 'kelvin'

# Getting and then setting the Windspeed Units for use later

        if kwargs.get('units2').lower() == 'mps':
            self.windunits = 'mps'
        elif kwargs.get('units2').lower() == 'mph':
            self.windunits = 'mph'
        elif kwargs.get('units2').lower() == 'kmph':
            self.windunits = 'kmph'
        elif kwargs.get('units2').lower() == 'knots':
            self.windunits = 'knots'


        #self.doConversion = bool(kwargs.get('units', 'Fahrenheit').lower() == 'Celsius')
        return kwargs


    def updatePixels(self, tlc, size, props, **pixelBlocks):
        ws = np.array(pixelBlocks['ws_pixels'], dtype='f4')
        t = np.array(pixelBlocks['temperature_pixels'], dtype='f4')

#  Using the temperature variable generated earlier to know if a calculation is needed to turn the temp into degrees F
        if self.tempunits.lower() == "celsius":
            t = (9.0/5.0 * t) + 32.0
        elif self.tempunits.lower() == "kelvin":
            t = ((((t)-273.15)*1.8000) +32.00)
        else:
            t = t

#  Using the windspeed variable generated earlier to know if a calculation is needed to turn the windspeed into mph
        if self.windunits.lower() == "mps":
            ws = ws * 2.2369362920544
        elif self.windunits.lower() == "kmph":
            ws = ws * 0.621371
        elif self.windunits() == "knots"
            ws = ws * 1.15078
        else:
            ws = ws

        ws16 = np.power(ws, 0.16)
        outBlock = 35.74 + (0.6215 * t) - (35.75 * ws16) + (0.4275 * t * ws16)
        pixelBlocks['output_pixels'] = outBlock.astype(props['pixelType'])
        return pixelBlocks


    def updateKeyMetadata(self, names, bandIndex, **keyMetadata):
        if bandIndex == -1:
            keyMetadata['datatype'] = 'Scientific'
            keyMetadata['datatype'] = 'Windchill'
        elif bandIndex == 0:
            keyMetadata['wavelengthmin'] = None     # reset inapplicable band-specific key metadata
            keyMetadata['wavelengthmax'] = None
            keyMetadata['bandname'] = 'Windchill'
        return keyMetadata
