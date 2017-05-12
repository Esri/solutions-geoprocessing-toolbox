# Name: WindSpeedFromUV

# Description: Python raster function that extracts wind speed from u and v components of wind.

# Date Edited: 24/03/2015

#----------------------------------------------------------------------------------------------------------------------

import numpy as np


class WindSpeedFromUV():

    def __init__(self):
        self.name = "Wind Speed Function"
        self.description = "This function computes wind Speed given u/v components of wind."


    def getParameterInfo(self):
        return [
            {
                'name': 'u',
                'dataType': 'raster',
                'value': None,
                'required': True,
                'displayName': "U component of wind Raster",
                'description': "A single-band raster where pixel values represent the u component of wind in metres per second."
            },
            {
                'name': 'v',
                'dataType': 'raster',
                'value': None,
                'required': True,
                'displayName': "V component of wind Raster",
                'description': "A single-band raster where pixel values represent the v component of wind in metres per second."
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
        kwargs['output_info']['statistics'] = ({'minimum': 0, 'maximum': 150}, )
        kwargs['output_info']['histogram'] = ()     # we know nothing about the histogram of the outgoing raster.
        kwargs['output_info']['pixelType'] = 'f4'
        return kwargs


    def updatePixels(self, tlc, size, props, **pixelBlocks):
        u = np.array(pixelBlocks['u_pixels'], dtype='f4')        
        v = np.array(pixelBlocks['v_pixels'], dtype='f4')

        outBlock = np.sqrt(u**2 + v**2)
        pixelBlocks['output_pixels'] = outBlock.astype(props['pixelType'])
        return pixelBlocks


    def updateKeyMetadata(self, names, bandIndex, **keyMetadata):
        if bandIndex == -1:
            keyMetadata['datatype'] = 'Scientific'
            keyMetadata['datatype'] = 'WindSpeed'
        elif bandIndex == 0:
            keyMetadata['wavelengthmin'] = None     # reset inapplicable band-specific key metadata
            keyMetadata['wavelengthmax'] = None
            keyMetadata['bandname'] = 'WindSpeed'
        return keyMetadata
