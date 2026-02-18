"""
디지털 트윈 서베이/인터뷰/시뮬레이션 시스템
Twin-2K-500 데이터셋을 활용한 실리콘 샘플 기반 조사 도구
"""

import os
import json
import pandas as pd
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import anthropic  # or openai
from datasets import load_dataset


# ==================== 설정 ====================

@dataclass
class SimulationConfig:
    """시뮬레이션 설정"""
    api_key: str = os.getenv("ANTHROPIC_API_KEY", "")  # or OPENAI_API_KEY
    model: str = "claude-sonnet-4-20250514"  # or "gpt-4"
    temperature: float = 0.7
    max_tokens: int = 2000
    dataset_name: str = "LLM-Digital-Twin/Twin-2K-500"
    dataset_config: str = "full_persona"
    

# ==================== 데이터 로더 ====================

class PersonaDataLoader:
    """Twin-2K-500 데이터셋에서 페르소나 로딩"""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.dataset = None
        self.personas = []
        
    def load_dataset(self):
        """데이터셋 로드"""
        print(f"Loading dataset: {self.config.dataset_name}...")
        self.dataset = load_dataset(
            self.config.dataset_name, 
            self.config.dataset_config
        )
        print(f"✓ Loaded {len(self.dataset['data'])} personas")
        return self
    
    def get_persona(self, index: int) -> Dict[str, Any]:
        """특정 인덱스의 페르소나 가져오기"""
        if self.dataset is None:
            self.load_dataset()
        return self.dataset['data'][index]
    
    def get_random_personas(self, n: int = 10) -> List[Dict[str, Any]]:
        """랜덤 페르소나 샘플링"""
        if self.dataset is None:
            self.load_dataset()
        
        import random
        indices = random.sample(range(len(self.dataset['data'])), min(n, len(self.dataset['data'])))
        return [self.dataset['data'][i] for i in indices]
    
    def filter_personas(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """조건에 맞는 페르소나 필터링
        
        예시:
        - criteria = {"age_range": (20, 30), "gender": "Female"}
        """
        if self.dataset is None:
            self.load_dataset()
        
        filtered = []
        for persona in self.dataset['data']:
            match = True
            for key, value in criteria.items():
                if key in persona:
                    if isinstance(value, tuple) and len(value) == 2:
                        # 범위 조건
                        if not (value[0] <= persona[key] <= value[1]):
                            match = False
                            break
                    elif persona[key] != value:
                        match = False
                        break
            if match:
                filtered.append(persona)
        
        print(f"✓ Filtered {len(filtered)} personas matching criteria")
        return filtered


# ==================== 질문 템플릿 ====================

class QuestionTemplate:
    """서베이/인터뷰 질문 템플릿"""
    
    # 서베이 질문 카테고리
    SURVEY_QUESTIONS = {
        "product_feedback": [
            "이 제품의 가장 마음에 드는 점은 무엇인가요?",
            "이 제품을 친구에게 추천할 의향이 얼마나 되시나요? (0-10점)",
            "제품 개선을 위한 제안사항이 있으신가요?",
        ],
        "brand_perception": [
            "우리 브랜드에 대해 어떻게 생각하시나요?",
            "우리 브랜드를 한 단어로 표현한다면?",
            "경쟁사 대비 우리의 강점은 무엇이라고 생각하시나요?",
        ],
        "consumer_behavior": [
            "최근 구매 결정에 가장 큰 영향을 준 요인은?",
            "제품 구매 시 가장 중요하게 생각하는 기준은?",
            "온라인 vs 오프라인 쇼핑 중 선호하시는 것은?",
        ],
        "lifestyle": [
            "여가 시간을 주로 어떻게 보내시나요?",
            "일과 삶의 균형에 대해 어떻게 생각하시나요?",
            "건강 관리를 위해 하고 있는 활동이 있나요?",
        ],
    }
    
    # 심층 인터뷰 가이드
    INTERVIEW_GUIDES = {
        "user_experience": {
            "opening": "오늘은 여러분의 경험에 대해 깊이 있게 이야기 나누고 싶습니다.",
            "main_questions": [
                "제품/서비스를 처음 접하게 된 계기는?",
                "사용 과정에서 겪은 가장 큰 어려움은?",
                "기대했던 것과 실제 경험의 차이는?",
                "다른 사람들에게 들려주고 싶은 이야기가 있나요?",
            ],
            "probes": [
                "좀 더 자세히 말씀해 주시겠어요?",
                "그때 어떤 감정을 느끼셨나요?",
                "구체적인 예시를 들어주실 수 있나요?",
            ]
        },
        "decision_making": {
            "opening": "구매 결정 과정에 대해 이야기해 봅시다.",
            "main_questions": [
                "처음 이 제품이 필요하다고 느낀 순간은?",
                "정보 탐색은 어떻게 하셨나요?",
                "최종 결정을 내리기까지 고려한 요소들은?",
                "만약 다시 선택한다면 같은 결정을 하시겠어요?",
            ],
            "probes": [
                "그 결정이 중요했던 이유는?",
                "다른 대안들은 어떤 것들이 있었나요?",
                "주변 사람들의 의견은 어땠나요?",
            ]
        }
    }
    
    # 행동 실험 시나리오
    BEHAVIORAL_EXPERIMENTS = {
        "price_sensitivity": {
            "scenario": "동일한 제품이 두 가지 가격으로 제공됩니다.",
            "conditions": [
                {"price": 10000, "description": "일반 가격"},
                {"price": 8000, "description": "할인 가격 (20% 할인)"},
            ],
            "question": "어느 것을 구매하시겠습니까?",
        },
        "framing_effect": {
            "scenario": "새로운 치료법의 효과에 대한 설명입니다.",
            "conditions": [
                {"frame": "positive", "description": "100명 중 90명이 생존합니다"},
                {"frame": "negative", "description": "100명 중 10명이 사망합니다"},
            ],
            "question": "이 치료법을 받으시겠습니까?",
        },
        "social_proof": {
            "scenario": "새로운 레스토랑을 선택하려고 합니다.",
            "conditions": [
                {"reviews": "5개 리뷰, 평점 4.8", "popularity": "낮음"},
                {"reviews": "500개 리뷰, 평점 4.5", "popularity": "높음"},
            ],
            "question": "어느 레스토랑을 선택하시겠습니까?",
        }
    }
    
    @classmethod
    def create_custom_survey(cls, questions: List[str], title: str = "Custom Survey") -> Dict:
        """커스텀 서베이 생성"""
        return {
            "title": title,
            "questions": questions,
            "created_at": datetime.now().isoformat(),
        }
    
    @classmethod
    def get_questions_by_category(cls, category: str) -> List[str]:
        """카테고리별 질문 가져오기"""
        return cls.SURVEY_QUESTIONS.get(category, [])


# ==================== LLM 시뮬레이터 ====================

class DigitalTwinSimulator:
    """디지털 트윈 응답 시뮬레이터"""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.client = anthropic.Anthropic(api_key=config.api_key)
        # OpenAI를 사용하는 경우:
        # self.client = openai.OpenAI(api_key=config.api_key)
    
    def create_persona_prompt(self, persona_data: Dict[str, Any]) -> str:
        """페르소나 데이터를 프롬프트로 변환"""
        
        # 페르소나 정보를 텍스트로 구조화
        persona_text = "You are simulating a real person with the following characteristics:\n\n"
        
        # 주요 정보 추출 (실제 데이터셋 구조에 맞게 조정 필요)
        if 'persona_text' in persona_data:
            persona_text += persona_data['persona_text']
        elif 'persona_json' in persona_data:
            # JSON 형식인 경우
            persona_info = json.loads(persona_data['persona_json']) if isinstance(persona_data['persona_json'], str) else persona_data['persona_json']
            for key, value in persona_info.items():
                persona_text += f"- {key}: {value}\n"
        else:
            # 직접 딕셔너리 형태인 경우
            for key, value in persona_data.items():
                if key not in ['id', 'index']:
                    persona_text += f"- {key}: {value}\n"
        
        persona_text += "\nPlease respond to questions as this person would, based on their demographics, values, and personality traits."
        
        return persona_text
    
    def simulate_response(
        self, 
        persona_data: Dict[str, Any], 
        question: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """단일 질문에 대한 응답 시뮬레이션"""
        
        persona_prompt = self.create_persona_prompt(persona_data)
        
        # 시스템 프롬프트 구성
        system_prompt = f"""{persona_prompt}

Important guidelines:
- Answer authentically as this person would
- Be consistent with the persona's characteristics
- Provide natural, human-like responses
- If uncertain, reflect that in your answer"""

        # 사용자 메시지 구성
        user_message = question
        if context:
            user_message = f"Context: {context}\n\nQuestion: {question}"
        
        try:
            # Anthropic API 사용
            message = self.client.messages.create(
                model=self.config.model,
                max_tokens=self.config.max_tokens,
                temperature=self.config.temperature,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_message}
                ]
            )
            
            response = message.content[0].text
            
            # OpenAI API를 사용하는 경우:
            # response = self.client.chat.completions.create(
            #     model=self.config.model,
            #     messages=[
            #         {"role": "system", "content": system_prompt},
            #         {"role": "user", "content": user_message}
            #     ],
            #     temperature=self.config.temperature,
            #     max_tokens=self.config.max_tokens
            # )
            # response = response.choices[0].message.content
            
            return {
                "question": question,
                "response": response,
                "timestamp": datetime.now().isoformat(),
                "success": True
            }
            
        except Exception as e:
            return {
                "question": question,
                "response": None,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
                "success": False
            }
    
    def conduct_survey(
        self, 
        persona_data: Dict[str, Any], 
        questions: List[str],
        survey_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """전체 서베이 수행"""
        
        results = {
            "persona_id": persona_data.get('id', 'unknown'),
            "survey_context": survey_context,
            "started_at": datetime.now().isoformat(),
            "responses": []
        }
        
        for i, question in enumerate(questions, 1):
            print(f"  Question {i}/{len(questions)}: {question[:50]}...")
            response = self.simulate_response(persona_data, question, survey_context)
            results["responses"].append(response)
        
        results["completed_at"] = datetime.now().isoformat()
        return results
    
    def conduct_interview(
        self, 
        persona_data: Dict[str, Any], 
        interview_guide: Dict[str, Any]
    ) -> Dict[str, Any]:
        """심층 인터뷰 수행"""
        
        results = {
            "persona_id": persona_data.get('id', 'unknown'),
            "interview_type": interview_guide.get('opening', ''),
            "started_at": datetime.now().isoformat(),
            "conversation": []
        }
        
        # Opening
        opening = interview_guide.get('opening', '')
        results["conversation"].append({
            "type": "opening",
            "interviewer": opening,
            "timestamp": datetime.now().isoformat()
        })
        
        # Main questions
        for question in interview_guide.get('main_questions', []):
            response = self.simulate_response(persona_data, question)
            results["conversation"].append({
                "type": "main_question",
                "interviewer": question,
                "respondent": response["response"],
                "timestamp": response["timestamp"]
            })
            
            # 필요시 probe 질문 추가 (첫 번째 probe 사용)
            if interview_guide.get('probes'):
                probe = interview_guide['probes'][0]
                probe_response = self.simulate_response(persona_data, probe)
                results["conversation"].append({
                    "type": "probe",
                    "interviewer": probe,
                    "respondent": probe_response["response"],
                    "timestamp": probe_response["timestamp"]
                })
        
        results["completed_at"] = datetime.now().isoformat()
        return results
    
    def run_experiment(
        self, 
        persona_data: Dict[str, Any], 
        experiment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """행동 실험 수행"""
        
        # 실험 시나리오 구성
        scenario = experiment.get('scenario', '')
        conditions = experiment.get('conditions', [])
        question = experiment.get('question', '')
        
        # 랜덤하게 조건 선택 (A/B 테스트)
        import random
        selected_condition = random.choice(conditions)
        
        # 시나리오와 조건을 결합한 질문 생성
        full_question = f"{scenario}\n\n"
        for key, value in selected_condition.items():
            full_question += f"{key}: {value}\n"
        full_question += f"\n{question}"
        
        response = self.simulate_response(persona_data, full_question)
        
        return {
            "persona_id": persona_data.get('id', 'unknown'),
            "experiment_type": scenario,
            "condition": selected_condition,
            "question": question,
            "response": response["response"],
            "timestamp": response["timestamp"]
        }


# ==================== 결과 분석기 ====================

class ResultAnalyzer:
    """시뮬레이션 결과 분석"""
    
    @staticmethod
    def aggregate_survey_results(results: List[Dict[str, Any]]) -> pd.DataFrame:
        """서베이 결과 집계"""
        
        data = []
        for result in results:
            persona_id = result.get('persona_id', 'unknown')
            for response in result.get('responses', []):
                data.append({
                    'persona_id': persona_id,
                    'question': response['question'],
                    'response': response['response'],
                    'timestamp': response['timestamp']
                })
        
        df = pd.DataFrame(data)
        return df
    
    @staticmethod
    def analyze_sentiment(responses: List[str]) -> Dict[str, Any]:
        """감성 분석 (간단한 버전)"""
        # 실제로는 sentiment analysis 라이브러리 사용
        positive_words = ['좋', '훌륭', '만족', '추천', '긍정', '완벽']
        negative_words = ['나쁨', '실망', '불만', '부정', '최악', '불편']
        
        sentiments = []
        for response in responses:
            if not response:
                continue
            pos_count = sum(1 for word in positive_words if word in response)
            neg_count = sum(1 for word in negative_words if word in response)
            
            if pos_count > neg_count:
                sentiments.append('positive')
            elif neg_count > pos_count:
                sentiments.append('negative')
            else:
                sentiments.append('neutral')
        
        return {
            'positive': sentiments.count('positive'),
            'negative': sentiments.count('negative'),
            'neutral': sentiments.count('neutral'),
            'total': len(sentiments)
        }
    
    @staticmethod
    def export_results(results: List[Dict[str, Any]], filename: str = "results.json"):
        """결과를 파일로 저장"""
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"✓ Results exported to {filename}")


# ==================== 메인 실행 ====================

def main():
    """메인 실행 예제"""
    
    print("=" * 60)
    print("디지털 트윈 서베이/인터뷰/시뮬레이션 시스템")
    print("=" * 60)
    
    # 1. 설정
    config = SimulationConfig(
        api_key=os.getenv("ANTHROPIC_API_KEY"),  # 환경변수에서 가져오기
        model="claude-sonnet-4-20250514",
        temperature=0.7
    )
    
    # 2. 데이터 로더 초기화
    loader = PersonaDataLoader(config)
    loader.load_dataset()
    
    # 3. 시뮬레이터 초기화
    simulator = DigitalTwinSimulator(config)
    
    # 4-1. 서베이 예제
    print("\n" + "=" * 60)
    print("1. SURVEY SIMULATION")
    print("=" * 60)
    
    # 랜덤 페르소나 5명 선택
    sample_personas = loader.get_random_personas(n=5)
    
    # 제품 피드백 서베이 질문
    survey_questions = QuestionTemplate.get_questions_by_category("product_feedback")
    
    survey_results = []
    for i, persona in enumerate(sample_personas, 1):
        print(f"\n[Persona {i}/5] Conducting survey...")
        result = simulator.conduct_survey(
            persona, 
            survey_questions,
            survey_context="새로 출시된 스마트워치에 대한 사용자 피드백 조사"
        )
        survey_results.append(result)
        print(f"✓ Survey completed for persona {i}")
    
    # 4-2. 인터뷰 예제
    print("\n" + "=" * 60)
    print("2. INTERVIEW SIMULATION")
    print("=" * 60)
    
    interview_guide = QuestionTemplate.INTERVIEW_GUIDES["user_experience"]
    
    interview_results = []
    for i, persona in enumerate(sample_personas[:2], 1):  # 2명만 인터뷰
        print(f"\n[Persona {i}/2] Conducting interview...")
        result = simulator.conduct_interview(persona, interview_guide)
        interview_results.append(result)
        print(f"✓ Interview completed for persona {i}")
    
    # 4-3. 행동 실험 예제
    print("\n" + "=" * 60)
    print("3. BEHAVIORAL EXPERIMENT")
    print("=" * 60)
    
    experiment = QuestionTemplate.BEHAVIORAL_EXPERIMENTS["price_sensitivity"]
    
    experiment_results = []
    for i, persona in enumerate(sample_personas, 1):
        print(f"\n[Persona {i}/5] Running experiment...")
        result = simulator.run_experiment(persona, experiment)
        experiment_results.append(result)
        print(f"✓ Experiment completed for persona {i}")
    
    # 5. 결과 분석
    print("\n" + "=" * 60)
    print("4. ANALYSIS")
    print("=" * 60)
    
    analyzer = ResultAnalyzer()
    
    # 서베이 결과 DataFrame으로 변환
    survey_df = analyzer.aggregate_survey_results(survey_results)
    print(f"\n✓ Survey results: {len(survey_df)} responses collected")
    print(survey_df.head())
    
    # 감성 분석
    all_responses = [r['response'] for result in survey_results 
                     for r in result['responses'] if r.get('response')]
    sentiment = analyzer.analyze_sentiment(all_responses)
    print(f"\n✓ Sentiment analysis: {sentiment}")
    
    # 6. 결과 저장
    print("\n" + "=" * 60)
    print("5. EXPORT RESULTS")
    print("=" * 60)
    
    analyzer.export_results(survey_results, "survey_results.json")
    analyzer.export_results(interview_results, "interview_results.json")
    analyzer.export_results(experiment_results, "experiment_results.json")
    
    print("\n" + "=" * 60)
    print("✓ All simulations completed!")
    print("=" * 60)


if __name__ == "__main__":
    # API 키 확인
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  Warning: ANTHROPIC_API_KEY not found in environment variables")
        print("Please set it: export ANTHROPIC_API_KEY='your-key-here'")
    else:
        main()
