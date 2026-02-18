#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
고도화된 AI 에이전트
Digital-Twin-Simulation 프로젝트의 방법론을 적용한 향상된 AI 에이전트
"""

import os
import json
import random
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import pandas as pd

from openai import OpenAI
from dotenv import load_dotenv
from src.dataset_loader import Persona

@dataclass
class ResponseMetadata:
    """응답 메타데이터"""
    confidence: float
    reasoning: str
    persona_traits_used: List[str]
    response_style: str
    timestamp: str

class EnhancedAIAgent:
    """고도화된 AI 에이전트"""
    
    def __init__(self, api_key: str = None):
        """AI 에이전트 초기화"""
        if api_key is None:
            api_key = os.getenv('OPENAI_API_KEY')
        
        if not api_key:
            raise ValueError("OpenAI API 키가 필요합니다.")
        
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4o-mini"
        self.response_history = []
        
    def generate_enhanced_survey_response(
        self,
        persona: Persona,
        question: str,
        question_type: str = "likert",
        scale_range: Tuple[int, int] = (1, 7),
        context: str = "",
        options: List[str] = None
    ) -> Dict[str, Any]:
        """향상된 서베이 응답 생성"""
        
        # 페르소나 컨텍스트 구축
        persona_context = self._build_enhanced_persona_context(persona)
        
        # 질문별 맞춤 프롬프트 생성
        prompt = self._create_enhanced_survey_prompt(
            persona_context, question, question_type, 
            scale_range, context, options
        )
        
        try:
            # AI 응답 생성
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 주어진 페르소나의 특성을 바탕으로 진정성 있는 응답을 생성하는 AI입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # 응답 파싱 및 분석
            parsed_response = self._parse_survey_response(
                ai_response, question_type, scale_range
            )
            
            # 메타데이터 생성
            metadata = self._generate_response_metadata(
                persona, question, parsed_response, ai_response
            )
            
            result = {
                'response': parsed_response['response'],
                'score': parsed_response.get('score'),
                'reasoning': parsed_response.get('reasoning', ''),
                'metadata': metadata,
                'raw_ai_response': ai_response
            }
            
            # 응답 히스토리 저장
            self.response_history.append({
                'persona_id': persona.id,
                'question': question,
                'result': result,
                'timestamp': datetime.now().isoformat()
            })
            
            return result
            
        except Exception as e:
            return {
                'response': f"응답 생성 오류: {str(e)}",
                'score': scale_range[0] + (scale_range[1] - scale_range[0]) // 2,  # 중간값
                'reasoning': "시스템 오류로 인한 기본 응답",
                'metadata': ResponseMetadata(
                    confidence=0.0,
                    reasoning="오류 발생",
                    persona_traits_used=[],
                    response_style="기본",
                    timestamp=datetime.now().isoformat()
                ),
                'error': str(e)
            }
    
    def generate_enhanced_interview_response(
        self,
        persona: Persona,
        interview_questions: List[str],
        interview_style: str = "친근한 대화",
        context: str = ""
    ) -> Dict[str, Any]:
        """향상된 인터뷰 응답 생성"""
        
        persona_context = self._build_enhanced_persona_context(persona)
        
        # 인터뷰 프롬프트 생성
        prompt = self._create_enhanced_interview_prompt(
            persona_context, interview_questions, interview_style, context
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "당신은 주어진 페르소나의 특성을 바탕으로 자연스럽고 진정성 있는 인터뷰 응답을 생성하는 AI입니다."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=1000
            )
            
            ai_response = response.choices[0].message.content.strip()
            
            # 응답 분석 및 구조화
            structured_response = self._structure_interview_response(
                ai_response, interview_questions
            )
            
            # 메타데이터 생성
            metadata = self._generate_interview_metadata(
                persona, interview_questions, structured_response
            )
            
            result = {
                'conversation': structured_response,
                'metadata': metadata,
                'raw_ai_response': ai_response
            }
            
            return result
            
        except Exception as e:
            return {
                'conversation': f"인터뷰 응답 생성 오류: {str(e)}",
                'metadata': ResponseMetadata(
                    confidence=0.0,
                    reasoning="오류 발생",
                    persona_traits_used=[],
                    response_style="기본",
                    timestamp=datetime.now().isoformat()
                ),
                'error': str(e)
            }
    
    def _build_enhanced_persona_context(self, persona: Persona) -> str:
        """향상된 페르소나 컨텍스트 구축"""
        persona_id = int(persona.id) if persona.id.isdigit() else hash(persona.id) % 1000
        
        # 다차원 특성 매핑
        demographics = self._get_enhanced_demographics(persona_id)
        personality = self._get_enhanced_personality(persona_id)
        preferences = self._get_enhanced_preferences(persona_id)
        experiences = self._get_enhanced_experiences(persona_id)
        values = self._get_enhanced_values(persona_id)
        
        context_parts = [
            f"인구통계: {demographics}",
            f"성격 특성: {personality}",
            f"선호도: {preferences}",
            f"경험 배경: {experiences}",
            f"가치관: {values}"
        ]
        
        # 기존 데이터 활용
        if 'persona_summary' in persona.data and persona.data['persona_summary']:
            summary = str(persona.data['persona_summary'])
            if len(summary) > 200:
                summary = summary[:200] + "..."
            context_parts.append(f"개인 배경: {summary}")
        
        return "\n".join(context_parts)
    
    def _get_enhanced_demographics(self, persona_id: int) -> str:
        """향상된 인구통계 정보"""
        age_groups = ["20대 초반", "20대 후반", "30대 초반", "30대 후반", "40대 초반", "40대 후반", "50대", "60대"]
        genders = ["남성", "여성", "기타"]
        regions = ["서울", "경기", "부산", "대구", "광주", "대전", "울산", "세종", "기타"]
        educations = ["고졸", "대졸", "대학원", "박사"]
        incomes = ["저소득", "중소득", "고소득", "최고소득"]
        occupations = ["사무직", "IT개발자", "마케터", "교사", "의사", "예술가", "판매원", "자영업자", "연구원", "디자이너"]
        
        return f"{age_groups[persona_id % len(age_groups)]}, {genders[persona_id % len(genders)]}, {regions[persona_id % len(regions)]}, {educations[persona_id % len(educations)]}, {incomes[persona_id % len(incomes)]}, {occupations[persona_id % len(occupations)]}"
    
    def _get_enhanced_personality(self, persona_id: int) -> str:
        """향상된 성격 특성"""
        primary_traits = [
            "외향적이고 사교적", "내향적이고 신중", "창의적이고 개방적", 
            "체계적이고 완벽주의", "낙천적이고 유연", "분석적이고 논리적", 
            "감성적이고 직관적", "경쟁적이고 야심적"
        ]
        
        secondary_traits = [
            "협력적", "독립적", "혁신적", "전통적", "모험적", "안정적", 
            "이상주의적", "현실적"
        ]
        
        primary = primary_traits[persona_id % len(primary_traits)]
        secondary = secondary_traits[(persona_id + 1) % len(secondary_traits)]
        
        return f"{primary}, {secondary}"
    
    def _get_enhanced_preferences(self, persona_id: int) -> str:
        """향상된 선호도 - 일관성 있는 브랜드 선호도 생성"""
        # ID 기반으로 일관성 있는 선호도 생성
        tech_prefs = ["애플 매니아", "삼성 팬", "구글 픽셀 선호", "중립적", "가성비 중시", "최신 기술 추구", "브랜드 무관심", "안정성 중시"]
        spending = ["극도 절약형", "절약형", "적당형", "소비형", "프리미엄형", "럭셔리형"]
        lifestyles = ["미니멀", "활동적", "편안함 추구", "도전적", "전통적", "혁신적"]
        
        # 브랜드 충성도와 기술 선호도를 연관시켜 일관성 확보
        brand_loyalty_level = persona_id % 4  # 0-3
        
        if brand_loyalty_level == 0:  # 높은 충성도
            brands = "브랜드 충성도 높음 (특정 브랜드 선호)"
            tech_pref = tech_prefs[persona_id % 3]  # 애플, 삼성, 구글 중 선택
        elif brand_loyalty_level == 1:  # 보통 충성도
            brands = "브랜드 충성도 보통 (선호 브랜드 있음)"
            tech_pref = tech_prefs[3 + (persona_id % 3)]  # 중립적, 가성비, 최신기술 중 선택
        elif brand_loyalty_level == 2:  # 낮은 충성도
            brands = "브랜드 충성도 낮음 (브랜드 무관심)"
            tech_pref = tech_prefs[6 + (persona_id % 2)]  # 브랜드 무관심, 안정성 중 선택
        else:  # 무관심
            brands = "브랜드 완전 무관심 (기능만 중시)"
            tech_pref = "기능 중심"
        
        spending_style = spending[persona_id % len(spending)]
        lifestyle = lifestyles[persona_id % len(lifestyles)]
        
        return f"기술: {tech_pref}, 소비: {spending_style}, 브랜드: {brands}, 라이프스타일: {lifestyle}"
    
    def _get_enhanced_experiences(self, persona_id: int) -> str:
        """향상된 경험 배경"""
        careers = ["신입", "경력 3-5년", "경력 10년+", "전문가", "리더", "은퇴"]
        industries = ["IT", "금융", "제조", "서비스", "교육", "의료", "예술", "스포츠", "정부", "비영리"]
        lifestyles = ["싱글", "커플", "가족", "대가족", "독신", "동거"]
        interests = ["기술", "예술", "스포츠", "여행", "독서", "음악", "게임", "요리", "사진", "운동"]
        
        return f"경력: {careers[persona_id % len(careers)]}, 업계: {industries[persona_id % len(industries)]}, 라이프스타일: {lifestyles[persona_id % len(lifestyles)]}, 관심사: {interests[persona_id % len(interests)]}"
    
    def _get_enhanced_values(self, persona_id: int) -> str:
        """향상된 가치관"""
        values = [
            "성공과 성취", "가족과 관계", "자유와 독립", "안정과 보안", 
            "창의와 혁신", "전통과 질서", "평등과 정의", "개인적 성장"
        ]
        
        primary_value = values[persona_id % len(values)]
        secondary_value = values[(persona_id + 2) % len(values)]
        
        return f"{primary_value}, {secondary_value}"
    
    def _create_enhanced_survey_prompt(
        self,
        persona_context: str,
        question: str,
        question_type: str,
        scale_range: Tuple[int, int],
        context: str,
        options: List[str] = None
    ) -> str:
        """향상된 서베이 프롬프트 생성"""
        
        base_prompt = f"""
