@echo off
chcp 65001 > nul
echo ========================================
echo  🌳 ArborMind AI 실행 스크립트
echo ========================================
echo.

REM 가상환경 확인
if not exist "venv\" (
    echo [1/3] 가상환경 생성 중...
    python -m venv venv
    if errorlevel 1 (
        echo ❌ 가상환경 생성 실패. Python이 설치되어 있는지 확인하세요.
        pause
        exit /b 1
    )
    echo ✅ 가상환경 생성 완료
) else (
    echo ✅ 가상환경 이미 존재
)

echo.
echo [2/3] 가상환경 활성화 중...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ 가상환경 활성화 실패
    pause
    exit /b 1
)

echo.
echo [3/3] 패키지 확인 및 설치 중...
pip list | findstr streamlit > nul
if errorlevel 1 (
    echo Streamlit이 설치되어 있지 않습니다. 설치 중...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ❌ 패키지 설치 실패
        pause
        exit /b 1
    )
    echo ✅ 패키지 설치 완료
) else (
    echo ✅ 패키지 이미 설치됨
)

echo.
echo ========================================
echo  🚀 ArborMind AI 시작!
echo ========================================
echo.
echo 브라우저에서 http://localhost:8501 을 열어주세요.
echo 종료하려면 Ctrl+C 를 누르세요.
echo.

streamlit run app.py

pause

