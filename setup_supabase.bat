@echo off
python -m pip install -r requirements.txt
if errorlevel 1 exit /b 1
python scripts\init_supabase.py
