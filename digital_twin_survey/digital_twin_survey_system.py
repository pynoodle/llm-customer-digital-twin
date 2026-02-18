"""
디지털 트윈 설문/인터뷰 시스템
Twin-2K-500 데이터셋을 활용한 AI 기반 설문조사 및 인터뷰 플랫폼
"""

import os
import json
import pandas as pd
from datasets import load_dataset
from openai import OpenAI
from typing import List, Dict, Optional
from datetime import datetime
import time


class DigitalTwinSurveySystem:
    """디지털 트윈 기반 설문/인터뷰 시스템"""
    
    def __init__(self, api_key: str):
        """
        시스템 초기화
        
        Args:
            api_key: OpenAI API 키
        """
        self.client = OpenAI(api_key=api_key)
        self.dataset = None
        self.selected_personas = []
        self.survey_results = []
        self.interview_results = []
        
    def load_dataset(self):
        """Twin-2K-500 데이터셋 로드"""
        print("📦 데이터셋 로딩 중...")
        try:
            # full_persona 구성 로드
            self.dataset = load_dataset("LLM-Digital-Twin/Twin-2K-500", "full_persona")
            print(f"✅ 데이터셋 로드 완료: {len(self.dataset['data'])}명의 페르소나")
            return True
        except Exception as e:
            print(f"❌ 데이터셋 로드 실패: {e}")
            return False
    
    def display_personas_summary(self, limit: int = 10):
        """페르소나 요약 정보 출력"""
        print("\n" + "="*80)
        print("👥 사용 가능한 페르소나 목록")
        print("="*80)
        
        for idx, row in enumerate(self.dataset['data'][:limit]):
            summary = row.get('persona_summary', 'No summary available')[:200]
            print(f"\n[{idx}] Participant ID: {row.get('participant_id', 'N/A')}")
            print(f"   요약: {summary}...")
        
        if len(self.dataset['data']) > limit:
            print(f"\n... 외 {len(self.dataset['data']) - limit}명 더 있음")
    
    def select_personas_by_criteria(self, criteria: Dict = None) -> List[int]:
        """
        기준에 따라 페르소나 선택
        
        Args:
            criteria: 선택 기준 (예: {"age_min": 25, "age_max": 45, "gender": "Female"})
            
        Returns:
            선택된 페르소나 인덱스 리스트
        """
        selected_indices = []
        
        if criteria is None:
            # 기준 없으면 전체 반환
            return list(range(len(self.dataset['data'])))
        
        print(f"\n🔍 필터링 기준: {criteria}")
        
        for idx, row in enumerate(self.dataset['data']):
            persona_text = row.get('persona_text', '')
            persona_json = row.get('persona_json', {})
            
            # 여기에 실제 필터링 로직 구현
            # 간단한 예시: 텍스트 검색
            if 'keyword' in criteria:
                if criteria['keyword'].lower() in persona_text.lower():
                    selected_indices.append(idx)
            else:
                selected_indices.append(idx)
        
        print(f"✅ {len(selected_indices)}명의 페르소나 선택됨")
        return selected_indices
    
    def select_personas_interactive(self) -> List[int]:
        """대화형 페르소나 선택"""
        print("\n" + "="*80)
        print("📋 페르소나 선택 방법")
        print("="*80)
        print("1. 전체 선택")
        print("2. 인덱스로 개별 선택 (예: 0,5,10)")
        print("3. 범위로 선택 (예: 0-20)")
        print("4. 랜덤 샘플링 (개수 입력)")
        print("5. 키워드 필터링")
        
        choice = input("\n선택 방법을 입력하세요 (1-5): ").strip()
        
        selected = []
        
        if choice == "1":
            # 전체 선택 (데모를 위해 최대 100명으로 제한)
            max_count = min(100, len(self.dataset['data']))
            confirm = input(f"전체 {max_count}명을 선택하시겠습니까? (y/n): ")
            if confirm.lower() == 'y':
                selected = list(range(max_count))
        
        elif choice == "2":
            # 개별 선택
            indices = input("인덱스를 쉼표로 구분해서 입력하세요 (예: 0,5,10): ")
            selected = [int(i.strip()) for i in indices.split(',')]
        
        elif choice == "3":
            # 범위 선택
            range_input = input("범위를 입력하세요 (예: 0-20): ")
            start, end = map(int, range_input.split('-'))
            selected = list(range(start, end + 1))
        
        elif choice == "4":
            # 랜덤 샘플링
            count = int(input("샘플링할 개수를 입력하세요: "))
            import random
            selected = random.sample(range(len(self.dataset['data'])), 
                                   min(count, len(self.dataset['data'])))
        
        elif choice == "5":
            # 키워드 필터링
            keyword = input("검색할 키워드를 입력하세요: ")
            selected = self.select_personas_by_criteria({"keyword": keyword})
        
        self.selected_personas = selected
        print(f"\n✅ {len(selected)}명의 페르소나가 선택되었습니다.")
        return selected
    
    def create_survey(self, questions: List[Dict]) -> Dict:
        """
        설문조사 생성
        
        Args:
            questions: 설문 질문 리스트
                [{"question": "질문 내용", "scale": "1-7", "type": "likert"}]
        
        Returns:
            설문조사 정의
        """
        survey = {
            "id": f"survey_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "questions": questions,
            "response_format": "1-7 scale"
        }
        return survey
    
    def create_interview(self, questions: List[str]) -> Dict:
        """
        인터뷰 생성
        
        Args:
            questions: 인터뷰 질문 리스트
        
        Returns:
            인터뷰 정의
        """
        interview = {
            "id": f"interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "created_at": datetime.now().isoformat(),
            "questions": questions,
            "response_format": "open-ended"
        }
        return interview
    
    def conduct_survey(self, survey: Dict, persona_indices: List[int] = None) -> pd.DataFrame:
        """
        설문조사 실시
        
        Args:
            survey: 설문조사 정의
            persona_indices: 응답할 페르소나 인덱스 (None이면 선택된 모든 페르소나)
        
        Returns:
            설문 결과 데이터프레임
        """
        if persona_indices is None:
            persona_indices = self.selected_personas
        
        print(f"\n🔄 {len(persona_indices)}명의 페르소나에게 설문조사 진행 중...")
        print(f"📝 총 {len(survey['questions'])}개 질문")
        
        results = []
        
        for idx, persona_idx in enumerate(persona_indices):
            print(f"\n진행: {idx+1}/{len(persona_indices)} ({(idx+1)/len(persona_indices)*100:.1f}%)")
            
            persona_data = self.dataset['data'][persona_idx]
            participant_id = persona_data.get('participant_id', f'P{persona_idx}')
            persona_text = persona_data.get('persona_text', '')
            
            persona_result = {
                'participant_id': participant_id,
                'persona_index': persona_idx
            }
            
            # 각 질문에 대해 답변 생성
            for q_idx, question_data in enumerate(survey['questions']):
                question = question_data['question']
                
                try:
                    # ChatGPT API 호출
                    response = self._get_survey_response(
                        persona_text=persona_text,
                        question=question,
                        scale="1-7"
                    )
                    
                    persona_result[f'Q{q_idx+1}'] = response['answer']
                    persona_result[f'Q{q_idx+1}_reasoning'] = response.get('reasoning', '')
                    
                except Exception as e:
                    print(f"  ⚠️ 오류 발생 (Participant {participant_id}, Q{q_idx+1}): {e}")
                    persona_result[f'Q{q_idx+1}'] = None
                    persona_result[f'Q{q_idx+1}_reasoning'] = f"Error: {e}"
                
                # API 요청 제한 방지를 위한 대기
                time.sleep(0.5)
            
            results.append(persona_result)
        
        df_results = pd.DataFrame(results)
        self.survey_results.append(df_results)
        
        print("\n✅ 설문조사 완료!")
        return df_results
    
    def conduct_interview(self, interview: Dict, persona_indices: List[int] = None) -> pd.DataFrame:
        """
        인터뷰 실시
        
        Args:
            interview: 인터뷰 정의
            persona_indices: 응답할 페르소나 인덱스
        
        Returns:
            인터뷰 결과 데이터프레임
        """
        if persona_indices is None:
            persona_indices = self.selected_personas
        
        print(f"\n🎤 {len(persona_indices)}명의 페르소나 인터뷰 진행 중...")
        print(f"📝 총 {len(interview['questions'])}개 질문")
        
        results = []
        
        for idx, persona_idx in enumerate(persona_indices):
            print(f"\n진행: {idx+1}/{len(persona_indices)} ({(idx+1)/len(persona_indices)*100:.1f}%)")
            
            persona_data = self.dataset['data'][persona_idx]
            participant_id = persona_data.get('participant_id', f'P{persona_idx}')
            persona_text = persona_data.get('persona_text', '')
            
            persona_result = {
                'participant_id': participant_id,
                'persona_index': persona_idx
            }
            
            # 각 질문에 대해 답변 생성
            for q_idx, question in enumerate(interview['questions']):
                try:
                    # ChatGPT API 호출
                    response = self._get_interview_response(
                        persona_text=persona_text,
                        question=question
                    )
                    
                    persona_result[f'Q{q_idx+1}'] = response['answer']
                    
                except Exception as e:
                    print(f"  ⚠️ 오류 발생 (Participant {participant_id}, Q{q_idx+1}): {e}")
                    persona_result[f'Q{q_idx+1}'] = f"Error: {e}"
                
                # API 요청 제한 방지
                time.sleep(0.5)
            
            results.append(persona_result)
        
        df_results = pd.DataFrame(results)
        self.interview_results.append(df_results)
        
        print("\n✅ 인터뷰 완료!")
        return df_results
    
    def _get_survey_response(self, persona_text: str, question: str, scale: str) -> Dict:
        """
        설문 질문에 대한 AI 응답 생성
        
        Args:
            persona_text: 페르소나 정보
            question: 설문 질문
            scale: 응답 척도 (예: "1-7")
        
        Returns:
            응답 딕셔너리 {"answer": int, "reasoning": str}
        """
        system_prompt = f"""You are an AI assistant simulating a survey participant. 
Your task is to answer the survey question based on the persona profile provided.

Response format:
- Provide a numerical answer on a scale of {scale}
- Provide brief reasoning for your answer

Be consistent with the persona's characteristics, beliefs, and past responses."""

        user_prompt = f"""Persona Profile:
{persona_text[:2000]}  # 토큰 제한을 위해 일부만 사용

Survey Question:
{question}

Please respond with a number from {scale} and explain your reasoning briefly.
Format your response as JSON:
{{"answer": <number>, "reasoning": "<brief explanation>"}}"""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",  # 또는 "gpt-4"
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.7,
                max_tokens=200
            )
            
            # JSON 파싱
            content = response.choices[0].message.content
            
            # JSON 추출 시도
            try:
                result = json.loads(content)
            except:
                # JSON 파싱 실패시 텍스트에서 숫자 추출
                import re
                numbers = re.findall(r'\b[1-7]\b', content)
                result = {
                    "answer": int(numbers[0]) if numbers else 4,  # 중간값 기본
                    "reasoning": content
                }
            
            return result
            
        except Exception as e:
            raise Exception(f"API 호출 실패: {e}")
    
    def _get_interview_response(self, persona_text: str, question: str) -> Dict:
        """
        인터뷰 질문에 대한 AI 응답 생성
        
        Args:
            persona_text: 페르소나 정보
            question: 인터뷰 질문
        
        Returns:
            응답 딕셔너리 {"answer": str}
        """
        system_prompt = """You are an AI assistant simulating an interview participant.
Your task is to answer the interview question based on the persona profile provided.

Guidelines:
- Answer in 2-4 sentences
- Be natural and conversational
- Stay consistent with the persona's characteristics
- Draw from the persona's past responses when relevant"""

        user_prompt = f"""Persona Profile:
{persona_text[:2000]}

Interview Question:
{question}

Please provide a natural, conversational response as this person would answer."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.8,
                max_tokens=300
            )
            
            return {
                "answer": response.choices[0].message.content.strip()
            }
            
        except Exception as e:
            raise Exception(f"API 호출 실패: {e}")
    
    def analyze_survey_results(self, df_results: pd.DataFrame) -> Dict:
        """설문 결과 분석"""
        print("\n" + "="*80)
        print("📊 설문조사 결과 분석")
        print("="*80)
        
        # 응답 열만 선택 (Q1, Q2, ...)
        response_cols = [col for col in df_results.columns if col.startswith('Q') 
                        and not col.endswith('_reasoning')]
        
        analysis = {
            'total_respondents': len(df_results),
            'questions_count': len(response_cols),
            'statistics': {}
        }
        
        for col in response_cols:
            responses = df_results[col].dropna()
            analysis['statistics'][col] = {
                'mean': responses.mean(),
                'median': responses.median(),
                'std': responses.std(),
                'min': responses.min(),
                'max': responses.max()
            }
            
            print(f"\n{col}:")
            print(f"  평균: {responses.mean():.2f}")
            print(f"  중앙값: {responses.median():.1f}")
            print(f"  표준편차: {responses.std():.2f}")
            print(f"  범위: {responses.min():.0f} - {responses.max():.0f}")
        
        return analysis
    
    def export_results(self, filename: str, format: str = 'csv'):
        """결과 내보내기"""
        if format == 'csv':
            if self.survey_results:
                for idx, df in enumerate(self.survey_results):
                    output_file = f"{filename}_survey_{idx+1}.csv"
                    df.to_csv(output_file, index=False, encoding='utf-8-sig')
                    print(f"✅ 설문 결과 저장: {output_file}")
            
            if self.interview_results:
                for idx, df in enumerate(self.interview_results):
                    output_file = f"{filename}_interview_{idx+1}.csv"
                    df.to_csv(output_file, index=False, encoding='utf-8-sig')
                    print(f"✅ 인터뷰 결과 저장: {output_file}")
        
        elif format == 'json':
            results = {
                'survey_results': [df.to_dict('records') for df in self.survey_results],
                'interview_results': [df.to_dict('records') for df in self.interview_results]
            }
            with open(f"{filename}.json", 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            print(f"✅ 결과 저장: {filename}.json")


def main():
    """메인 실행 함수"""
    print("="*80)
    print("🤖 디지털 트윈 설문/인터뷰 시스템")
    print("="*80)
    
    # API 키 설정
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        api_key = input("OpenAI API 키를 입력하세요: ").strip()
    
    # 시스템 초기화
    system = DigitalTwinSurveySystem(api_key)
    
    # 데이터셋 로드
    if not system.load_dataset():
        print("데이터셋 로드 실패. 프로그램을 종료합니다.")
        return
    
    # 페르소나 미리보기
    system.display_personas_summary(limit=5)
    
    # 페르소나 선택
    print("\n📝 응답자를 선택하세요")
    system.select_personas_interactive()
    
    # 조사 유형 선택
    print("\n" + "="*80)
    print("📋 조사 유형 선택")
    print("="*80)
    print("1. 설문조사 (Survey) - 1-7 척도 응답")
    print("2. 인터뷰 (Interview) - 개방형 질문")
    print("3. 둘 다")
    
    choice = input("\n선택하세요 (1-3): ").strip()
    
    # 설문조사 예시
    if choice in ["1", "3"]:
        print("\n📝 설문조사 질문 입력")
        survey_questions = []
        
        # 데모를 위한 샘플 질문
        use_sample = input("샘플 질문을 사용하시겠습니까? (y/n): ")
        if use_sample.lower() == 'y':
            survey_questions = [
                {"question": "How satisfied are you with your current job?", 
                 "scale": "1-7", "type": "likert"},
                {"question": "How likely are you to recommend this product to a friend?", 
                 "scale": "1-7", "type": "likert"},
                {"question": "How much do you agree with the statement: 'AI will benefit society'?", 
                 "scale": "1-7", "type": "likert"}
            ]
        else:
            num_questions = int(input("질문 개수를 입력하세요: "))
            for i in range(num_questions):
                q = input(f"질문 {i+1}: ")
                survey_questions.append({
                    "question": q,
                    "scale": "1-7",
                    "type": "likert"
                })
        
        # 설문 생성 및 실시
        survey = system.create_survey(survey_questions)
        
        # 소수 샘플로 테스트
        test_size = min(3, len(system.selected_personas))
        confirm = input(f"\n⚠️ 먼저 {test_size}명으로 테스트하시겠습니까? (y/n): ")
        
        if confirm.lower() == 'y':
            test_personas = system.selected_personas[:test_size]
            results = system.conduct_survey(survey, test_personas)
        else:
            results = system.conduct_survey(survey)
        
        # 결과 분석
        system.analyze_survey_results(results)
    
    # 인터뷰 예시
    if choice in ["2", "3"]:
        print("\n🎤 인터뷰 질문 입력")
        interview_questions = []
        
        use_sample = input("샘플 질문을 사용하시겠습니까? (y/n): ")
        if use_sample.lower() == 'y':
            interview_questions = [
                "What motivated you to choose your current career path?",
                "How do you balance work and personal life?",
                "What are your thoughts on remote work?"
            ]
        else:
            num_questions = int(input("질문 개수를 입력하세요: "))
            for i in range(num_questions):
                q = input(f"질문 {i+1}: ")
                interview_questions.append(q)
        
        # 인터뷰 생성 및 실시
        interview = system.create_interview(interview_questions)
        
        test_size = min(3, len(system.selected_personas))
        confirm = input(f"\n⚠️ 먼저 {test_size}명으로 테스트하시겠습니까? (y/n): ")
        
        if confirm.lower() == 'y':
            test_personas = system.selected_personas[:test_size]
            results = system.conduct_interview(interview, test_personas)
        else:
            results = system.conduct_interview(interview)
        
        # 결과 미리보기
        print("\n" + "="*80)
        print("📄 인터뷰 결과 미리보기")
        print("="*80)
        print(results.head())
    
    # 결과 저장
    save = input("\n결과를 저장하시겠습니까? (y/n): ")
    if save.lower() == 'y':
        filename = input("파일명을 입력하세요 (확장자 제외): ")
        system.export_results(filename, format='csv')
    
    print("\n✅ 프로그램 종료")


if __name__ == "__main__":
    main()
