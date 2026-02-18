# 🤖 디지털 트윈 서베이/인터뷰/시뮬레이션 시스템

Twin-2K-500 데이터셋을 활용한 실리콘 샘플(Silicon Sample) 기반 조사 도구입니다.

## 📋 개요

이 시스템은 2,058명의 실제 미국 참가자 데이터를 기반으로 한 디지털 트윈을 생성하여:
- **서베이(Survey)**: 대규모 설문조사 시뮬레이션
- **인터뷰(Interview)**: 심층 인터뷰 수행
- **실험(Experiment)**: 행동 경제학 실험 실행

LLM을 활용하여 실제 사람처럼 응답하는 가상 응답자를 시뮬레이션합니다.

## 🎯 주요 기능

### 1. 페르소나 관리
- Twin-2K-500 데이터셋 자동 로딩
- 조건별 페르소나 필터링
- 랜덤 샘플링

### 2. 질문 템플릿
- **서베이 카테고리**:
  - 제품 피드백 (Product Feedback)
  - 브랜드 인식 (Brand Perception)
  - 소비자 행동 (Consumer Behavior)
  - 라이프스타일 (Lifestyle)

- **인터뷰 가이드**:
  - 사용자 경험 (User Experience)
  - 의사결정 과정 (Decision Making)

- **행동 실험**:
  - 가격 민감도 (Price Sensitivity)
  - 프레이밍 효과 (Framing Effect)
  - 사회적 증거 (Social Proof)

### 3. LLM 시뮬레이션
- Anthropic Claude 지원
- OpenAI GPT 지원 (주석 처리됨)
- 페르소나 기반 맥락적 응답 생성

### 4. 결과 분석
- 응답 데이터 집계 및 DataFrame 변환
- 기본 감성 분석
- JSON/Excel 내보내기

## 🚀 시작하기

### 1. 설치

```bash
# 레포지토리 클론
git clone [your-repo-url]
cd digital-twin-survey

# 의존성 설치
pip install -r requirements.txt
```

### 2. API 키 설정

`.env` 파일을 생성하고 API 키를 추가하세요:

```bash
# Anthropic Claude 사용 시
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# 또는 OpenAI 사용 시
# OPENAI_API_KEY=your_openai_api_key_here
```

또는 환경변수로 직접 설정:

```bash
export ANTHROPIC_API_KEY='your-api-key'
```

### 3. 실행

```bash
python digital_twin_survey_system.py
```

## 💻 사용 예제

### 기본 사용

```python
from digital_twin_survey_system import *

# 1. 설정
config = SimulationConfig(
    api_key="your-api-key",
    model="claude-sonnet-4-20250514"
)

# 2. 데이터 로딩
loader = PersonaDataLoader(config)
loader.load_dataset()

# 3. 페르소나 선택
personas = loader.get_random_personas(n=10)

# 4. 시뮬레이터 초기화
simulator = DigitalTwinSimulator(config)

# 5. 서베이 실행
questions = QuestionTemplate.get_questions_by_category("product_feedback")
results = simulator.conduct_survey(personas[0], questions)

print(results)
```

### 커스텀 서베이 생성

```python
# 자신만의 질문 만들기
custom_questions = [
    "이 서비스의 가장 큰 장점은 무엇인가요?",
    "개선이 필요한 부분이 있다면?",
    "다른 서비스와 비교했을 때 어떤가요?"
]

custom_survey = QuestionTemplate.create_custom_survey(
    questions=custom_questions,
    title="신규 서비스 피드백 조사"
)

# 여러 페르소나에게 서베이 실행
results = []
for persona in personas:
    result = simulator.conduct_survey(
        persona, 
        custom_questions,
        survey_context="새로운 배달 앱 서비스에 대한 피드백"
    )
    results.append(result)
```

### 조건별 페르소나 필터링

```python
# 20-30세 여성 페르소나만 선택
young_females = loader.filter_personas({
    "age_range": (20, 30),
    "gender": "Female"
})

# 특정 조건의 페르소나로 타겟 조사
results = []
for persona in young_females[:10]:  # 10명만
    result = simulator.conduct_survey(persona, questions)
    results.append(result)
```

### 인터뷰 수행

```python
# 인터뷰 가이드 선택
interview_guide = QuestionTemplate.INTERVIEW_GUIDES["user_experience"]

# 심층 인터뷰 진행
interview_result = simulator.conduct_interview(
    personas[0], 
    interview_guide
)

# 대화 내용 확인
for turn in interview_result["conversation"]:
    print(f"[{turn['type']}]")
    print(f"Q: {turn['interviewer']}")
    if 'respondent' in turn:
        print(f"A: {turn['respondent']}\n")
```

### 행동 실험

