# Name: WindchillUV

# Description: Raster function that calculates Wind chill using U and V components of wind rather than a single variable for wind speed.

# Date Edited: 24/03/2015

#----------------------------------------------------------------------------------------------------------------------

import numpy as np


class WindChillUV():

    def __init__(self):
        self.name = "Wind Chill Function"
        self.description = "This function computes wind chill on the Fahrenheit scale given u/v components of wind and a temparature variable."
        self.tempunits = "Kelvin"

    def getParameterInfo(self):
        return [
            {
                'name': 'tmpsfc',
                'dataType': 'raster',
                'value': None,
                'required': True,
                'displayName': "Temperature Raster",
                'description': "A single-band raster where pixel values represent ambient air temperature."
            },
            {
                'name': 'units',
                'dataType': 'string',
                'value': 'Kelvin', # To be changed by the user to match whatever there input parameter units are.
                'required': True,
                'domain': ('Celsius', 'Fahrenheit', 'Kelvin'),
                'displayName': "Temperature Measured In",
                'description': "The unit of measurement associated with the temperature raster."
            },
            {
                'name': 'u',
                'dataType': 'raster',
                'value': None,
                'required': True,
                'displayName': "U component of wind Raster",
                'description': "A single-band raster where pixel values represent the u component of wind."
            },
            {
                'name': 'v',
                'dataType': 'raster',
                'value': None,
                'required': True,
                'displayName': "V component of wind Raster",
                'description': "A single-band raster where pixel values represent the v component of wind."
            }
        ]


    def getConfiguration(self, **scalars):
        return {
          'inheritProperties': 4 | 8,               # inherit all but the pixel type and NoData from the input raster
          'invalidateProperties': 2 | 4 | 8,        # invalidate statistics & histogram on the parent dataset because we modify pixel values.
          'inputMask': False                        # Don't need input raster mask in .updatePixels(). Simply use the inherited NoData.
        }


    def updateRasterInfo(self, **kwargs):
        kwargs['output_info']['bandCount'] = 1      # output is a single band raster
        kwargs['output_info']['pixelType'] = 'f4'

# Getting and then setting the Temprature Units for use later

        if kwargs.get('units').lower() == 'celsius':
            self.tempunits = 'celsius'
        elif kwargs.get('units').lower() == 'farenheit':
            self.tempunits = 'farenheit'
        elif kwargs.get('units').lower() == 'kelvin':
            self.tempunits = 'kelvin'


        return kwargs


    def updatePixels(self, tlc, size, props, **pixelBlocks):
        u = np.array(pixelBlocks['u_pixels'], dtype='f4')
        v = np.array(pixelBlocks['v_pixels'], dtype='f4') 
        t = np.array(pixelBlocks['tmpsfc_pixels'], dtype='f4')

#  Using the temperature variable generated earlier to know if a calculation is needed to turn the temp into degrees F
        if self.tempunits.lower() == "celsius":
            t = (9.0/5.0 * t) + 32.0
        elif self.tempunits.lower() == "kelvin":
            t = ((((t)-273.15)*1.8000) +32.00)
        else:
            t = t


        ws = (np.sqrt(np.square(u) + np.square(v))*2.23694)
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
