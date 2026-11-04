@echo off
echo ====================================================
echo   Starting FUTRSEC AI Resume Engine Full Stack...
echo ====================================================

cd /d "%~dp0"

echo [1/2] Starting FastAPI Backend on port 8000...
start "FUTRSEC Backend" cmd /k "py -3.12 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

echo [2/2] Starting React Frontend on port 5173...
start "FUTRSEC Frontend" cmd /k "cd frontend && npm run dev"

timeout /t 3 /nobreak >nul
echo Opening application in your default browser...
start http://localhost:5173

echo ====================================================
echo  FUTRSEC AI Resume Engine is live!
echo  Frontend UI:       http://localhost:5173
echo  Backend API and Docs: http://localhost:8000/docs
echo ====================================================
