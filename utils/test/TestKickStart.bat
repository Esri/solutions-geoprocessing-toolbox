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
rem  requirements:
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
rem  12/01/2015 - JH - added paremeter for default log file name
rem  07/05/2016 - MF - updates to changes for Pro 1.3+
rem ==================================================

REM === TEST SETUP ===================================
REM === TEST SETUP ===================================


REM === LOG SETUP ====================================
REM usage: set LOG=<defaultLogFileName.log>
REM name is optional; if not specified, name will be specified for you
set LOG=
REM === LOG SETUP ====================================


REM === SINGLE VERSION ==================================
REM If you only have ONE version of Python installed
REM uncomment the following lines
REM =====================================================
REM python TestRunner.py
REM IF %ERRORLEVEL% NEQ 0 (
REM    ECHO 'One or more tests failed'
REM )
REM === SINGLE VERSION ==================================


REM === MULTIPLE VERSIONS ===============================
REM If you have BOTH versions of Python installed use
REM these lines
REM =====================================================
ECHO Python 3.4 Tests ===============================
REM py -3.4 TestRunner.py %LOG%
REM The location of python.exe will depend upon your installation
REM of ArcGIS Pro. Modify the following line as necessary:
"C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe" TestRunner.py %LOG%
REM check if ArcGIS Pro/Python 3.4 tests failed
IF %ERRORLEVEL% NEQ 0 (
   ECHO 'One or more tests failed'
)
ECHO Python 2.7 Tests ===============================
REM py -2.7 TestRunner.py %LOG%
py TestRunner.py %LOG%
REM check if Desktop for ArcGIS/Python 2.7 tests failed
IF %ERRORLEVEL% NEQ 0 (
   ECHO 'One or more tests failed'
)
REM === MULTIPLE VERSIONS ===============================


REM === CLEANUP =========================================
ECHO Removing RangeRingUtils.py ...
DEL ".\distance_tests\RangeRingUtils.py"
REM === CLEANUP =========================================

pause
