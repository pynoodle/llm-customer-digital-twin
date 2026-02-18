#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
고도화된 디지털 트윈 서베이 인터뷰 시뮬레이션 시스템
Digital-Twin-Simulation 프로젝트의 노트북을 참고하여 개발
"""

import pandas as pd
import numpy as np
import json
import random
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import os
from pathlib import Path

@dataclass
class SimulationConfig:
    """시뮬레이션 설정 클래스"""
    model_name: str = "gpt-4o-mini"
    temperature: float = 0.7
    max_tokens: int = 1000
    batch_size: int = 10
    simulation_id: str = None
    output_dir: str = "simulation_results"
    
    def __post_init__(self):
        if self.simulation_id is None:
            self.simulation_id = f"sim_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

@dataclass
class SurveyQuestion:
    """서베이 질문 클래스"""
    question_id: str
    question_text: str
    question_type: str  # "likert", "multiple_choice", "open_ended", "rating"
    options: List[str] = None
    scale_range: Tuple[int, int] = (1, 7)
    required: bool = True

@dataclass
class InterviewGuide:
    """인터뷰 가이드 클래스"""
    guide_id: str
    title: str
    questions: List[str]
    context: str = ""
    style: str = "친근한 대화"

@dataclass
class SimulationResult:
    """시뮬레이션 결과 클래스"""
    persona_id: str
    question_id: str
    response: str
    score: Optional[int] = None
    reasoning: str = ""
    timestamp: str = None
    confidence: float = 0.0
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now().isoformat()

class AdvancedPersonaSimulator:
    """고도화된 페르소나 시뮬레이터"""
    
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.results = []
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def generate_survey_responses(
        self, 
        personas: List[Dict], 
        questions: List[SurveyQuestion],
        context: str = ""
    ) -> List[SimulationResult]:
        """서베이 응답 생성"""
        results = []
        
        for persona in personas:
            persona_id = persona.get('id', 'unknown')
            print(f"[INFO] 페르소나 {persona_id} 서베이 응답 생성 중...")
            
            for question in questions:
                try:
                    result = self._generate_single_response(
                        persona, question, context
                    )
                    results.append(result)
                except Exception as e:
                    print(f"[ERROR] 페르소나 {persona_id}, 질문 {question.question_id}: {e}")
                    # 오류 시 기본 응답 생성
                    error_result = SimulationResult(
                        persona_id=persona_id,
                        question_id=question.question_id,
                        response=f"응답 생성 오류: {str(e)}",
                        score=3,  # 중립 점수
                        reasoning="시스템 오류로 인한 기본 응답"
                    )
                    results.append(error_result)
        
        self.results.extend(results)
        return results
    
    def generate_interview_responses(
        self,
        personas: List[Dict],
        interview_guide: InterviewGuide
    ) -> List[SimulationResult]:
        """인터뷰 응답 생성"""
        results = []
        
        for persona in personas:
            persona_id = persona.get('id', 'unknown')
            print(f"[INFO] 페르소나 {persona_id} 인터뷰 응답 생성 중...")
            
            # 인터뷰 전체 응답 생성
            try:
                response = self._generate_interview_response(
                    persona, interview_guide
                )
                
                result = SimulationResult(
                    persona_id=persona_id,
                    question_id=interview_guide.guide_id,
                    response=response,
                    reasoning=f"인터뷰 스타일: {interview_guide.style}"
                )
                results.append(result)
                
            except Exception as e:
                print(f"[ERROR] 페르소나 {persona_id} 인터뷰: {e}")
                error_result = SimulationResult(
                    persona_id=persona_id,
                    question_id=interview_guide.guide_id,
                    response=f"인터뷰 응답 생성 오류: {str(e)}",
                    reasoning="시스템 오류로 인한 기본 응답"
                )
                results.append(error_result)
        
        self.results.extend(results)
        return results
    
    def _generate_single_response(
        self, 
        persona: Dict, 
        question: SurveyQuestion, 
        context: str
    ) -> SimulationResult:
        """단일 응답 생성"""
        # 페르소나 컨텍스트 구축
        persona_context = self._build_enhanced_persona_context(persona)
        
        # 질문 유형별 프롬프트 생성
        prompt = self._create_question_prompt(question, persona_context, context)
        
        # AI 응답 생성 (실제로는 AI API 호출)
        response, score, reasoning = self._call_ai_api(prompt, question)
        
        return SimulationResult(
            persona_id=persona.get('id', 'unknown'),
            question_id=question.question_id,
            response=response,
            score=score,
            reasoning=reasoning,
            confidence=self._calculate_confidence(response, reasoning)
        )
    
    def _generate_interview_response(
        self,
        persona: Dict,
        interview_guide: InterviewGuide
    ) -> str:
        """인터뷰 응답 생성"""
        persona_context = self._build_enhanced_persona_context(persona)
        
        # 인터뷰 프롬프트 생성
        prompt = f"""
        당신은 {persona_context} 특성을 가진 사람입니다.
        
        인터뷰 컨텍스트: {interview_guide.context}
        인터뷰 스타일: {interview_guide.style}
        
        다음 질문들에 대해 자연스럽고 진정성 있는 답변을 해주세요:
        
        {chr(10).join([f"{i+1}. {q}" for i, q in enumerate(interview_guide.questions)])}
        
        각 질문에 대해 개인적인 경험과 의견을 바탕으로 답변해주세요.
        """
        
        # AI 응답 생성
        response, _, _ = self._call_ai_api(prompt, None)
        return response
    
    def _build_enhanced_persona_context(self, persona: Dict) -> str:
        """향상된 페르소나 컨텍스트 구축"""
        persona_id = int(persona.get('id', 0))
        
        # 더 정교한 특성 매핑
        demographics = self._get_demographics(persona_id)
        personality = self._get_personality_traits(persona_id)
        preferences = self._get_preferences(persona_id)
        experiences = self._get_experiences(persona_id)
        
        context_parts = [
            f"인구통계: {demographics}",
            f"성격 특성: {personality}",
            f"선호도: {preferences}",
            f"경험 배경: {experiences}"
        ]
        
        # 기존 데이터 활용
        if 'persona_summary' in persona and persona['persona_summary']:
            summary = str(persona['persona_summary'])[:300] + "..."
            context_parts.append(f"개인 배경: {summary}")
        
        return "\n".join(context_parts)
    
    def _get_demographics(self, persona_id: int) -> str:
        """인구통계 정보 생성"""
        age_groups = ["20대 초반", "20대 후반", "30대 초반", "30대 후반", "40대 초반", "40대 후반", "50대", "60대"]
        genders = ["남성", "여성", "기타"]
        regions = ["서울", "경기", "부산", "대구", "광주", "대전", "울산", "세종", "기타"]
        educations = ["고졸", "대졸", "대학원", "박사"]
        incomes = ["저소득", "중소득", "고소득", "최고소득"]
        
        return f"{age_groups[persona_id % len(age_groups)]}, {genders[persona_id % len(genders)]}, {regions[persona_id % len(regions)]}, {educations[persona_id % len(educations)]}, {incomes[persona_id % len(incomes)]}"
    
    def _get_personality_traits(self, persona_id: int) -> str:
        """성격 특성 생성"""
        traits = [
            "외향적이고 사교적",
            "내향적이고 신중", 
            "창의적이고 개방적",
            "체계적이고 완벽주의",
            "낙천적이고 유연",
            "분석적이고 논리적",
            "감성적이고 직관적",
            "경쟁적이고 야심적"
        ]
        
        # 여러 특성 조합
        primary_trait = traits[persona_id % len(traits)]
        secondary_trait = traits[(persona_id + 1) % len(traits)]
        
        return f"{primary_trait}, {secondary_trait}"
    
    def _get_preferences(self, persona_id: int) -> str:
        """선호도 생성"""
        tech_prefs = ["애플 매니아", "삼성 팬", "중립적", "가성비 중시", "최신 기술 추구"]
        spending = ["극도 절약형", "절약형", "적당형", "소비형", "프리미엄형", "럭셔리형"]
        brands = ["브랜드 충성도 높음", "브랜드 충성도 보통", "브랜드 충성도 낮음", "브랜드 무관심"]
        
        return f"기술: {tech_prefs[persona_id % len(tech_prefs)]}, 소비: {spending[persona_id % len(spending)]}, 브랜드: {brands[persona_id % len(brands)]}"
    
    def _get_experiences(self, persona_id: int) -> str:
        """경험 배경 생성"""
        careers = ["신입", "경력 3-5년", "경력 10년+", "전문가", "리더"]
        industries = ["IT", "금융", "제조", "서비스", "교육", "의료", "예술", "스포츠"]
        lifestyles = ["싱글", "커플", "가족", "대가족", "독신"]
        
        return f"경력: {careers[persona_id % len(careers)]}, 업계: {industries[persona_id % len(industries)]}, 라이프스타일: {lifestyles[persona_id % len(lifestyles)]}"
    
    def _create_question_prompt(
        self, 
        question: SurveyQuestion, 
        persona_context: str, 
        context: str
    ) -> str:
        """질문별 프롬프트 생성"""
        base_prompt = f"""
        당신은 {persona_context} 특성을 가진 사람입니다.
        
        컨텍스트: {context}
        
        질문: {question.question_text}
        """
        
        if question.question_type == "likert":
            scale_min, scale_max = question.scale_range
            base_prompt += f"""
            
            {scale_min}점(전혀 동의하지 않음)부터 {scale_max}점(완전히 동의함)까지의 척도로 답변해주세요.
            점수와 함께 그 이유를 설명해주세요.
            """
        elif question.question_type == "multiple_choice":
            if question.options:
                base_prompt += f"""
                
                다음 선택지 중에서 선택해주세요:
                {chr(10).join([f"- {opt}" for opt in question.options])}
                """
        elif question.question_type == "open_ended":
            base_prompt += """
            
            자유롭게 답변해주세요. 개인적인 경험과 의견을 포함해주세요.
            """
        
        return base_prompt
    
    def _call_ai_api(self, prompt: str, question: Optional[SurveyQuestion]) -> Tuple[str, Optional[int], str]:
        """AI API 호출 (실제 구현 필요)"""
        # 실제로는 OpenAI API나 다른 LLM API 호출
        # 여기서는 시뮬레이션용 응답 생성
        
        if question and question.question_type == "likert":
            score = random.randint(question.scale_range[0], question.scale_range[1])
            response = f"점수: {score} - 개인적인 경험과 선호도를 바탕으로 한 답변입니다."
            reasoning = f"페르소나의 특성과 질문의 내용을 고려하여 {score}점을 선택했습니다."
        else:
            response = "개인적인 경험과 의견을 바탕으로 한 답변입니다."
            reasoning = "페르소나의 배경과 특성을 반영한 답변입니다."
            score = None
        
        return response, score, reasoning
    
    def _calculate_confidence(self, response: str, reasoning: str) -> float:
        """응답 신뢰도 계산"""
        # 간단한 휴리스틱 기반 신뢰도 계산
        confidence = 0.5  # 기본값
        
        if len(response) > 50:
            confidence += 0.1
        if "개인적인" in response or "경험" in response:
            confidence += 0.1
        if len(reasoning) > 20:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def save_results(self, filename: str = None) -> str:
        """결과 저장"""
        if filename is None:
            filename = f"simulation_results_{self.config.simulation_id}.json"
        
        filepath = self.output_dir / filename
        
        # 결과를 딕셔너리로 변환
        results_data = [asdict(result) for result in self.results]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, ensure_ascii=False, indent=2)
        
        print(f"[OK] 결과 저장 완료: {filepath}")
        return str(filepath)
    
    def export_to_csv(self, filename: str = None) -> str:
        """CSV 형식으로 내보내기"""
        if filename is None:
            filename = f"simulation_results_{self.config.simulation_id}.csv"
        
        filepath = self.output_dir / filename
        
        # DataFrame으로 변환
        df_data = []
        for result in self.results:
            df_data.append({
                'persona_id': result.persona_id,
                'question_id': result.question_id,
                'response': result.response,
                'score': result.score,
                'reasoning': result.reasoning,
                'confidence': result.confidence,
                'timestamp': result.timestamp
            })
        
        df = pd.DataFrame(df_data)
        df.to_csv(filepath, index=False, encoding='utf-8-sig')
        
        print(f"[OK] CSV 내보내기 완료: {filepath}")
        return str(filepath)

class SimulationAnalyzer:
    """시뮬레이션 결과 분석기"""
    
    def __init__(self, results: List[SimulationResult]):
        self.results = results
        self.df = pd.DataFrame([asdict(result) for result in results])
    
    def analyze_response_patterns(self) -> Dict[str, Any]:
        """응답 패턴 분석"""
        analysis = {}
        
        # 점수 분포 분석
        if 'score' in self.df.columns:
            scores = self.df['score'].dropna()
            if len(scores) > 0:
                analysis['score_distribution'] = {
                    'mean': float(scores.mean()),
                    'std': float(scores.std()),
                    'min': int(scores.min()),
                    'max': int(scores.max()),
                    'median': float(scores.median())
                }
        
        # 페르소나별 응답 다양성
        persona_responses = self.df.groupby('persona_id')['response'].nunique()
        analysis['persona_diversity'] = {
            'mean_unique_responses': float(persona_responses.mean()),
            'total_personas': len(persona_responses),
            'diversity_score': float(persona_responses.std())
        }
        
        # 질문별 응답 분석
        question_analysis = {}
        for question_id in self.df['question_id'].unique():
            q_data = self.df[self.df['question_id'] == question_id]
            question_analysis[question_id] = {
                'total_responses': len(q_data),
                'unique_responses': q_data['response'].nunique(),
                'avg_confidence': float(q_data['confidence'].mean()) if 'confidence' in q_data.columns else 0.0
            }
        
        analysis['question_analysis'] = question_analysis
        
        return analysis
    
    def generate_report(self) -> str:
        """분석 리포트 생성"""
        patterns = self.analyze_response_patterns()
        
        report = f"""