```python
# 가격 민감도 실험
experiment = QuestionTemplate.BEHAVIORAL_EXPERIMENTS["price_sensitivity"]

experiment_results = []
for persona in personas:
    result = simulator.run_experiment(persona, experiment)
    experiment_results.append(result)

# 결과 분석
# 각 조건별 선택 비율 계산 등
```

### 결과 분석 및 저장

```python
analyzer = ResultAnalyzer()

# DataFrame으로 변환
df = analyzer.aggregate_survey_results(results)
print(df.head())

# 감성 분석
responses = [r['response'] for result in results 
             for r in result['responses'] if r.get('response')]
sentiment = analyzer.analyze_sentiment(responses)
print(f"긍정: {sentiment['positive']}, 부정: {sentiment['negative']}")

# 결과 저장
analyzer.export_results(results, "my_survey_results.json")

# Excel로 저장하려면
df.to_excel("survey_results.xlsx", index=False)
```

## 📊 데이터셋 정보

### Twin-2K-500 데이터셋

- **참가자 수**: 2,058명 (미국 대표 표본)
- **질문 수**: 500개 이상
- **웨이브**: 4개 (주간 간격)
- **포함 내용**:
  - 인구통계학적 정보
  - 심리학적 척도
  - 경제적 선호도
  - 성격 특성
  - 인지 능력
  - 행동 경제학 실험

### 데이터셋 구조

```python
{
    'full_persona': {
        'data': [
            {
                'id': 'persona_001',
                'persona_text': '상세한 페르소나 설명...',
                'persona_json': {...},  # 구조화된 정보
                # ... 기타 필드
            },
            ...
        ]
    }
}
```

## 🔧 고급 설정

### OpenAI 사용하기

코드에서 Anthropic 관련 부분을 주석 처리하고 OpenAI 부분의 주석을 해제하세요:

```python
# digital_twin_survey_system.py 파일에서

# import anthropic  # 주석 처리
import openai  # 주석 해제

class DigitalTwinSimulator:
    def __init__(self, config: SimulationConfig):
        # self.client = anthropic.Anthropic(api_key=config.api_key)  # 주석 처리
        self.client = openai.OpenAI(api_key=config.api_key)  # 주석 해제
```

### 시뮬레이션 파라미터 조정

```python
config = SimulationConfig(
    api_key="your-key",
    model="claude-sonnet-4-20250514",
    temperature=0.8,  # 더 창의적인 응답 (0.0~1.0)
    max_tokens=3000,  # 더 긴 응답
)
```

## 📈 활용 사례

### 1. 제품 개발
- 새 기능에 대한 사용자 반응 테스트
- 타겟 세그먼트별 니즈 파악
- 프로토타입 피드백 수집

### 2. 마케팅 리서치
- 광고 메시지 테스트
- 브랜드 포지셔닝 검증
- 가격 전략 수립

### 3. UX 리서치
- 사용자 여정 맵핑
- 페인 포인트 발견
- 개선 아이디어 도출

### 4. 학술 연구
- 행동 경제학 실험
- 의사결정 연구
- 소비자 심리 분석

## ⚠️ 주의사항

### 데이터 품질
- 시뮬레이션 결과는 실제 데이터로 검증 필요
- LLM의 한계와 편향성 인지
- 대표성 있는 샘플 선택 중요

### API 비용
- 대규모 시뮬레이션 시 API 비용 발생
- 토큰 사용량 모니터링 권장
- 테스트는 소규모로 시작

### 윤리적 고려
- 실제 사람의 데이터를 바탕으로 함을 명시
- 연구 목적으로만 사용
- 개인정보 보호 원칙 준수

## 🛠️ 확장 아이디어

### 추가 가능한 기능
1. **시각화 대시보드**: Streamlit/Dash로 웹 인터페이스 구축
2. **고급 분석**: 토픽 모델링, 클러스터링
3. **실시간 모니터링**: 진행 상황 추적
4. **A/B 테스트**: 자동화된 실험 설계
5. **보고서 생성**: 자동 인사이트 추출

### 통합 가능한 도구
- Google Sheets/Excel 자동 업데이트
- Slack 알림
- Tableau/PowerBI 연동
- MLflow 실험 추적

## 📚 참고 자료

- [Twin-2K-500 Dataset](https://huggingface.co/datasets/LLM-Digital-Twin/Twin-2K-500)
- [GitHub Repository](https://github.com/tianyipeng-lab/Digital-Twin-Simulation)
- [Research Paper](https://arxiv.org/abs/2505.17479)
- [Anthropic API Docs](https://docs.anthropic.com/)

## 🤝 기여하기

개선 아이디어나 버그 리포트는 언제나 환영합니다!

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다.

## 💬 문의

질문이나 제안사항이 있으시면 이슈를 등록해주세요.

---

**Happy Simulating! 🚀**