당신은 {persona_context} 특성을 가진 실제 사람입니다.

컨텍스트: {context}

질문: {question}

중요한 지침:
1. 당신의 고유한 성격, 경험, 가치관을 바탕으로 답변하세요
2. 다른 사람과 똑같은 답변을 하지 마세요
3. 당신만의 개별적인 관점과 경험을 반영하세요
4. 일관성 있게 답변하세요 (예: 브랜드 충성도가 높으면 높은 점수, 낮으면 낮은 점수)
"""
        
        if question_type == "likert":
            scale_min, scale_max = scale_range
            base_prompt += f"""

{scale_min}점(전혀 동의하지 않음)부터 {scale_max}점(완전히 동의함)까지의 척도로 답변해주세요.

당신의 브랜드 선호도, 소비 성향, 기술 수준에 따라 일관성 있게 점수를 선택하세요:
- 브랜드 충성도가 높으면 높은 점수 (5-7점)
- 브랜드 충성도가 낮으면 낮은 점수 (1-4점)
- 브랜드 무관심이면 중간 점수 (3-5점)

응답 형식:
점수: [1-7 사이의 숫자]
이유: [당신만의 구체적인 이유와 개인적 경험]
"""
        
        elif question_type == "multiple_choice":
            if options:
                base_prompt += f"""