# 시뮬레이션 결과 분석 리포트

## 전체 통계
- 총 응답 수: {len(self.results)}
- 페르소나 수: {patterns.get('persona_diversity', {}).get('total_personas', 0)}
- 평균 응답 다양성: {patterns.get('persona_diversity', {}).get('mean_unique_responses', 0):.2f}

## 점수 분포 (리커트 척도 질문)
"""
        
        if 'score_distribution' in patterns:
            score_dist = patterns['score_distribution']
            report += f"""
- 평균 점수: {score_dist['mean']:.2f}
- 표준편차: {score_dist['std']:.2f}
- 최소값: {score_dist['min']}
- 최대값: {score_dist['max']}
- 중앙값: {score_dist['median']:.2f}
"""
        
        report += "\n## 질문별 분석\n"
        for q_id, q_analysis in patterns.get('question_analysis', {}).items():
            report += f"""
### {q_id}
- 총 응답 수: {q_analysis['total_responses']}
- 고유 응답 수: {q_analysis['unique_responses']}
- 평균 신뢰도: {q_analysis['avg_confidence']:.2f}
"""
        
        return report

def create_sample_questions() -> List[SurveyQuestion]:
    """샘플 질문 생성"""
    return [
        SurveyQuestion(
            question_id="q1",
            question_text="새로운 기술 제품을 얼마나 자주 구매하시나요?",
            question_type="likert",
            scale_range=(1, 7)
        ),
        SurveyQuestion(
            question_id="q2", 
            question_text="브랜드 충성도가 높은 편인가요?",
            question_type="likert",
            scale_range=(1, 7)
        ),
        SurveyQuestion(
            question_id="q3",
            question_text="스마트폰 구매 시 가장 중요한 요소는 무엇인가요?",
            question_type="multiple_choice",
            options=["가격", "성능", "디자인", "브랜드", "기능"]
        ),
        SurveyQuestion(
            question_id="q4",
            question_text="최근 구매한 제품에 대해 자유롭게 말씀해주세요.",
            question_type="open_ended"
        )
    ]

def create_sample_interview_guide() -> InterviewGuide:
    """샘플 인터뷰 가이드 생성"""
    return InterviewGuide(
        guide_id="interview_1",
        title="기술 제품 사용 경험 인터뷰",
        questions=[
            "평소 어떤 기술 제품을 주로 사용하시나요?",
            "최근 구매한 제품 중 만족도가 높은 것은 무엇인가요?",
            "제품 구매 시 가장 중요하게 생각하는 요소는 무엇인가요?",
            "브랜드에 대한 충성도는 어느 정도인가요?",
            "새로운 기술에 대한 관심도는 어떤가요?"
        ],
        context="기술 제품 사용 경험과 선호도에 대한 심층 인터뷰",
        style="친근한 대화"
    )

def main():
    """메인 실행 함수"""
    print("=== 고도화된 디지털 트윈 시뮬레이션 시스템 ===")
    
    # 설정 초기화
    config = SimulationConfig(
        model_name="gpt-4o-mini",
        temperature=0.7,
        batch_size=5
    )
    
    # 시뮬레이터 초기화
    simulator = AdvancedPersonaSimulator(config)
    
    # 샘플 페르소나 생성
    sample_personas = [
        {"id": "100", "persona_summary": "20대 초반 IT 개발자"},
        {"id": "200", "persona_summary": "30대 후반 마케터"},
        {"id": "300", "persona_summary": "40대 초반 교사"},
        {"id": "400", "persona_summary": "50대 자영업자"},
        {"id": "500", "persona_summary": "60대 은퇴자"}
    ]
    
    # 서베이 시뮬레이션
    print("\n=== 서베이 시뮬레이션 실행 ===")
    questions = create_sample_questions()
    survey_results = simulator.generate_survey_responses(
        sample_personas, questions, "기술 제품 선호도 조사"
    )
    
    # 인터뷰 시뮬레이션
    print("\n=== 인터뷰 시뮬레이션 실행 ===")
    interview_guide = create_sample_interview_guide()
    interview_results = simulator.generate_interview_responses(
        sample_personas, interview_guide
    )
    
    # 결과 저장
    print("\n=== 결과 저장 ===")
    json_file = simulator.save_results()
    csv_file = simulator.export_to_csv()
    
    # 결과 분석
    print("\n=== 결과 분석 ===")
    analyzer = SimulationAnalyzer(simulator.results)
    report = analyzer.generate_report()
    
    # 리포트 저장
    report_file = Path(config.output_dir) / f"analysis_report_{config.simulation_id}.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"[OK] 분석 리포트 저장: {report_file}")
    print(f"[OK] JSON 결과: {json_file}")
    print(f"[OK] CSV 결과: {csv_file}")
    
    print("\n=== 시뮬레이션 완료 ===")
    print(f"총 {len(simulator.results)}개의 응답 생성")
    print(f"페르소나 수: {len(sample_personas)}")
    print(f"질문 수: {len(questions)}")

if __name__ == "__main__":
    main()
