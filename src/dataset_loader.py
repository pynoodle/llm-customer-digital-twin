"""
Twin-2K-500 데이터셋 로더
전처리된 CSV 파일을 사용하여 빠른 성능을 제공합니다.
"""

import pandas as pd
import json
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import os


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
        
        # 주요 필드만 표시
        key_fields = ['persona_text', 'persona_summary']
        
        for field in key_fields:
            if field in self.data and self.data[field]:
                value = str(self.data[field])
                if len(value) > 200:
                    value = value[:200] + "..."
                summary_parts.append(f"{field.capitalize()}: {value}")
        
        return "\n".join(summary_parts) if summary_parts else "No summary available"


class DatasetLoader:
    """전처리된 데이터셋 로더"""
    
    def __init__(self, csv_path: str = "processed_dataset/twin2k500_processed.csv"):
        self.csv_path = csv_path
        self.df = None
        self.personas = []
        self.stats = None
    
    def load(self, subset: str = "full_persona") -> None:
        """전처리된 CSV 파일을 로드합니다."""
        print(f"Loading processed dataset: {self.csv_path}...")
        
        if not os.path.exists(self.csv_path):
            print(f"[ERROR] Processed dataset not found: {self.csv_path}")
            print("[INFO] Please run create_processed_dataset.py first to create the processed dataset.")
            raise FileNotFoundError(f"Processed dataset not found: {self.csv_path}")
        
        try:
            # CSV 파일 로드
            self.df = pd.read_csv(self.csv_path, encoding='utf-8-sig')
            print(f"[OK] Successfully loaded {len(self.df)} personas")
            print(f"[OK] Available columns: {list(self.df.columns)}")
            
            # 통계 정보 로드
            stats_path = os.path.join(os.path.dirname(self.csv_path), "dataset_stats.json")
            if os.path.exists(stats_path):
                with open(stats_path, 'r', encoding='utf-8') as f:
                    self.stats = json.load(f)
                print(f"[OK] Statistics loaded")
            
            # 페르소나 객체 생성
            self._create_personas()
            
        except Exception as e:
            print(f"[ERROR] Failed to load dataset: {e}")
            raise
    
    def _create_personas(self) -> None:
        """DataFrame에서 페르소나 객체를 생성합니다."""
        self.personas = []
        
        for idx, row in self.df.iterrows():
            persona_data = row.to_dict()
            persona_id = str(persona_data.get('id', idx))
            
            persona = Persona(id=persona_id, data=persona_data)
            self.personas.append(persona)
        
        print(f"[OK] Created {len(self.personas)} persona objects")
    
    def get_all_personas(self) -> List[Persona]:
        """모든 페르소나를 반환합니다."""
        return self.personas
    
    def get_persona_by_id(self, persona_id: str) -> Optional[Persona]:
        """ID로 페르소나를 찾습니다."""
        for persona in self.personas:
            if persona.id == persona_id:
                return persona
        return None
    
    def search_personas(self, filters: Dict[str, Any]) -> List[Persona]:
        """필터 조건에 맞는 페르소나를 검색합니다."""
        if self.df is None:
            return []
        
        # DataFrame에서 필터링
        filtered_df = self.df.copy()
        
        for field, value in filters.items():
            if field in filtered_df.columns:
                if isinstance(value, list):
                    filtered_df = filtered_df[filtered_df[field].isin(value)]
                else:
                    filtered_df = filtered_df[filtered_df[field] == value]
        
        # 결과를 페르소나 객체로 변환
        results = []
        for idx, row in filtered_df.iterrows():
            persona_data = row.to_dict()
            persona_id = str(persona_data.get('id', idx))
            persona = Persona(id=persona_id, data=persona_data)
            results.append(persona)
        
        return results
    
    def get_random_sample(self, n: int = 10, seed: Optional[int] = None) -> List[Persona]:
        """랜덤 샘플을 반환합니다."""
        import random
        
        if seed is not None:
            random.seed(seed)
        
        if n >= len(self.personas):
            return self.personas.copy()
        
        return random.sample(self.personas, n)
    
    def get_available_fields(self) -> List[str]:
        """사용 가능한 필드 목록을 반환합니다."""
        if self.df is None:
            return []
        return list(self.df.columns)
    
    def get_categorized_fields(self) -> Dict[str, List[str]]:
        """필드를 카테고리별로 분류합니다."""
        if self.df is None:
            return {}
        
        all_fields = list(self.df.columns)
        categories = {
            "기본정보": [],
            "질문응답": [],
            "기타": []
        }
        
        for field in all_fields:
            field_str = str(field)
            field_lower = field_str.lower()
            
            if field_str in ['id', 'persona_text', 'persona_summary']:
                categories["기본정보"].append(field_str)
            elif field_str.startswith('question_'):
                categories["질문응답"].append(field_str)
            else:
                categories["기타"].append(field_str)
        
        return {k: sorted(v) for k, v in categories.items() if v}
    
    def get_field_unique_values(self, field: str) -> List[Any]:
        """특정 필드의 고유값 목록을 반환합니다."""
        if self.df is None or field not in self.df.columns:
            return []
        
        unique_values = self.df[field].dropna().unique().tolist()
        return sorted(unique_values)
    
    def get_dataset_stats(self) -> Dict[str, Any]:
        """데이터셋 통계 정보를 반환합니다."""
        if self.stats:
            return self.stats
        
        if self.df is None:
            return {}
        
        return {
            'total_records': len(self.df),
            'total_columns': len(self.df.columns),
            'columns': list(self.df.columns)
        }
    
    def get_sample_data(self, n: int = 5) -> List[Dict[str, Any]]:
        """샘플 데이터를 반환합니다."""
        if self.df is None:
            return []
        
        sample_df = self.df.head(n)
        return sample_df.to_dict('records')


def main():
    """테스트 함수"""
    print("🧪 DatasetLoader 테스트")
    
    loader = DatasetLoader()
    try:
        loader.load()
        
        if loader.personas:
            print(f"\n✅ 로드된 페르소나 수: {len(loader.personas)}")
            
            # 샘플 페르소나 출력
            sample = loader.personas[0]
            print(f"\n👤 샘플 페르소나 (ID: {sample.id}):")
            print(sample.get_summary())
            
            # 필드 정보
            fields = loader.get_available_fields()
            print(f"\n📊 사용 가능한 필드: {len(fields)}개")
            print(f"필드 목록: {fields}")
            
            # 카테고리별 필드
            categorized = loader.get_categorized_fields()
            print(f"\n📂 카테고리별 필드:")
            for category, field_list in categorized.items():
                print(f"  {category}: {len(field_list)}개")
                if field_list:
                    print(f"    예시: {field_list[:3]}")
        else:
            print("❌ 데이터 로드 실패")
    except Exception as e:
        print(f"❌ 오류 발생: {e}")


if __name__ == "__main__":
    main()