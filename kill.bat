@echo off
:again
taskkill /F /IM "python.exe"
if errorlevel=0 goto end
if errorlevel=1 goto again
:end