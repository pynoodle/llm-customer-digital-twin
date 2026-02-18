@echo off
chcp 65001 >nul
echo ======================================================================
echo 🚀 디지털 트윈 설문/인터뷰 시스템 설치 스크립트 (Windows)
echo ======================================================================
echo.

REM Python 확인
echo 1️⃣ Python 버전 확인 중...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python이 설치되지 않았습니다.
    echo Python 3.8 이상을 설치하세요: https://www.python.org/downloads/
    pause
    exit /b 1
)

python --version
echo ✅ Python 발견
echo.

REM 가상환경 생성
echo 2️⃣ 가상환경 설정
set /p CREATE_VENV="가상환경을 생성하시겠습니까? (권장) (y/n): "

if /i "%CREATE_VENV%"=="y" (
    echo 가상환경 생성 중...
    python -m venv venv
    
    if exist venv\Scripts\activate.bat (
        call venv\Scripts\activate.bat
        echo ✅ 가상환경 활성화됨
    ) else (
        echo ❌ 가상환경 생성 실패
        pause
        exit /b 1
    )
) else (
    echo ⚠️ 가상환경 없이 진행합니다.
)
echo.

REM 패키지 설치
echo 3️⃣ 필수 패키지 설치 중...
python -m pip install --upgrade pip
pip install -r requirements.txt

if errorlevel 1 (
    echo ❌ 패키지 설치 실패
    pause
    exit /b 1
)
echo ✅ 패키지 설치 완료
echo.

REM .env 파일 생성
echo 4️⃣ 환경 설정
if not exist .env (
    copy .env.example .env >nul
    echo ✅ .env 파일 생성됨
    echo ⚠️ .env 파일을 열어서 OPENAI_API_KEY를 설정하세요!
) else (
    echo ⚠️ .env 파일이 이미 존재합니다.
)
echo.

REM 결과 디렉토리 생성
echo 5️⃣ 결과 저장 디렉토리 생성
if not exist results mkdir results
echo ✅ results\ 디렉토리 생성됨
echo.

REM 설치 완료
echo ======================================================================
echo ✅ 설치 완료!
echo ======================================================================
echo.
echo 다음 단계:
echo   1. .env 파일을 편집하여 OPENAI_API_KEY를 설정하세요
echo   2. 빠른 데모 실행: python demo.py
echo   3. 메인 프로그램 실행: python digital_twin_survey_system.py
echo.

if /i "%CREATE_VENV%"=="y" (
    echo 가상환경 활성화 명령어:
    echo   venv\Scripts\activate.bat
    echo.
)

echo 문서:
echo   - README.md: 전체 가이드
echo   - QUICKSTART.md: 빠른 시작
echo   - PROJECT_STRUCTURE.md: 프로젝트 구조
echo.
echo 즐거운 설문 조사 되세요! 🎉
echo.
pause
