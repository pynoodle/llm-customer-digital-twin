# 🤖 디지털 트윈 설문/인터뷰 시스템 사용 가이드

Twin-2K-500 데이터셋을 활용한 AI 기반 설문조사 및 인터뷰 플랫폼입니다.

## 📋 목차
1. [시스템 개요](#시스템-개요)
2. [설치 방법](#설치-방법)
3. [사용 방법](#사용-방법)
4. [주요 기능](#주요-기능)
5. [예제](#예제)
6. [FAQ](#faq)

---

## 🎯 시스템 개요

이 시스템은 2,058명의 실제 사람들의 설문 응답 데이터를 기반으로 "디지털 트윈"을 생성하고, 
ChatGPT API를 통해 새로운 설문 질문에 답변하거나 인터뷰에 응답하게 합니다.

### 주요 특징
- ✅ 실제 설문 데이터 기반 페르소나
- ✅ 1-7 척도 설문조사 지원
- ✅ 개방형 인터뷰 질문 지원
- ✅ 응답자 선택 기능 (필터링, 샘플링 등)
- ✅ 결과 분석 및 내보내기

### 데이터셋 정보
- **출처**: Hugging Face - LLM-Digital-Twin/Twin-2K-500
- **참가자 수**: 2,058명
- **질문 수**: 500개 이상
- **포함 데이터**: 인구통계, 심리, 경제, 성격, 인지 측정치

---

## 💻 설치 방법

### 1. 환경 설정

```bash
# Python 3.8 이상 필요
python --version

# 가상환경 생성 (권장)
python -m venv venv

# 가상환경 활성화
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate
```

### 2. 패키지 설치

```bash
pip install -r requirements.txt
```

### 3. API 키 설정

OpenAI API 키가 필요합니다:

**방법 1: 환경 변수 설정**
```bash
# .env 파일 생성
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

**방법 2: 실행 시 입력**
- 프로그램 실행 시 API 키를 입력하라는 프롬프트가 나타납니다.

---

## 🚀 사용 방법

### 기본 실행

```bash
python digital_twin_survey_system.py
```

### 단계별 사용 흐름

```
1. 데이터셋 로딩
   ↓
2. 페르소나 미리보기 (최대 5명)
   ↓
3. 응답자 선택
   - 전체 선택
   - 개별 선택 (인덱스)
   - 범위 선택 (0-20)
   - 랜덤 샘플링
   - 키워드 필터링
   ↓
4. 조사 유형 선택
   - 설문조사 (1-7 척도)
   - 인터뷰 (개방형)
   - 둘 다
   ↓
5. 질문 입력
   - 샘플 질문 사용
   - 직접 입력
   ↓
6. 조사 실시
   - 테스트 실행 (3명)
   - 전체 실행
   ↓
7. 결과 확인 및 저장
```

---

## 🎨 주요 기능

### 1. 페르소나 선택

#### 전체 선택
```python
# 모든 페르소나 선택 (최대 100명)
선택 방법: 1
```

#### 개별 선택
```python
# 특정 인덱스의 페르소나 선택
선택 방법: 2
인덱스: 0,5,10,15,20
```

#### 범위 선택
```python
# 0번부터 50번까지 선택
선택 방법: 3
범위: 0-50
```

#### 랜덤 샘플링
```python
# 무작위로 20명 선택
선택 방법: 4
개수: 20
```

#### 키워드 필터링
```python
# 특정 키워드를 포함하는 페르소나 선택
선택 방법: 5
키워드: engineer
```

### 2. 설문조사 (Survey)

#### 특징
- 1-7 리커트 척도 사용
- 각 응답에 대한 이유 제공
- 자동 통계 분석

#### 예시 질문
```
1. How satisfied are you with your current job? (1-7)
2. How likely are you to recommend this product? (1-7)
3. Rate your agreement: "AI will benefit society" (1-7)
```

#### 결과 형식
```
participant_id | Q1 | Q1_reasoning | Q2 | Q2_reasoning | ...
P001          | 5  | "I enjoy..."  | 6  | "High qual..." | ...
P002          | 3  | "Some asp..." | 4  | "Mixed exp..." | ...
```

### 3. 인터뷰 (Interview)

#### 특징
- 개방형 질문
- 2-4 문장 자연스러운 응답
- 페르소나 특성 반영

#### 예시 질문
```
1. What motivated you to choose your current career path?
2. How do you balance work and personal life?
3. What are your thoughts on remote work?
```

#### 결과 형식
```
participant_id | Q1 | Q2 | Q3
P001          | "I've always..." | "I try to..." | "Remote work..."
P002          | "My interest..." | "It's chall..." | "I appreciate..."
```

---

## 📊 예제

### 예제 1: 간단한 설문조사

```python
from digital_twin_survey_system import DigitalTwinSurveySystem
import os

# 시스템 초기화
api_key = os.getenv('OPENAI_API_KEY')
system = DigitalTwinSurveySystem(api_key)

# 데이터 로드
system.load_dataset()

# 10명 랜덤 선택
import random
system.selected_personas = random.sample(range(100), 10)

# 설문 생성
survey = system.create_survey([
    {"question": "How satisfied are you with your job?", "scale": "1-7"},
    {"question": "Rate your work-life balance", "scale": "1-7"}
])

# 설문 실시
results = system.conduct_survey(survey)

# 결과 분석
analysis = system.analyze_survey_results(results)

# 결과 저장
system.export_results('my_survey', format='csv')
```

### 예제 2: 인터뷰 진행

```python
# 시스템 초기화 (위와 동일)
system = DigitalTwinSurveySystem(api_key)
system.load_dataset()

# 키워드로 필터링
system.selected_personas = system.select_personas_by_criteria(
    {"keyword": "technology"}
)

# 인터뷰 생성
interview = system.create_interview([
    "What role does technology play in your daily life?",
    "What tech product would you recommend?",
    "How has technology changed your work?"
])

# 인터뷰 실시
results = system.conduct_interview(interview)

# 결과 저장
system.export_results('tech_interview', format='csv')
```

### 예제 3: 설문 + 인터뷰 동시 진행

```python
# 같은 응답자 그룹에 대해 설문과 인터뷰 모두 진행

# 30명 선택
system.selected_personas = list(range(30))

# 설문 실시
survey = system.create_survey([
    {"question": "Rate your job satisfaction", "scale": "1-7"}
])
survey_results = system.conduct_survey(survey)

# 동일 그룹 인터뷰
interview = system.create_interview([
    "What makes you satisfied or dissatisfied with your job?"
])
interview_results = system.conduct_interview(interview)

# 결과 비교 분석 가능
```

---

## 💡 팁 & 권장사항

### 1. API 비용 관리
```python
# 테스트는 항상 소수로!
test_personas = system.selected_personas[:3]
results = system.conduct_survey(survey, test_personas)
```

### 2. 질문 설계
```
좋은 설문 질문:
✅ "Rate your satisfaction with remote work (1-7)"
✅ "How likely are you to change jobs? (1-7)"

좋은 인터뷰 질문:
✅ "What motivated your career choice?"
✅ "Describe your ideal work environment"
```

### 3. 페르소나 선택
```python
# 특정 그룹 분석 예시
# 젊은 층만 선택
young_personas = system.select_personas_by_criteria(
    {"keyword": "age: 18-30"}
)

# 특정 직업군 선택
engineers = system.select_personas_by_criteria(
    {"keyword": "engineer"}
)
```

### 4. 결과 분석
```python
# 설문 결과 통계
analysis = system.analyze_survey_results(results)

# 평균이 높은 질문 찾기
for q, stats in analysis['statistics'].items():
    if stats['mean'] > 5.5:
        print(f"{q}: 높은 만족도 (평균 {stats['mean']:.2f})")
```

---

## ❓ FAQ

### Q1: API 비용이 얼마나 드나요?
**A**: GPT-4o-mini 기준으로 응답자 1명당 약 $0.001-0.002 정도입니다.
- 10명 설문 (3개 질문): ~$0.02-0.05
- 100명 설문 (5개 질문): ~$0.5-1.0

### Q2: 얼마나 정확한가요?
**A**: 연구에 따르면 실제 사람의 재검사 정확도의 87-88%에 달합니다.

### Q3: 한국어 질문도 가능한가요?
**A**: 네! OpenAI API는 다국어를 지원합니다.
```python
survey = system.create_survey([
    {"question": "당신의 직업 만족도를 평가해주세요 (1-7)", "scale": "1-7"}
])
```

### Q4: 데이터셋이 로드되지 않아요
**A**: 
```bash
# Hugging Face 데이터셋 재설치
pip install --upgrade datasets

# 캐시 삭제
rm -rf ~/.cache/huggingface/datasets
```

### Q5: API 오류가 발생해요
**A**: 
- API 키 확인
- 요청 제한 확인 (RPM, TPM)
- `time.sleep()`으로 대기 시간 증가

### Q6: 결과를 Excel로 내보낼 수 있나요?
**A**: 
```python
# CSV를 Excel로 변환
import pandas as pd
df = pd.read_csv('my_survey_survey_1.csv')
df.to_excel('my_survey.xlsx', index=False)
```

### Q7: 여러 설문을 순차적으로 진행할 수 있나요?
**A**: 네, 가능합니다!
```python
# 설문 1
survey1 = system.create_survey([...])
results1 = system.conduct_survey(survey1)

# 설문 2 (동일 응답자)
survey2 = system.create_survey([...])
results2 = system.conduct_survey(survey2)
```

---

## 🔧 고급 사용법

### 커스텀 프롬프트 수정

시스템의 `_get_survey_response()` 또는 `_get_interview_response()` 메서드를 
수정하여 프롬프트를 커스터마이징할 수 있습니다.

```python
# 예: 더 창의적인 응답을 원할 경우
def _get_interview_response(self, persona_text: str, question: str):
    system_prompt = """You are a creative storyteller..."""
    # temperature를 높여 다양성 증가
    response = self.client.chat.completions.create(
        temperature=0.9,  # 기본값 0.8에서 증가
        ...
    )
```

### 배치 처리

대량의 응답자를 효율적으로 처리:

```python
# 50명씩 배치로 처리
batch_size = 50
all_results = []

for i in range(0, len(system.selected_personas), batch_size):
    batch = system.selected_personas[i:i+batch_size]
    results = system.conduct_survey(survey, batch)
    all_results.append(results)
    time.sleep(60)  # 배치 간 대기

# 결과 병합
final_results = pd.concat(all_results, ignore_index=True)
```

---

## 📞 문의 및 지원

- **이슈 리포트**: GitHub Issues
- **데이터셋 문서**: https://huggingface.co/datasets/LLM-Digital-Twin/Twin-2K-500
- **논문**: Twin-2K-500 (arXiv:2505.17479)

---

## 📄 라이선스

이 프로젝트는 교육 및 연구 목적으로 제공됩니다.
Twin-2K-500 데이터셋의 라이선스를 확인하세요.

---

## 🙏 감사의 말

이 시스템은 Toubia et al.의 Twin-2K-500 데이터셋을 기반으로 합니다.

**Citation:**
```
@article{toubia2025twin2k500,
  title={Twin-2K-500: A dataset for building digital twins of over 2,000 people},
  author={Toubia, Olivier and Gui, George Z. and Peng, Tianyi and Merlau, Daniel J. 
          and Li, Ang and Chen, Haozhe},
  journal={arXiv preprint arXiv:2505.17479},
  year={2025}
}
```
