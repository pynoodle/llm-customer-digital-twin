#!/bin/bash

# 디지털 트윈 서베이 시스템 실행 스크립트 (macOS/Linux)

echo "🤖 디지털 트윈 서베이 시스템"
echo "======================================"

# 가상환경 확인
if [ ! -d "venv" ]; then
    echo "⚠️  가상환경이 없습니다. 생성 중..."
    python3 -m venv venv
    echo "✅ 가상환경 생성 완료"
fi

# 가상환경 활성화
echo "🔄 가상환경 활성화 중..."
source venv/bin/activate

# 의존성 설치 확인
if [ ! -f "venv/installed" ]; then
    echo "📦 의존성 설치 중..."
    pip install -r requirements.txt
    touch venv/installed
    echo "✅ 의존성 설치 완료"
fi

# .env 파일 확인
if [ ! -f ".env" ]; then
    echo "⚠️  .env 파일이 없습니다."
    echo "📝 .env.example을 .env로 복사하고 API 키를 입력해주세요."
    cp .env.example .env
    echo ""
    echo "다음 명령어로 .env 파일을 편집하세요:"
    echo "  nano .env"
    echo "  또는"
    echo "  code .env"
    echo ""
    read -p "API 키를 입력하셨나요? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ 종료합니다. API 키를 입력 후 다시 실행해주세요."
        exit 1
    fi
fi

# Streamlit 실행
echo ""
echo "🚀 Streamlit 앱을 실행합니다..."
echo "🌐 브라우저에서 http://localhost:8501 을 엽니다"
echo ""
echo "종료하려면 Ctrl+C를 누르세요"
echo "======================================"
echo ""

streamlit run app.py
