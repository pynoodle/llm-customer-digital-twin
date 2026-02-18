"""
Hugging Face Twin-2K-500 데이터셋 로더 모듈
디지털 트윈 페르소나 데이터를 로드하고 관리합니다.
"""

from datasets import load_dataset
import pandas as pd
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json as json_module


@dataclass
class Persona:
    """디지털 트윈 페르소나 데이터 클래스"""
    id: str
    data: Dict[str, Any]
    
    def __repr__(self):
        return f"Persona(id={self.id})"
    
    def get_summary(self) -> str:
        """페르소나의 요약 정보를 반환합니다."""
        summary_parts = []
        
        # 주요 필드만 표시 (데이터셋 구조에 따라 조정 필요)
        key_fields = ['age', 'gender', 'occupation', 'education', 'location', 
                     'interests', 'personality', 'background']
        
        for field in key_fields:
            if field in self.data and self.data[field]:
                summary_parts.append(f"{field.capitalize()}: {self.data[field]}")
        
        # 모든 필드가 없으면 전체 데이터 표시
        if not summary_parts:
            for key, value in self.data.items():
                if isinstance(value, str) and len(str(value)) < 200:
                    summary_parts.append(f"{key}: {value}")
        
        return "\n".join(summary_parts) if summary_parts else str(self.data)


