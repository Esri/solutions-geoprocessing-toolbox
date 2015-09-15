# coding: utf-8
#------------------------------------------------------------------------------
# Copyright 2015 Esri
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
# TestRuner.py
#------------------------------------------------------------------------------

import os
import sys

commandStr = r"ant -f run_all_tests.xml"

def main():
	print("Start...(" + str(datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")) + ")")
	os.system(commandStr)
	print("Done. (" + str(datetime.datetime.now().strftime("%A, %d. %B %Y %I:%M%p")) + ")")

# MAIN =============================================
if __name__ == "__main__":
    main()
