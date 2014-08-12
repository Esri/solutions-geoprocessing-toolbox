#------------------------------------------------------------------------------
# Copyright 2014 Esri
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#------------------------------------------------------------------------------

import os, sys, math, decimal, traceback
import arcpy

# INPUT DATASET, Required
dataset = arcpy.GetParameterAsText(0)

try:
    
    #get the top and bottom
    desc = arcpy.Describe(dataset)
    zfactor = 1.0
    if desc.spatialReference.type != "Geographic":
        zfactor = 1.0
    else:
        extent = desc.Extent
        extent_split = [extent.XMin,extent.YMin,extent.XMax,extent.YMax]
           
        top = float(extent_split[3])
        bottom = float(extent_split[1])
        
        #find the mid-latitude of the dataset
        if (top > bottom):
            height = (top - bottom)
            mid = (height/2) + bottom
        elif (top < bottom):  # Unlikely, but just in case
            height = bottom - top
            mid = (height/2) + top
        else: # top == bottom
            mid = top
    
        # convert degrees to radians
        mid = math.radians(mid)
    
        # Find length of degree at equator based on spheroid's semi-major axis
        spatial_reference = desc.SpatialReference
        semi_major_axis = spatial_reference.semiMajorAxis # in meters
        equatorial_length_of_degree = ((2.0 * math.pi * float(semi_major_axis))/360.0)
    
        # function:
        # Z-Factor = 1.0/(111320 * cos(mid-latitude in radians)) 
        decimal.getcontext().prec = 28
        decimal.getcontext().rounding = decimal.ROUND_UP
        a = decimal.Decimal("1.0")
        #b = decimal.Decimal("111320.0") # number of meters in one degree at equator (approximate using WGS84)
        b = decimal.Decimal(str(equatorial_length_of_degree))
        c = decimal.Decimal(str(math.cos(mid)))
        zfactor = a/(b * c)
        zfactor = "%06f" % (zfactor.__abs__())
    
    arcpy.SetParameterAsText(1,str(zfactor))

    # return Z factor message
    arcpy.AddMessage(r"Z-factor: " + (str(zfactor)))

except:
    #print "General Error:"
    print("General Error:") #UPDATE
    tb = sys.exc_info()[2]
    tbinfo = traceback.format_tb(tb)[0]
    #pymsg = tbinfo + "\n" + str(sys.exc_type)+ ": " + str(sys.exc_value) #UPDATE
    pymsg = tbinfo + "\n" + str(sys.exc_info()[0])+ ": " + str(sys.exc_info()[1])
    arcpy.AddError(pymsg)
    #print pymsg #UPDATE
    print(pymsg)