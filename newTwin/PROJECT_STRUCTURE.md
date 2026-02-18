# 📁 프로젝트 구조

```
digital-twin-survey-system/
│
├── 📄 app.py                          # Streamlit GUI 메인 애플리케이션
├── 📄 digital_twin_survey_system.py   # 백엔드 로직 (핵심 클래스들)
│
├── 📋 requirements.txt                # Python 의존성
├── 📋 .env.example                   # 환경변수 템플릿
├── 📋 .gitignore                     # Git 제외 파일
├── 📋 .cursorrules                   # Cursor AI 설정
│
├── 🚀 run.sh                         # 실행 스크립트 (macOS/Linux)
├── 🚀 run.bat                        # 실행 스크립트 (Windows)
│
├── 📖 README.md                      # 전체 프로젝트 문서
├── 📖 README_CURSOR.md              # Cursor 사용 가이드
├── 📖 QUICKSTART.md                 # 5분 퀵스타트 가이드
└── 📖 PROJECT_STRUCTURE.md          # 이 파일
```

## 📄 주요 파일 설명

### 🎨 프론트엔드

**app.py** (Streamlit GUI)
- 웹 기반 인터페이스
- 5개 주요 탭:
  1. 👥 페르소나 선택
  2. 📋 서베이
  3. 🎤 인터뷰
  4. 🧪 실험
  5. 📊 결과 분석
- 실시간 진행 상태 표시
- 결과 다운로드 기능

### ⚙️ 백엔드

**digital_twin_survey_system.py**

주요 클래스:

1. **SimulationConfig**
   - API 키, 모델, 파라미터 관리
   
2. **PersonaDataLoader**
   - Twin-2K-500 데이터셋 로딩
   - 페르소나 샘플링 및 필터링
   
3. **QuestionTemplate**
   - 서베이 질문 템플릿
   - 인터뷰 가이드
   - 행동 실험 시나리오
   
4. **DigitalTwinSimulator**
   - LLM API 호출
   - 페르소나 기반 응답 시뮬레이션
   - 서베이/인터뷰/실험 수행
   
5. **ResultAnalyzer**
   - 결과 집계 및 분석
   - 감성 분석
   - 데이터 내보내기

## 🔄 데이터 흐름

```
1. 사용자 입력 (app.py)
   ↓
2. 페르소나 선택 (PersonaDataLoader)
   ↓
3. 질문 선택 (QuestionTemplate)
   ↓
4. LLM 시뮬레이션 (DigitalTwinSimulator)
   ↓
5. 결과 분석 (ResultAnalyzer)
   ↓
6. 결과 표시 및 다운로드 (app.py)
```

## 🎯 핵심 기능 흐름

### 서베이 실행
```python
1. 페르소나 로딩
   loader = PersonaDataLoader(config)
   personas = loader.get_random_personas(n=10)

2. 질문 선택
   questions = QuestionTemplate.get_questions_by_category("product_feedback")

3. 시뮬레이션 실행
   simulator = DigitalTwinSimulator(config)
   results = simulator.conduct_survey(persona, questions, context)

4. 결과 분석
   analyzer = ResultAnalyzer()
   df = analyzer.aggregate_survey_results(results)
   sentiment = analyzer.analyze_sentiment(responses)
```

## 📦 생성되는 파일들

### 실행 중 생성:
- `.env` - API 키 저장
- `venv/` - Python 가상환경

### 결과 파일:
- `survey_results_*.json` - 서베이 원본 데이터
- `survey_results_*.csv` - 서베이 분석용 데이터
- `interview_results_*.json` - 인터뷰 대화 기록
- `experiment_results_*.json` - 실험 결과

## 🔧 설정 파일들

### .env
```
ANTHROPIC_API_KEY=sk-ant-...
DEFAULT_MODEL=claude-sonnet-4-20250514
DEFAULT_TEMPERATURE=0.7
```

### .cursorrules
- Cursor AI의 프로젝트 이해를 돕는 규칙
- 코딩 스타일 가이드
- 자주 사용하는 패턴

### .gitignore
- Python 캐시 파일
- 가상환경
- API 키
- 결과 파일

## 🚀 실행 스크립트

### run.sh (macOS/Linux)
1. 가상환경 확인/생성
2. 의존성 설치
3. .env 파일 확인
4. Streamlit 실행

### run.bat (Windows)
- run.sh와 동일한 기능 (Windows용)

## 📚 문서 파일들

### README.md
- 전체 프로젝트 개요
- 상세 사용 가이드
- API 문서
- 예시 코드

### README_CURSOR.md
- Cursor 전용 가이드
- 단축키 및 팁
- AI와 협업하는 방법
- 문제 해결

### QUICKSTART.md
- 5분 시작 가이드
- 필수 단계만
- 빠른 예시

## 🎨 커스터마이징 포인트

### 쉬운 수정:
- 질문 템플릿 추가 (`QuestionTemplate` 클래스)
- UI 색상 변경 (`app.py` CSS 부분)
- 모델 파라미터 조정 (`SimulationConfig`)

### 중급 수정:
- 새로운 분석 기능 추가 (`ResultAnalyzer`)
- 페르소나 필터링 로직 (`PersonaDataLoader`)
- 결과 시각화 추가 (`app.py`)

### 고급 수정:
- 새로운 실험 타입
- 다중 LLM 지원
- 데이터베이스 연동
- API 엔드포인트 추가

## 🔗 외부 연동

### 필수:
- Anthropic API (claude.ai)
- HuggingFace (Twin-2K-500 데이터셋)

### 옵션:
- OpenAI API (대체 LLM)
- Google Drive (결과 저장)
- Slack (알림)

## 📊 확장 가능성

### 현재 구조로 쉽게 추가 가능:
1. ✅ 실시간 대시보드
2. ✅ 과거 결과 관리
3. ✅ 다중 사용자 지원
4. ✅ 결과 공유 기능
5. ✅ 자동 보고서 생성

### 아키텍처 변경 필요:
1. 데이터베이스 연동
2. 인증 시스템
3. RESTful API
4. 클라우드 배포

## 🎓 학습 경로

### 초보자:
1. QUICKSTART.md 따라하기
2. 기본 서베이 실행
3. Cursor AI로 간단한 수정

### 중급자:
1. README_CURSOR.md 숙독
2. 커스텀 질문/템플릿 추가
3. 결과 시각화 구현

### 고급자:
1. 새로운 기능 모듈 추가
2. 성능 최적화
3. 아키텍처 확장

---

**💡 Tip**: Cursor AI에게 "프로젝트 구조를 설명해줘"라고 물어보면 이 내용을 기반으로 설명해줄 거예요!
