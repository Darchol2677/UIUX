@echo off
echo ==============================================
echo Installing Dependencies...
echo ==============================================
py -m pip install -r requirements.txt

echo ==============================================
echo Starting Server...
echo ==============================================
echo IMPORTANT: Make sure you have set the OPENAI_API_KEY environment variable.
py app.py
pause
