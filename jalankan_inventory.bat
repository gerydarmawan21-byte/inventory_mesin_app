@echo off
REM Aktifkan virtual environment
call venv\Scripts\activate

REM Jalankan Streamlit
streamlit run app.py

pause
