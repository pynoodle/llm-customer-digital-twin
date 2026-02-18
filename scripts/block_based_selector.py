"""
블록 기반 설문대상 선정 시스템
"""

import pandas as pd
import json
import os
import sys
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

# Windows 콘솔 인코딩 문제 해결
if sys.platform == "win32":
    import codecs
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
    sys.stderr = codecs.getwriter("utf-8")(sys.stderr.detach())

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

class BlockBasedSelector:
    """블록 기반 설문대상 선정 시스템"""
    
    def __init__(self, csv_path: str = "processed_dataset/block_based_dataset.csv"):
        self.csv_path = csv_path
        self.df = None
        self.personas = []
        self.metadata = None
        self.block_categories = None
        
    def load(self) -> None:
        """블록 기반 데이터셋을 로드합니다."""
        print(f"[INFO] 블록 기반 데이터셋 로딩 중: {self.csv_path}")
        
        if not os.path.exists(self.csv_path):
            print(f"[ERROR] 파일을 찾을 수 없습니다: {self.csv_path}")
            print("[INFO] 먼저 create_block_based_dataset.py를 실행하여 데이터를 생성하세요.")
            return
        
        try:
            # CSV 파일 로드
            self.df = pd.read_csv(self.csv_path, encoding='utf-8-sig')
            print(f"[OK] 데이터 로드 완료: {len(self.df)}개 레코드")
            print(f"[INFO] 컬럼 수: {len(self.df.columns)}")
            
            # 메타데이터 로드
            metadata_path = os.path.join(os.path.dirname(self.csv_path), "block_dataset_metadata.json")
            if os.path.exists(metadata_path):
                with open(metadata_path, 'r', encoding='utf-8') as f:
                    self.metadata = json.load(f)
                print(f"[OK] 메타데이터 로드 완료")
            
            # 페르소나 객체 생성
            self._create_personas()
            
            # 블록 카테고리 설정
            self._setup_block_categories()
            
        except Exception as e:
            print(f"[ERROR] 데이터 로드 실패: {e}")
            return
    
    def _create_personas(self) -> None:
        """DataFrame에서 페르소나 객체를 생성합니다."""
        self.personas = []
        
        for idx, row in self.df.iterrows():
            persona_data = row.to_dict()
            persona_id = str(persona_data.get('pid', idx))
            
            persona = Persona(id=persona_id, data=persona_data)
            self.personas.append(persona)
        
        print(f"[OK] {len(self.personas)}개 페르소나 생성 완료")
    
    def _setup_block_categories(self) -> None:
        """블록 카테고리를 설정합니다."""
        if not self.metadata:
            return
        
        self.block_categories = self.metadata.get('categories', {})
    
    def get_available_blocks(self) -> List[str]:
        """사용 가능한 블록 목록을 반환합니다."""
        if self.df is None:
            return []
        
        # has_로 시작하는 컬럼들에서 블록 이름 추출
        block_columns = [col for col in self.df.columns if col.startswith('has_')]
        blocks = [col.replace('has_', '').replace('_', ' ').title() for col in block_columns]
        return sorted(blocks)
    
    def get_block_categories(self) -> Dict[str, List[str]]:
        """블록을 카테고리별로 분류합니다."""
        if not self.block_categories:
            return {}
        
        return self.block_categories
    
    def get_block_statistics(self) -> Dict[str, Dict[str, Any]]:
        """블록별 통계 정보를 반환합니다."""
        if self.df is None:
            return {}
        
        stats = {}
        block_columns = [col for col in self.df.columns if col.startswith('has_')]
        
        for col in block_columns:
            block_name = col.replace('has_', '').replace('_', ' ').title()
            question_col = f"questions_{col.replace('has_', '')}"
            
            presence_count = self.df[col].sum()
            presence_rate = (presence_count / len(self.df)) * 100
            
            avg_questions = 0
            if question_col in self.df.columns:
                avg_questions = self.df[question_col].mean()
            
            stats[block_name] = {
                'presence_count': int(presence_count),
                'presence_rate': round(presence_rate, 1),
                'avg_questions': round(avg_questions, 1)
            }
        
        return stats
    
    def filter_by_blocks(self, required_blocks: List[str], optional_blocks: List[str] = None) -> List[Persona]:
        """블록 조건에 따라 페르소나를 필터링합니다."""
        if self.df is None:
            return []
        
        filtered_df = self.df.copy()
        
        # 필수 블록 조건
        for block in required_blocks:
            safe_name = block.lower().replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')
            has_col = f"has_{safe_name}"
            if has_col in filtered_df.columns:
                filtered_df = filtered_df[filtered_df[has_col] == 1]
        
        # 선택적 블록 조건
        if optional_blocks:
            for block in optional_blocks:
                safe_name = block.lower().replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')
                has_col = f"has_{safe_name}"
                if has_col in filtered_df.columns:
                    filtered_df = filtered_df[filtered_df[has_col] == 1]
        
        # 결과를 페르소나 객체로 변환
        results = []
        for idx, row in filtered_df.iterrows():
            persona_data = row.to_dict()
            persona_id = str(persona_data.get('pid', idx))
            persona = Persona(id=persona_id, data=persona_data)
            results.append(persona)
        
        return results
    
    def filter_by_question_count(self, block_name: str, min_questions: int = 1, max_questions: int = None) -> List[Persona]:
        """특정 블록의 질문 수로 필터링합니다."""
        if self.df is None:
            return []
        
        safe_name = block_name.lower().replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')
        question_col = f"questions_{safe_name}"
        
        if question_col not in self.df.columns:
            return []
        
        filtered_df = self.df[self.df[question_col] >= min_questions]
        
        if max_questions is not None:
            filtered_df = filtered_df[filtered_df[question_col] <= max_questions]
        
        # 결과를 페르소나 객체로 변환
        results = []
        for idx, row in filtered_df.iterrows():
            persona_data = row.to_dict()
            persona_id = str(persona_data.get('pid', idx))
            persona = Persona(id=persona_id, data=persona_data)
            results.append(persona)
        
        return results
    
    def get_random_sample(self, n: int = 10, seed: Optional[int] = None, 
                         required_blocks: List[str] = None) -> List[Persona]:
        """랜덤 샘플을 반환합니다."""
        import random
        
        if seed is not None:
            random.seed(seed)
        
        # 필터링된 데이터에서 샘플링
        if required_blocks:
            candidates = self.filter_by_blocks(required_blocks)
        else:
            candidates = self.personas
        
        if n >= len(candidates):
            return candidates.copy()
        
        return random.sample(candidates, n)
    
    def get_persona_by_id(self, persona_id: str) -> Optional[Persona]:
        """ID로 페르소나를 찾습니다."""
        for persona in self.personas:
            if persona.id == persona_id:
                return persona
        return None
    
    def show_filtering_options(self) -> None:
        """필터링 옵션을 표시합니다."""
        print("[INFO] 블록 기반 설문대상 선정 옵션")
        print("="*50)
        
        # 카테고리별 블록 표시
        categories = self.get_block_categories()
        if categories:
            for category, blocks in categories.items():
                print(f"\n[INFO] {category.replace('_', ' ').title()}:")
                for block in blocks[:5]:  # 처음 5개만 표시
                    print(f"  - {block}")
                if len(blocks) > 5:
                    print(f"  ... 외 {len(blocks) - 5}개")
        
        # 통계 정보 표시
        print(f"\n[INFO] 블록 통계 (상위 10개):")
        stats = self.get_block_statistics()
        sorted_stats = sorted(stats.items(), key=lambda x: x[1]['presence_rate'], reverse=True)
        
        for i, (block_name, stat) in enumerate(sorted_stats[:10], 1):
            print(f"  {i:2d}. {block_name:<30} {stat['presence_rate']:5.1f}% ({stat['presence_count']:,}명)")
    
    def export_filtered_results(self, personas: List[Persona], filename: str) -> None:
        """필터링된 결과를 파일로 저장합니다."""
        if not personas:
            print("[ERROR] 저장할 데이터가 없습니다.")
            return
        
        # 페르소나 데이터를 DataFrame으로 변환
        data = []
        for persona in personas:
            data.append(persona.data)
        
        df = pd.DataFrame(data)
        
        # CSV 저장
        csv_path = f"results/{filename}.csv"
        os.makedirs("results", exist_ok=True)
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        print(f"[OK] 결과 저장 완료: {csv_path}")
        
        # JSON 저장
        json_path = f"results/{filename}.json"
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"[OK] JSON 저장 완료: {json_path}")

