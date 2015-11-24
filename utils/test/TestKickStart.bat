@ECHO OFF
rem ------------------------------------------------------------------------------
rem  Copyright 2015 Esri
rem  Licensed under the Apache License, Version 2.0 (the "License");
rem  you may not use this file except in compliance with the License.
rem  You may obtain a copy of the License at
rem 
rem    http://www.apache.org/licenses/LICENSE-2.0
rem 
rem  Unless required by applicable law or agreed to in writing, software
rem  distributed under the License is distributed on an "AS IS" BASIS,
rem  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
rem  See the License for the specific language governing permissions and
rem  limitations under the License.
rem ------------------------------------------------------------------------------
rem  TestKickStart.bat
rem ------------------------------------------------------------------------------
rem  requirments:
rem  * ArcGIS Desktop 10.X+ or ArcGIS Pro 1.X+
rem  * Python 2.7 or Python 3.4
rem  author: ArcGIS Solutions
rem  company: Esri
rem ==================================================
rem  description:
rem  This file starts the test running for Desktop (Python 2.7+) and
rem  ArcGIS Pro (Python 3.4+).
rem 
rem ==================================================
rem  history:
rem  10/06/2015 - MF - placeholder
rem  10/30/2015 - MF - tests running
rem 11/23/2015 - JH - added paremeter for default log file name
rem ==================================================

REM usage: set LOG=<defaultLogFileName.log>
REM name is optional; if not specified, name will be specified for you
set LOG=default.log

REM =====================================================
REM If you have BOTH versions of Python installed:

ECHO Python 3.4 Tests ===============================
py -3.4 TestRunner.py %LOG%

ECHO Python 2.7 Tests ===============================
py -2.7 TestRunner.py %LOG%

REM =====================================================
REM If you only have ONE version of Python installed:
REM python TestRunner.py
pause
