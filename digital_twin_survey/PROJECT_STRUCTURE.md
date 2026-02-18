# 📁 프로젝트 구조

```
digital_twin_survey/
│
├── 📄 README.md                          # 전체 문서 및 가이드
├── 📄 QUICKSTART.md                      # 빠른 시작 가이드
├── 📄 PROJECT_STRUCTURE.md               # 이 파일
│
├── ⚙️ requirements.txt                   # Python 패키지 목록
├── ⚙️ .env.example                       # 환경 변수 템플릿
│
├── 🔧 핵심 시스템
│   └── digital_twin_survey_system.py    # 메인 시스템 클래스
│
├── 🎯 실행 스크립트
│   ├── demo.py                           # 빠른 데모 (3명, 샘플 질문)
│   └── advanced_examples.py              # 고급 예제 (타겟팅, 비교)
│
└── 📊 분석 도구
    └── analysis_tools.py                 # 결과 분석 및 시각화

```

## 📄 파일별 설명

### 1. 핵심 시스템

#### `digital_twin_survey_system.py` (21KB)
**역할**: 전체 시스템의 핵심 클래스

**주요 클래스**:
- `DigitalTwinSurveySystem`: 메인 시스템 클래스

**주요 기능**:
```python
load_dataset()                    # 데이터셋 로드
display_personas_summary()        # 페르소나 미리보기
select_personas_interactive()     # 대화형 응답자 선택
select_personas_by_criteria()     # 필터링으로 선택
create_survey()                   # 설문조사 생성
create_interview()                # 인터뷰 생성
conduct_survey()                  # 설문 실시
conduct_interview()               # 인터뷰 실시
analyze_survey_results()          # 결과 분석
export_results()                  # 결과 내보내기
```

**사용 예시**:
```python
from digital_twin_survey_system import DigitalTwinSurveySystem

system = DigitalTwinSurveySystem(api_key)
system.load_dataset()
system.select_personas_interactive()
survey = system.create_survey([...])
results = system.conduct_survey(survey)
```

---

### 2. 실행 스크립트

#### `demo.py` (4KB)
**역할**: 빠른 데모 실행

**특징**:
- 사전 정의된 샘플 질문
- 3명 고정 응답자
- 2-3분 완료
- 초보자 친화적

**실행 방법**:
```bash
python demo.py
```

**출력**:
- `demo_results_survey_1.csv`
- `demo_results_interview_1.csv`

---

#### `advanced_examples.py` (8KB)
**역할**: 고급 활용 예제

**포함된 예제**:
1. **타겟 설문** (`targeted_survey_example`)
   - 특정 직군 필터링 (예: 기술 직종)
   - 맞춤형 설문 설계
   - 후속 인터뷰

2. **그룹 비교** (`demographic_comparison_example`)
   - 연령대별 비교
   - 그룹 간 통계 분석
   - 시각화 데이터 생성

**실행 방법**:
```bash
python advanced_examples.py
```

**출력**:
- `tech_survey_survey_1.csv`
- `tech_survey_complete.xlsx`
- `demographic_comparison.xlsx`

---

### 3. 분석 도구

#### `analysis_tools.py` (13KB)
**역할**: 결과 분석 및 시각화

**주요 클래스**:

**1. SurveyAnalyzer**
```python
# 설문 결과 분석
analyzer = SurveyAnalyzer('results.csv')
analyzer.basic_statistics()           # 기본 통계
analyzer.distribution_plot()          # 분포 차트
analyzer.correlation_heatmap()        # 상관관계 히트맵
analyzer.response_patterns()          # 응답 패턴
analyzer.summary_report()             # 종합 리포트
```

**2. InterviewAnalyzer**
```python
# 인터뷰 결과 분석
analyzer = InterviewAnalyzer('interview.csv')
analyzer.word_frequency()             # 단어 빈도
analyzer.response_length_analysis()   # 응답 길이
analyzer.sentiment_indicators()       # 감성 지표
analyzer.summary_report()             # 종합 리포트
```

**실행 방법**:
```bash
python analysis_tools.py
```

**출력**:
- `*_distribution.png` - 응답 분포 차트
- `*_correlation.png` - 상관관계 히트맵
- `*_report.txt` - 분석 리포트

---

### 4. 설정 파일

#### `requirements.txt` (354B)
**필수 패키지 목록**:
```
pandas>=2.0.0
numpy>=1.24.0
datasets>=2.14.0
openai>=1.0.0
python-dotenv>=1.0.0
matplotlib>=3.7.0
seaborn>=0.12.0
tqdm>=4.65.0
```