def main():
    """메인 함수"""
    print("[INFO] 블록 기반 설문대상 선정 시스템")
    print("="*50)
    
    # 시스템 초기화
    selector = BlockBasedSelector()
    selector.load()
    
    if not selector.personas:
        print("[ERROR] 데이터 로드 실패")
        return
    
    # 필터링 옵션 표시
    selector.show_filtering_options()
    
    # 예시 필터링
    print(f"\n[INFO] 예시 필터링:")
    
    # 1. 핵심 블록을 가진 페르소나
    core_blocks = ["Demographics", "Personality", "Cognitive Tests"]
    core_personas = selector.filter_by_blocks(core_blocks)
    print(f"  - 핵심 블록 보유자: {len(core_personas)}명")
    
    # 2. 심리학 실험 참여자
    psychology_blocks = ["False Consensus", "Base Rate 70 Engineers", "Disease Loss"]
    psychology_personas = selector.filter_by_blocks(psychology_blocks)
    print(f"  - 심리학 실험 참여자: {len(psychology_personas)}명")
    
    # 3. 경제적 선호도 연구 대상
    economic_personas = selector.filter_by_question_count("Economic Preferences", min_questions=10)
    print(f"  - 경제적 선호도 연구 대상: {len(economic_personas)}명")
    
    # 4. 랜덤 샘플링
    random_sample = selector.get_random_sample(n=5, seed=42, required_blocks=["Demographics"])
    print(f"  - 랜덤 샘플 (Demographics 필수): {len(random_sample)}명")
    
    print(f"\n[OK] 블록 기반 선정 시스템 준비 완료!")

if __name__ == "__main__":
    main()
