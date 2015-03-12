#------------------------------------------------------------------------------
# Copyright 2013 Esri
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
# Name: search_replace.py
# Description: MDCS setup related/Not used by MDCS directly.
# Version: 20140417
# Requirements: ArcGIS 10.1 SP1
# Author: Esri Imagery Workflows team
#------------------------------------------------------------------------------
#!/usr/bin/env python

import os,sys
from fnmatch import fnmatch

def main():
    pass

if __name__ == '__main__':
    main()


if len(sys.argv) != 5:
    print (" number of inputs are invalid")
    print (" <path to the folder> <search string> <replace string> <file extension filter>")
    sys.exit()
parent_folder_path= sys.argv[1]
search = sys.argv[2]
replace = sys.argv[3]
pattern = sys.argv[4]

for path, subdirs, files in os.walk(parent_folder_path):
    for name in files:
        if fnmatch(name, pattern):
            newfilePath = os.path.join(path, name)

            file = open(newfilePath, 'r')
            xml = file.read()
            file.close()

            try:

                print (newfilePath)
                print ("String [%s] replaced with [%s]" % (search, replace))
                print ("-------------------------------")

                l_indx_ = xml.lower().index(search.lower())
                while(l_indx_ >= 0):
                    left_ = xml[0:l_indx_]
                    right = xml[l_indx_ + len(search):len(xml)]
                    xml = left_ + replace + right
                    try:
                        l_indx_ = xml.lower().index(search.lower(), l_indx_ + 1)
                    except:
                        l_indx_ = -1

                file = open(newfilePath, 'w')
                file.write(str(xml))
                file.close()

            except:
                found = False

            xml = ''
            file = ''
print ("Done")
