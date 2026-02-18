"""
ChatGPT API 연동 및 프롬프트 엔지니어링 모듈
디지털 트윈이 설문조사와 인터뷰에 응답하도록 합니다.
"""

import os
from typing import Dict, Any, Optional, List
from openai import OpenAI
from dotenv import load_dotenv
from src.dataset_loader import Persona


class AIAgent:
    """디지털 트윈 AI 에이전트"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        AI 에이전트를 초기화합니다.
        
        Args:
            api_key: OpenAI API 키 (None인 경우 환경변수에서 로드)
        """
        load_dotenv()
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "OpenAI API 키가 설정되지 않았습니다. "
                ".env 파일에 OPENAI_API_KEY를 설정하거나 api_key 파라미터를 전달하세요."
            )
        
        self.client = OpenAI(api_key=self.api_key)
        self.model = "gpt-4o-mini"  # 비용 효율적인 모델 사용
    
    def _build_persona_context(self, persona: Persona) -> str:
        """
        페르소나 정보를 핵심 특성만 추출하여 컨텍스트 문자열로 변환합니다.
        
        Args:
            persona: 페르소나 객체
        
        Returns:
            컨텍스트 문자열
        """
        context_parts = ["당신은 다음과 같은 특성을 가진 사람입니다:\n"]
        
        # 페르소나 ID를 기반으로 한 고유한 특성 생성
        persona_id = int(persona.id) if persona.id.isdigit() else hash(persona.id) % 1000
        
        # 더 다양한 특성 세트
        age_groups = ["20대 초반", "20대 후반", "30대 초반", "30대 후반", "40대 초반", "40대 후반", "50대", "60대"]
        occupations = ["사무직", "IT개발자", "마케터", "교사", "의사", "예술가", "판매원", "자영업자", "연구원", "디자이너"]
        personalities = ["외향적이고 사교적", "내향적이고 신중", "창의적이고 개방적", "체계적이고 완벽주의", "낙천적이고 유연", "분석적이고 논리적", "감성적이고 직관적"]
        interests = ["기술과 IT", "예술과 문화", "스포츠와 건강", "여행과 모험", "독서와 학습", "음악과 영화", "게임과 엔터테인먼트", "요리와 생활"]
        
        # 더 복잡한 ID 기반 특성 할당 (중복 최소화)
        age = age_groups[persona_id % len(age_groups)]
        occupation = occupations[persona_id % len(occupations)]
        personality = personalities[persona_id % len(personalities)]
        interest = interests[persona_id % len(interests)]
        
        # 기술 선호도 (더 세분화)
        tech_preference = "애플 매니아" if persona_id % 5 == 0 else "삼성 팬" if persona_id % 5 == 1 else "중립적" if persona_id % 5 == 2 else "가성비 중시" if persona_id % 5 == 3 else "최신 기술 추구"
        
        # 소비 성향 (더 다양화)
        spending_style = "극도 절약형" if persona_id % 6 == 0 else "절약형" if persona_id % 6 == 1 else "적당형" if persona_id % 6 == 2 else "소비형" if persona_id % 6 == 3 else "프리미엄형" if persona_id % 6 == 4 else "럭셔리형"
        
        # 추가 특성들
        tech_savviness = "기술 초보" if persona_id % 3 == 0 else "보통 수준" if persona_id % 3 == 1 else "기술 고수"
        brand_loyalty = "브랜드 충성도 높음" if persona_id % 4 == 0 else "브랜드 충성도 보통" if persona_id % 4 == 1 else "브랜드 충성도 낮음" if persona_id % 4 == 2 else "브랜드 무관심"
        
        context_parts.extend([
            f"- 나이: {age}",
            f"- 직업: {occupation}",
            f"- 성격: {personality}",
            f"- 관심사: {interest}",
            f"- 기술 선호도: {tech_preference}",
            f"- 소비 성향: {spending_style}",
            f"- 기술 숙련도: {tech_savviness}",
            f"- 브랜드 충성도: {brand_loyalty}"
        ])
        
        # 기존 데이터가 있다면 활용
        if 'persona_summary' in persona.data and persona.data['persona_summary']:
            summary = str(persona.data['persona_summary'])
            if len(summary) > 200:
                summary = summary[:200] + "..."
            context_parts.append(f"- 개인 배경: {summary}")
        
        return "\n".join(context_parts)
    
    def respond_to_survey_question(
        self,
        persona: Persona,
        question: str,
        scale_description: str = "1(전혀 동의하지 않음) ~ 7(매우 동의함)"
    ) -> Dict[str, Any]:
        """
        설문조사 질문에 1-7 척도로 응답합니다.
        
        Args:
            persona: 응답할 페르소나
            question: 설문 질문
            scale_description: 척도 설명
        
        Returns:
            응답 딕셔너리 (score, reasoning)
        """
        persona_context = self._build_persona_context(persona)
        
        system_prompt = f"""당신은 설문조사에 참여하는 응답자입니다.
주어진 페르소나의 특성과 배경을 바탕으로 설문 질문에 진정성 있게 답변해야 합니다.

{persona_context}

답변 형식:
- 반드시 1부터 7까지의 숫자 중 하나로 응답하세요.
- 척도: {scale_description}
- 답변 이유를 간단히 설명하세요 (1-2문장).

응답 형식 예시:
점수: 5
이유: [당신의 특성을 고려한 간단한 설명]
"""
        
        user_prompt = f"질문: {question}"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            content = response.choices[0].message.content.strip()
            
            # 응답 파싱
            score = self._extract_score(content)
            reasoning = self._extract_reasoning(content)
            
            return {
                "persona_id": persona.id,
                "question": question,
                "score": score,
                "reasoning": reasoning,
                "raw_response": content
            }
            
        except Exception as e:
            return {
                "persona_id": persona.id,
                "question": question,
                "score": None,
                "reasoning": None,
                "error": str(e),
                "raw_response": None
            }
    
    def respond_to_interview_question(
        self,
        persona: Persona,
        question: str,
        context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        인터뷰 질문에 자유롭게 응답합니다.
        
        Args:
            persona: 응답할 페르소나
            question: 인터뷰 질문
            context: 추가 컨텍스트 (선택사항)
        
        Returns:
            응답 딕셔너리 (response)
        """
        persona_context = self._build_persona_context(persona)
        
        system_prompt = f"""당신은 인터뷰에 참여하는 응답자입니다.
주어진 페르소나의 특성과 배경을 바탕으로 질문에 진정성 있고 구체적으로 답변해야 합니다.

{persona_context}

답변 지침:
- 당신의 경험, 생각, 감정을 구체적으로 표현하세요.
- 자연스럽고 인간적인 어조로 답변하세요.
- 너무 짧거나 형식적이지 않게, 3-5문장 정도로 답변하세요.
"""
        
        if context:
            system_prompt += f"\n\n추가 컨텍스트:\n{context}"
        
        user_prompt = f"질문: {question}"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            
            return {
                "persona_id": persona.id,
                "question": question,
                "response": content,
                "raw_response": content
            }
            
        except Exception as e:
            return {
                "persona_id": persona.id,
                "question": question,
                "response": None,
                "error": str(e),
                "raw_response": None
            }
    
    def conduct_follow_up(
        self,
        persona: Persona,
        conversation_history: List[Dict[str, str]],
        follow_up_question: str
    ) -> Dict[str, Any]:
        """
        이전 대화를 바탕으로 후속 질문에 응답합니다.
        
        Args:
            persona: 응답할 페르소나
            conversation_history: 이전 대화 기록 [{"question": "...", "answer": "..."}, ...]
            follow_up_question: 후속 질문
        
        Returns:
            응답 딕셔너리
        """
        persona_context = self._build_persona_context(persona)
        
        system_prompt = f"""당신은 인터뷰에 참여하는 응답자입니다.
주어진 페르소나의 특성과 배경을 바탕으로 질문에 진정성 있게 답변해야 합니다.

{persona_context}

이전 대화 내용을 참고하여 일관성 있게 답변하세요.
"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # 대화 기록 추가
        for turn in conversation_history:
            messages.append({"role": "user", "content": turn["question"]})
            messages.append({"role": "assistant", "content": turn["answer"]})
        
        # 후속 질문 추가
        messages.append({"role": "user", "content": follow_up_question})
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.8,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            
            return {
                "persona_id": persona.id,
                "question": follow_up_question,
                "response": content,
                "raw_response": content
            }
            
        except Exception as e:
            return {
                "persona_id": persona.id,
                "question": follow_up_question,
                "response": None,
                "error": str(e),
                "raw_response": None
            }
    
    def _extract_score(self, response: str) -> Optional[int]:
        """응답에서 점수를 추출합니다."""
        import re
        
        # "점수: X" 형식 찾기
        match = re.search(r'점수\s*[:：]\s*(\d+)', response)
        if match:
            score = int(match.group(1))
            if 1 <= score <= 7:
                return score
        
        # 첫 번째 숫자 찾기
        match = re.search(r'\b([1-7])\b', response)
        if match:
            return int(match.group(1))
        
        # 찾지 못한 경우
        return None
    
    def _extract_reasoning(self, response: str) -> Optional[str]:
        """응답에서 이유를 추출합니다."""
        import re
        
        # "이유:" 또는 "설명:" 뒤의 텍스트 추출
        match = re.search(r'(?:이유|설명)\s*[:：]\s*(.+)', response, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # "점수: X" 뒤의 나머지 텍스트
        match = re.search(r'점수\s*[:：]\s*\d+\s*(.+)', response, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # 전체 응답 반환
        return response.strip()
    
    def generate_survey_response(
        self,
        persona: Persona,
        questions: List[str],
        context: Optional[str] = None
    ) -> List[str]:
        """
        여러 설문 질문에 대한 응답을 생성합니다.
        
        Args:
            persona: 응답할 페르소나
            questions: 질문 리스트
            context: 설문 컨텍스트 (선택사항)
        
        Returns:
            응답 리스트
        """
        responses = []
        
        for question in questions:
            try:
                result = self.respond_to_survey_question(persona, question)
                if result.get('error'):
                    responses.append(f"오류: {result['error']}")
                else:
                    score = result.get('score', 'N/A')
                    reasoning = result.get('reasoning', '')
                    responses.append(f"점수: {score} - {reasoning}")
            except Exception as e:
                responses.append(f"오류: {str(e)}")
        
        return responses
    
    def generate_interview_response(
        self,
        persona: Persona,
        interview_guide: str,
        style: str = "친근한 대화"
    ) -> str:
        """
        인터뷰 가이드에 따른 응답을 생성합니다.
        
        Args:
            persona: 응답할 페르소나
            interview_guide: 인터뷰 가이드 (질문들)
            style: 인터뷰 스타일
        
        Returns:
            인터뷰 응답
        """
        questions = [q.strip() for q in interview_guide.split('\n') if q.strip()]
        
        if not questions:
            return "인터뷰 가이드가 비어있습니다."
        
        # 첫 번째 질문으로 시작
        try:
            result = self.respond_to_interview_question(persona, questions[0])
            if result.get('error'):
                return f"오류: {result['error']}"
            
            response = f"질문: {questions[0]}\n답변: {result['response']}\n\n"
            
            # 추가 질문들에 대한 응답
            for question in questions[1:]:
                try:
                    result = self.respond_to_interview_question(persona, question)
                    if result.get('error'):
                        response += f"질문: {question}\n답변: 오류 - {result['error']}\n\n"
                    else:
                        response += f"질문: {question}\n답변: {result['response']}\n\n"
                except Exception as e:
                    response += f"질문: {question}\n답변: 오류 - {str(e)}\n\n"
            
            return response.strip()
            
        except Exception as e:
            return f"인터뷰 진행 중 오류 발생: {str(e)}"
    
    def generate_experiment_response(
        self,
        persona: Persona,
        scenario: str,
        question: str,
        conditions: List[str] = None
    ) -> str:
        """
        실험 시나리오에 대한 응답을 생성합니다.
        
        Args:
            persona: 응답할 페르소나
            scenario: 실험 시나리오
            question: 실험 질문
            conditions: 실험 조건들 (선택사항)
        
        Returns:
            실험 응답
        """
        persona_context = self._build_persona_context(persona)
        
        system_prompt = f"""당신은 행동 실험에 참여하는 응답자입니다.
주어진 페르소나의 특성과 배경을 바탕으로 실험 상황에 진정성 있게 반응해야 합니다.

{persona_context}

실험 시나리오:
{scenario}

실험 조건: {', '.join(conditions) if conditions else '조건 없음'}

답변 지침:
- 주어진 시나리오에 대해 당신의 실제 반응을 표현하세요.
- 당신의 성격, 경험, 가치관을 반영한 답변을 하세요.
- 구체적이고 진정성 있는 답변을 제공하세요.
"""
        
        user_prompt = f"실험 질문: {question}"
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,
                max_tokens=800
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"실험 응답 생성 중 오류 발생: {str(e)}"


if __name__ == "__main__":
    # 테스트 코드
    from src.dataset_loader import DatasetLoader
    
    print("Testing AI Agent...")
    
    # 테스트용 페르소나 생성
    test_persona = Persona(
        id="test_1",
        data={
            "age": 28,
            "gender": "female",
            "occupation": "software engineer",
            "interests": "technology, reading, hiking"
        }
    )
    
    try:
        agent = AIAgent()
        
        # 설문 테스트
        print("\n=== Survey Test ===")
        survey_result = agent.respond_to_survey_question(
            test_persona,
            "나는 인공지능 기술이 사회에 긍정적인 영향을 미칠 것이라고 생각한다."
        )
        print(f"Score: {survey_result['score']}")
        print(f"Reasoning: {survey_result['reasoning']}")
        
        # 인터뷰 테스트
        print("\n=== Interview Test ===")
        interview_result = agent.respond_to_interview_question(
            test_persona,
            "당신의 직업을 선택한 이유는 무엇인가요?"
        )
        print(f"Response: {interview_result['response']}")
        
    except ValueError as e:
        print(f"Error: {e}")
        print("Please set OPENAI_API_KEY in .env file")