**설치**:
```bash
pip install -r requirements.txt
```

---

#### `.env.example` (528B)
**환경 변수 템플릿**

**설정 항목**:
```bash
OPENAI_API_KEY=your_key_here
MODEL_NAME=gpt-4o-mini
REQUEST_DELAY=0.5
MAX_RETRIES=3
RESULTS_DIR=./results
LOG_LEVEL=INFO
```

**사용 방법**:
```bash
cp .env.example .env
# .env 파일 편집
```

---

## 🔄 일반적인 워크플로우

### 워크플로우 1: 빠른 테스트
```
1. demo.py 실행
   ↓
2. 결과 확인 (CSV)
   ↓
3. analysis_tools.py로 분석
```

### 워크플로우 2: 맞춤형 설문
```
1. digital_twin_survey_system.py 실행
   ↓
2. 응답자 선택 (필터링/샘플링)
   ↓
3. 질문 입력 or 샘플 사용
   ↓
4. 설문 실시 (테스트 → 전체)
   ↓
5. 결과 분석 및 저장
```

### 워크플로우 3: 고급 분석
```
1. advanced_examples.py 실행
   ↓
2. 타겟 그룹 설문
   ↓
3. 그룹 간 비교
   ↓
4. Excel 리포트 생성
```

---

## 📊 데이터 흐름

```
Twin-2K-500 Dataset (Hugging Face)
         ↓
[데이터셋 로드]
         ↓
[페르소나 선택]
    ↙        ↘
[설문]      [인터뷰]
    ↓          ↓
[ChatGPT API 호출]
    ↓          ↓
[응답 생성]
    ↓          ↓
[결과 저장 (CSV)]
    ↓          ↓
[분석 및 시각화]
    ↓
[리포트 생성]
```

---

## 🎨 커스터마이징 가이드

### 1. 프롬프트 수정
```python
# digital_twin_survey_system.py 수정
def _get_survey_response(self, ...):
    system_prompt = """
    여기에 커스텀 프롬프트 작성
    """
```

### 2. 필터링 로직 추가
```python
# select_personas_by_criteria 메서드 확장
def select_personas_by_criteria(self, criteria):
    # 연령, 직업, 지역 등 다양한 필터 추가
    pass
```

### 3. 분석 메트릭 추가
```python
# analysis_tools.py에 새로운 분석 클래스 추가
class CustomAnalyzer:
    def custom_metric(self):
        # 새로운 분석 지표
        pass
```

---

## 💾 결과 파일 형식

### 설문 결과 (CSV)
```csv
participant_id,persona_index,Q1,Q1_reasoning,Q2,Q2_reasoning,...
P001,0,5,"I enjoy...",6,"High quality...",...
P002,1,3,"Some aspects...",4,"Mixed experience...",...
```

### 인터뷰 결과 (CSV)
```csv
participant_id,persona_index,Q1,Q2,Q3,...
P001,0,"I've always...","I try to...","Remote work...",...
P002,1,"My interest...","It's challenging...","I appreciate...",...
```

---

## 🔧 확장 가능성

### 추가할 수 있는 기능
1. **실시간 대시보드** - Streamlit/Dash 통합
2. **데이터베이스 연동** - PostgreSQL/MongoDB
3. **배치 처리** - Celery/Redis 큐
4. **고급 NLP 분석** - BERT 임베딩, 토픽 모델링
5. **A/B 테스트** - 질문 변형 실험
6. **다국어 지원** - 자동 번역 통합
7. **웹 인터페이스** - Flask/FastAPI API

---

## 📚 참고 자료

- **데이터셋**: https://huggingface.co/datasets/LLM-Digital-Twin/Twin-2K-500
- **논문**: arXiv:2505.17479
- **OpenAI API**: https://platform.openai.com/docs

---

## 🆘 트러블슈팅

### 문제: 데이터셋 로드 실패
```bash
pip install --upgrade datasets
rm -rf ~/.cache/huggingface/datasets
```

### 문제: API 오류
```python
# REQUEST_DELAY 증가
time.sleep(1.0)  # 기본값 0.5에서 증가
```

### 문제: 메모리 부족
```python
# 배치 크기 줄이기
batch_size = 10  # 기본값 50에서 감소
```

---

이 구조로 프로젝트를 쉽게 이해하고 확장할 수 있습니다! 🚀
