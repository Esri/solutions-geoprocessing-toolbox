
# coding: utf-8
'''
------------------------------------------------------------------------------
 Copyright 2017 Esri
 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at
   http://www.apache.org/licenses/LICENSE-2.0
 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
------------------------------------------------------------------------------
 ==================================================
 arcpyAssert.py
 --------------------------------------------------
 requirements: ArcGIS X.X, Python 2.7 or Python 3.4
 author: ArcGIS Solutions
 contact: support@esri.com
 company: Esri
 ==================================================
 description:
 Credit to Moravec Labs for originating this Mixin class
 * 
 * https://github.com/MoravecLabs/ArcpyTestExample
 
 ==================================================
 history:
 05/02/2017 - MF - Copied code from MoravecLabs
 ==================================================
'''

import arcpy
import os
import tempfile
import unittest

class FeatureClassAssertMixin(object):
    """
    Mixin for supporting the compare or assertion of two feature classes.
    """

    def assertFeatureClassEqual(self,
                                first,
                                second,
                                sort_field,
                                message=None,
                                compare_type=None,
                                ignore_options=None,
                                xy_tolerance=None,
                                m_tolerance=None,
                                z_tolerance=None,
                                attribute_tolerances=None,
                                omit_field=None):
        """
        Compares the second feature class to the first, and reports any issues.  Detailed issues are printed to the
        console if found.
        :param first:
        :param second:
        :param sort_field:
        :param message:
        :param compare_type:
        :param ignore_options:
        :param xy_tolerance:
        :param m_tolerance:
        :param z_tolerance:
        :param attribute_tolerances:
        :param omit_field:
        :return:
        """

        # Make a place to store the compare file
        compare_file = tempfile.mkstemp(".txt")
        os.close(compare_file[0])
        os.remove(compare_file[1])
        result = arcpy.FeatureCompare_management(first,
                                                 second,
                                                 sort_field,
                                                 compare_type,
                                                 ignore_options,
                                                 xy_tolerance,
                                                 m_tolerance,
                                                 z_tolerance,
                                                 attribute_tolerances,
                                                 omit_field,
                                                 continue_compare=True,
                                                 out_compare_file=compare_file[1])
        if 'true' == result.getOutput(1):
            # delete the compare file
            os.remove(compare_file[1])
            return

        # read the compare file and print it out
        print(compare_file[1])
        with open(compare_file[1], 'r') as f:
            #[print(l.rstrip()) for l in f.readlines()] # syntax error here
            for l in f.readlines():
                print(l.rstrip()) 
        os.remove(compare_file[1])

        # set the assertion message.
        msg = message if message is not None else "Feature class {} is not equal to {}".format(second, first)
        raise AssertionError(msg)