class DatasetLoader:
    """Twin-2K-500 데이터셋 로더"""
    
    def __init__(self):
        self.dataset = None
        self.personas: List[Persona] = []
        self.df: Optional[pd.DataFrame] = None
    
    def load(self, subset: str = "full_persona") -> None:
        """
        Hugging Face에서 데이터셋을 로드합니다.
        
        Args:
            subset: 데이터셋 서브셋 이름 (기본값: "full_persona")
        """
        print(f"Loading dataset: LLM-Digital-Twin/Twin-2K-500 (subset: {subset})...")
        
        try:
            self.dataset = load_dataset("LLM-Digital-Twin/Twin-2K-500", subset)
            
            # 'data' split을 DataFrame으로 변환
            if 'data' in self.dataset:
                self.df = pd.DataFrame(self.dataset['data'])
            else:
                # split이 없으면 첫 번째 사용 가능한 split 사용
                available_splits = list(self.dataset.keys())
                if available_splits:
                    self.df = pd.DataFrame(self.dataset[available_splits[0]])
                else:
                    raise ValueError("No data splits found in dataset")
            
            # persona_json 파싱하여 DataFrame 확장
            print("[INFO] Parsing persona_json fields...")
            self._expand_persona_json()
            
            # Persona 객체 생성
            self._create_personas()
            
            print(f"[OK] Successfully loaded {len(self.personas)} personas")
            print(f"[OK] Total fields available: {len(self.df.columns)}")
            
        except Exception as e:
            print(f"[ERROR] Error loading dataset: {e}")
            raise
    
    def _expand_persona_json(self) -> None:
        """persona_json 필드를 파싱하여 DataFrame에 추가 컬럼으로 확장합니다."""
        if 'persona_json' not in self.df.columns:
            return
        
        # 모든 JSON 데이터를 파싱하여 새 컬럼 생성
        json_data_list = []
        
        for idx, row in self.df.iterrows():
            persona_json = row.get('persona_json')
            
            if persona_json:
                try:
                    if isinstance(persona_json, str):
                        parsed_data = json_module.loads(persona_json)
                    else:
                        parsed_data = persona_json
                    
                    # 숫자 키를 의미 있는 이름으로 변환
                    renamed_data = {}
                    for key, value in parsed_data.items():
                        # 키가 순수 숫자인 경우 Q{숫자} 형태로 변환
                        if str(key).isdigit():
                            renamed_key = f"question_{key}"
                        else:
                            renamed_key = key
                        renamed_data[renamed_key] = value
                    
                    json_data_list.append(renamed_data)
                except:
                    json_data_list.append({})
            else:
                json_data_list.append({})
        
        # JSON 데이터를 DataFrame으로 변환
        if json_data_list:
            json_df = pd.DataFrame(json_data_list)
            
            # 원본 DataFrame과 병합
            # 중복 컬럼명 방지
            for col in json_df.columns:
                if col not in self.df.columns:
                    self.df[col] = json_df[col]
                else:
                    self.df[f'json_{col}'] = json_df[col]
            
            print(f"[OK] Expanded {len(json_df.columns)} fields from persona_json")
            
            # 필드 이름 샘플 출력 (처음 10개)
            sample_fields = list(json_df.columns)[:10]
            if sample_fields:
                print(f"[INFO] Sample fields: {', '.join(sample_fields)}")
    
    def _create_personas(self) -> None:
        """DataFrame에서 Persona 객체들을 생성합니다."""
        self.personas = []
        
        for idx, row in self.df.iterrows():
            persona_data = row.to_dict()
            persona_id = str(idx)
            
            # ID 필드가 있으면 사용
            if 'id' in persona_data:
                persona_id = str(persona_data['id'])
            elif 'persona_id' in persona_data:
                persona_id = str(persona_data['persona_id'])
            elif 'participant_id' in persona_data:
                persona_id = str(persona_data['participant_id'])
            elif 'pid' in persona_data:
                persona_id = str(persona_data['pid'])
            
            # persona_json은 이미 _expand_persona_json에서 파싱되어 DataFrame에 추가됨
            persona = Persona(id=persona_id, data=persona_data)
            self.personas.append(persona)
    
    def get_all_personas(self) -> List[Persona]:
        """모든 페르소나를 반환합니다."""
        return self.personas
    
    def get_persona_by_id(self, persona_id: str) -> Optional[Persona]:
        """ID로 특정 페르소나를 반환합니다."""
        for persona in self.personas:
            if persona.id == persona_id:
                return persona
        return None
    
    def search_personas(self, filters: Dict[str, Any]) -> List[Persona]:
        """
        필터 조건에 맞는 페르소나를 검색합니다.
        
        Args:
            filters: 검색 조건 딕셔너리 (예: {'gender': 'female', 'age': 25})
        
        Returns:
            필터링된 페르소나 리스트
        """
        if not filters:
            return self.personas
        
        filtered = []
        
        for persona in self.personas:
            match = True
            for key, value in filters.items():
                # 키가 존재하지 않으면 매치 실패
                if key not in persona.data:
                    match = False
                    break
                
                # 값이 리스트인 경우 (multiple choice)
                if isinstance(value, list):
                    if persona.data[key] not in value:
                        match = False
                        break
                # 문자열 검색 (대소문자 무시)
                elif isinstance(value, str) and isinstance(persona.data[key], str):
                    if value.lower() not in persona.data[key].lower():
                        match = False
                        break
                # 정확한 매치
                else:
                    if persona.data[key] != value:
                        match = False
                        break
            
            if match:
                filtered.append(persona)
        
        return filtered
    
    def get_random_sample(self, n: int = 10, seed: Optional[int] = None) -> List[Persona]:
        """
        무작위 샘플을 추출합니다.
        
        Args:
            n: 샘플 크기
            seed: 랜덤 시드
        
        Returns:
            무작위로 선택된 페르소나 리스트
        """
        import random
        
        if seed is not None:
            random.seed(seed)
        
        sample_size = min(n, len(self.personas))
        return random.sample(self.personas, sample_size)
    
    def get_available_fields(self) -> List[str]:
        """데이터셋에서 사용 가능한 모든 필드를 반환합니다."""
        if self.df is not None:
            return list(self.df.columns)
        return []
    
    def get_categorized_fields(self) -> Dict[str, List[str]]:
        """필드를 카테고리별로 분류하여 반환합니다."""
        if self.df is None:
            return {}
        
        # DataFrame에서 모든 컬럼 가져오기
        all_fields = list(self.df.columns)
        
        # 필드를 카테고리별로 분류
        categories = {
            "인구통계": [],
            "직업경제": [],
            "교육": [],
            "성격심리": [],
            "경제특성": [],
            "라이프스타일": [],
            "지리위치": [],
            "관계가족": [],
            "가치관태도": [],
            "기술미디어": [],
            "기타": []
        }
        
        # 키워드 기반 분류
        demographic_keywords = ['age', 'gender', 'sex', 'race', 'ethnicity', 'birth', 'year_birth']
        job_keywords = ['occupation', 'job', 'work', 'employment', 'career', 'income', 'salary', 'industry']
        education_keywords = ['education', 'degree', 'school', 'college', 'university', 'student', 'academic']
        personality_keywords = ['personality', 'trait', 'character', 'openness', 'conscientious', 
                               'extraversion', 'agreeable', 'neuroticism', 'emotional', 'big_five']
        economic_keywords = ['economic', 'financial', 'wealth', 'assets', 'debt', 'saving', 'budget']
        lifestyle_keywords = ['lifestyle', 'hobby', 'interest', 'activity', 'leisure', 'sport', 'health', 'exercise']
        location_keywords = ['location', 'city', 'state', 'region', 'country', 'address', 'zip', 'urban', 'rural']
        relationship_keywords = ['marital', 'married', 'relationship', 'family', 'children', 'spouse', 'partner', 'household']
        value_keywords = ['value', 'belief', 'attitude', 'opinion', 'political', 'religious', 'moral', 'question_']
        tech_keywords = ['technology', 'tech', 'digital', 'internet', 'social_media', 'phone', 'computer', 'online']
        
        for field in all_fields:
            # 필드 이름을 문자열로 변환
            field_str = str(field)
            field_lower = field_str.lower()
            categorized = False
            
            # 기본 필드는 제외
            if field_str in ['persona_text', 'persona_summary', 'persona_json', 'participant_id', 'pid']:
                continue
            
            # 카테고리별 분류
            if any(kw in field_lower for kw in demographic_keywords):
                categories["인구통계"].append(field_str)
                categorized = True
            elif any(kw in field_lower for kw in job_keywords):
                categories["직업경제"].append(field_str)
                categorized = True
            elif any(kw in field_lower for kw in education_keywords):
                categories["교육"].append(field_str)
                categorized = True
            elif any(kw in field_lower for kw in personality_keywords):
                categories["성격심리"].append(field_str)
                categorized = True
            elif any(kw in field_lower for kw in economic_keywords):
                categories["경제특성"].append(field_str)
                categorized = True
            elif any(kw in field_lower for kw in lifestyle_keywords):
                categories["라이프스타일"].append(field_str)
                categorized = True
            elif any(kw in field_lower for kw in location_keywords):
                categories["지리위치"].append(field_str)
                categorized = True
            elif any(kw in field_lower for kw in relationship_keywords):
                categories["관계가족"].append(field_str)
                categorized = True
            elif any(kw in field_lower for kw in value_keywords):
                categories["가치관태도"].append(field_str)
                categorized = True
            elif any(kw in field_lower for kw in tech_keywords):
                categories["기술미디어"].append(field_str)
                categorized = True
            
            if not categorized:
                categories["기타"].append(field_str)
        
        # 빈 카테고리 제거 및 정렬
        return {k: sorted(v) for k, v in categories.items() if v}
    
    def get_field_unique_values(self, field: str) -> List[Any]:
        """특정 필드의 고유 값들을 반환합니다."""
        if self.df is not None and field in self.df.columns:
            return sorted(self.df[field].dropna().unique().tolist())
        return []


if __name__ == "__main__":
    # 테스트 코드
    loader = DatasetLoader()
    loader.load()
    
    print(f"\nTotal personas: {len(loader.get_all_personas())}")
    print(f"\nAvailable fields: {loader.get_available_fields()}")
    
    # 첫 번째 페르소나 출력
    if loader.personas:
        print(f"\nFirst persona:")
        print(loader.personas[0].get_summary())

