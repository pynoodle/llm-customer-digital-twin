@echo off
REM 디지털 트윈 서베이 시스템 실행 스크립트 (Windows)

echo 🤖 디지털 트윈 서베이 시스템
echo ======================================

REM 가상환경 확인
if not exist "venv\" (
    echo ⚠️  가상환경이 없습니다. 생성 중...
    python -m venv venv
    echo ✅ 가상환경 생성 완료
)

REM 가상환경 활성화
echo 🔄 가상환경 활성화 중...
call venv\Scripts\activate.bat

REM 의존성 설치 확인
if not exist "venv\installed" (
    echo 📦 의존성 설치 중...
    pip install -r requirements.txt
    echo. > venv\installed
    echo ✅ 의존성 설치 완료
)

REM .env 파일 확인
if not exist ".env" (
    echo ⚠️  .env 파일이 없습니다.
    echo 📝 .env.example을 .env로 복사하고 API 키를 입력해주세요.
    copy .env.example .env
    echo.
    echo 다음 명령어로 .env 파일을 편집하세요:
    echo   notepad .env
    echo   또는
    echo   code .env
    echo.
    set /p response="API 키를 입력하셨나요? (y/n): "
    if /i not "%response%"=="y" (
        echo ❌ 종료합니다. API 키를 입력 후 다시 실행해주세요.
        exit /b 1
    )
)

REM Streamlit 실행
echo.
echo 🚀 Streamlit 앱을 실행합니다...
echo 🌐 브라우저에서 http://localhost:8501 을 엽니다
echo.
echo 종료하려면 Ctrl+C를 누르세요
echo ======================================
echo.

streamlit run app.py