다음 선택지 중에서 당신의 개인적 경험과 선호도를 바탕으로 가장 적합한 것을 선택해주세요:
{chr(10).join([f"- {opt}" for opt in options])}

당신의 고유한 특성과 경험을 바탕으로 선택하고 그 이유를 설명해주세요.
"""
        
        elif question_type == "open_ended":
            base_prompt += """

자유롭게 답변해주세요. 당신의 개인적인 경험, 의견, 감정을 포함하여 진정성 있고 고유한 답변을 해주세요.
"""
        
        return base_prompt
    
    def _create_enhanced_interview_prompt(
        self,
        persona_context: str,
        questions: List[str],
        interview_style: str,
        context: str
    ) -> str:
        """향상된 인터뷰 프롬프트 생성"""
        
        return f"""
당신은 {persona_context} 특성을 가진 사람입니다.

인터뷰 컨텍스트: {context}
인터뷰 스타일: {interview_style}

다음 질문들에 대해 자연스럽고 진정성 있는 답변을 해주세요. 
당신의 개인적인 경험, 의견, 감정을 포함하여 실제 사람처럼 답변해주세요.

질문들:
{chr(10).join([f"{i+1}. {q}" for i, q in enumerate(questions)])}

각 질문에 대해 구체적이고 개인적인 답변을 해주세요.
"""
    
    def _parse_survey_response(
        self, 
        ai_response: str, 
        question_type: str, 
        scale_range: Tuple[int, int]
    ) -> Dict[str, Any]:
        """서베이 응답 파싱"""
        
        if question_type == "likert":
            # 점수 추출
            score = None
            reasoning = ""
            
            # "점수: X" 패턴 찾기
            import re
            score_match = re.search(r'점수:\s*(\d+)', ai_response)
            if score_match:
                score = int(score_match.group(1))
                score = max(scale_range[0], min(scale_range[1], score))  # 범위 제한
            
            # 이유 추출
            reason_match = re.search(r'이유:\s*(.+)', ai_response)
            if reason_match:
                reasoning = reason_match.group(1).strip()
            else:
                reasoning = ai_response
            
            # 중복 제거를 위해 점수와 이유 부분을 제거한 응답 생성
            clean_response = ai_response
            if score_match and reason_match:
                # "점수: X" 부분 제거
                clean_response = re.sub(r'점수:\s*\d+\s*\n?', '', clean_response)
                # "이유:" 부분 제거
                clean_response = re.sub(r'이유:\s*', '', clean_response)
                clean_response = clean_response.strip()
            
            return {
                'response': clean_response,
                'score': score,
                'reasoning': reasoning
            }
        
        else:
            return {
                'response': ai_response,
                'reasoning': ai_response
            }
    
    def _structure_interview_response(
        self, 
        ai_response: str, 
        questions: List[str]
    ) -> str:
        """인터뷰 응답 구조화"""
        
        # AI 응답을 그대로 사용 (이미 구조화된 형태로 생성됨)
        return ai_response
    
    def _generate_response_metadata(
        self,
        persona: Persona,
        question: str,
        parsed_response: Dict[str, Any],
        raw_response: str
    ) -> ResponseMetadata:
        """응답 메타데이터 생성"""
        
        # 신뢰도 계산
        confidence = self._calculate_confidence(raw_response, parsed_response)
        
        # 사용된 페르소나 특성 추출
        traits_used = self._extract_used_traits(persona, question, raw_response)
        
        # 응답 스타일 분석
        response_style = self._analyze_response_style(raw_response)
        
        return ResponseMetadata(
            confidence=confidence,
            reasoning=parsed_response.get('reasoning', ''),
            persona_traits_used=traits_used,
            response_style=response_style,
            timestamp=datetime.now().isoformat()
        )
    
    def _generate_interview_metadata(
        self,
        persona: Persona,
        questions: List[str],
        structured_response: str
    ) -> ResponseMetadata:
        """인터뷰 메타데이터 생성"""
        
        confidence = self._calculate_confidence(structured_response, {})
        traits_used = self._extract_used_traits(persona, "인터뷰", structured_response)
        response_style = self._analyze_response_style(structured_response)
        
        return ResponseMetadata(
            confidence=confidence,
            reasoning="인터뷰 응답",
            persona_traits_used=traits_used,
            response_style=response_style,
            timestamp=datetime.now().isoformat()
        )
    
    def _calculate_confidence(self, response: str, parsed_response: Dict[str, Any]) -> float:
        """신뢰도 계산"""
        confidence = 0.3  # 기본값 (더 낮게 시작)
        
        # 응답 길이
        if len(response) > 50:
            confidence += 0.1
        if len(response) > 100:
            confidence += 0.1
        if len(response) > 200:
            confidence += 0.1
        
        # 개인적 표현 포함
        personal_indicators = ["개인적으로", "저는", "제 경험", "저의", "나의", "저에게", "제가", "저는"]
        personal_count = sum(1 for indicator in personal_indicators if indicator in response)
        confidence += personal_count * 0.05
        
        # 구체적 이유 포함
        reason_indicators = ["이유", "때문에", "왜냐하면", "왜냐하면", "그래서", "따라서", "때문"]
        reason_count = sum(1 for indicator in reason_indicators if indicator in response)
        confidence += reason_count * 0.03
        
        # 구체적인 내용 포함
        if "경험" in response or "사용" in response or "구매" in response:
            confidence += 0.1
        
        # 점수가 있는 경우
        if 'score' in parsed_response and parsed_response['score'] is not None:
            confidence += 0.1
        
        # 페르소나 ID 기반 변동성 추가
        if 'persona_id' in parsed_response:
            persona_id = int(parsed_response['persona_id']) if str(parsed_response['persona_id']).isdigit() else 0
            # ID 기반으로 신뢰도에 약간의 변동성 추가
            confidence += (persona_id % 10) * 0.01
        
        return min(confidence, 1.0)
    
    def _extract_used_traits(self, persona: Persona, question: str, response: str) -> List[str]:
        """사용된 페르소나 특성 추출"""
        traits = []
        
        # 간단한 휴리스틱으로 특성 추출
        if "기술" in question.lower() or "제품" in question.lower():
            traits.append("기술 선호도")
        
        if "브랜드" in question.lower():
            traits.append("브랜드 충성도")
        
        if "구매" in question.lower() or "소비" in question.lower():
            traits.append("소비 성향")
        
        if "경험" in response or "저는" in response:
            traits.append("개인적 경험")
        
        return traits
    
    def _analyze_response_style(self, response: str) -> str:
        """응답 스타일 분석"""
        if len(response) < 50:
            return "간결함"
        elif len(response) > 300:
            return "상세함"
        elif "감정" in response or "느낌" in response or "좋아" in response or "싫어" in response:
            return "감성적"
        elif "분석" in response or "논리" in response or "데이터" in response or "통계" in response:
            return "분석적"
        elif "경험" in response or "사용" in response or "구매" in response:
            return "경험적"
        elif "기술" in response or "기능" in response or "성능" in response:
            return "기술적"
        else:
            return "균형적"
    
    def get_response_statistics(self) -> Dict[str, Any]:
        """응답 통계 반환"""
        if not self.response_history:
            return {"total_responses": 0}
        
        total_responses = len(self.response_history)
        unique_personas = len(set(r['persona_id'] for r in self.response_history))
        
        # 신뢰도 통계
        confidences = []
        for response in self.response_history:
            if 'metadata' in response['result'] and hasattr(response['result']['metadata'], 'confidence'):
                confidences.append(response['result']['metadata'].confidence)
        
        avg_confidence = np.mean(confidences) if confidences else 0.0
        
        return {
            "total_responses": total_responses,
            "unique_personas": unique_personas,
            "average_confidence": avg_confidence,
            "response_types": {
                "survey": len([r for r in self.response_history if 'score' in r['result']]),
                "interview": len([r for r in self.response_history if 'conversation' in r['result']])
            }
        }
