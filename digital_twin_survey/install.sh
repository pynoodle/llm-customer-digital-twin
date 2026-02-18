#!/bin/bash

echo "======================================================================"
echo "🚀 디지털 트윈 설문/인터뷰 시스템 설치 스크립트"
echo "======================================================================"
echo ""

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Python 버전 확인
echo "1️⃣ Python 버전 확인 중..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3가 설치되지 않았습니다.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✅ Python ${PYTHON_VERSION} 발견${NC}"

# 최소 버전 확인 (3.8 이상)
REQUIRED_VERSION="3.8"
if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then 
    echo -e "${RED}❌ Python 3.8 이상이 필요합니다. 현재: ${PYTHON_VERSION}${NC}"
    exit 1
fi

# 가상환경 생성 여부 확인
echo ""
echo "2️⃣ 가상환경 설정"
read -p "가상환경을 생성하시겠습니까? (권장) (y/n): " CREATE_VENV

if [ "$CREATE_VENV" = "y" ] || [ "$CREATE_VENV" = "Y" ]; then
    echo "가상환경 생성 중..."
    python3 -m venv venv
    
    # 가상환경 활성화
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        echo -e "${GREEN}✅ 가상환경 활성화됨${NC}"
    else
        echo -e "${RED}❌ 가상환경 생성 실패${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️ 가상환경 없이 진행합니다.${NC}"
fi

# 패키지 설치
echo ""
echo "3️⃣ 필수 패키지 설치 중..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 패키지 설치 완료${NC}"
else
    echo -e "${RED}❌ 패키지 설치 실패${NC}"
    exit 1
fi

# .env 파일 생성
echo ""
echo "4️⃣ 환경 설정"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${GREEN}✅ .env 파일 생성됨${NC}"
    echo -e "${YELLOW}⚠️ .env 파일을 열어서 OPENAI_API_KEY를 설정하세요!${NC}"
else
    echo -e "${YELLOW}⚠️ .env 파일이 이미 존재합니다.${NC}"
fi

# 결과 디렉토리 생성
echo ""
echo "5️⃣ 결과 저장 디렉토리 생성"
mkdir -p results
echo -e "${GREEN}✅ results/ 디렉토리 생성됨${NC}"

# 설치 완료
echo ""
echo "======================================================================"
echo -e "${GREEN}✅ 설치 완료!${NC}"
echo "======================================================================"
echo ""
echo "다음 단계:"
echo "  1. .env 파일을 편집하여 OPENAI_API_KEY를 설정하세요"
echo "  2. 빠른 데모 실행: python demo.py"
echo "  3. 메인 프로그램 실행: python digital_twin_survey_system.py"
echo ""

if [ "$CREATE_VENV" = "y" ] || [ "$CREATE_VENV" = "Y" ]; then
    echo "가상환경 활성화 명령어:"
    echo "  source venv/bin/activate"
    echo ""
fi

echo "문서:"
echo "  - README.md: 전체 가이드"
echo "  - QUICKSTART.md: 빠른 시작"
echo "  - PROJECT_STRUCTURE.md: 프로젝트 구조"
echo ""
echo "즐거운 설문 조사 되세요! 🎉"
