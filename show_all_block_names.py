"""
persona_json의 모든 블록 이름 출력
"""

import pandas as pd
from datasets import load_dataset
import json
from collections import Counter

def show_all_block_names():
    """persona_json의 모든 블록 이름을 출력합니다."""
    print("📋 Twin-2K-500 데이터셋 모든 블록 이름")
    print("="*60)
    
    # 데이터셋 로드
    dataset = load_dataset("LLM-Digital-Twin/Twin-2K-500", "full_persona")
    df = dataset['data'].to_pandas()
    
    # 모든 레코드의 블록 이름 수집
    all_block_names = []
    block_name_with_questions = []
    
    print("🔄 모든 레코드에서 블록 이름 수집 중...")
    
    for idx, row in df.iterrows():
        try:
            parsed = json.loads(row['persona_json'])
            if isinstance(parsed, list):
                for block in parsed:
                    if isinstance(block, dict) and 'BlockName' in block:
                        block_name = block['BlockName']
                        all_block_names.append(block_name)
                        
                        # 질문 수도 함께 저장
                        question_count = len(block.get('Questions', []))
                        block_name_with_questions.append((block_name, question_count))
        except Exception as e:
            print(f"⚠️ 레코드 {idx} 파싱 실패: {e}")
    
    # 고유 블록 이름과 빈도 계산
    unique_blocks = Counter(all_block_names)
    
    print(f"\n📊 블록 통계:")
    print(f"  - 총 블록 인스턴스: {len(all_block_names):,}")
    print(f"  - 고유 블록 이름: {len(unique_blocks)}")
    
    print(f"\n🏷️ 모든 블록 이름 (빈도순):")
    print("-" * 60)
    
    for i, (block_name, count) in enumerate(unique_blocks.most_common(), 1):
        percentage = count / len(df) * 100
        print(f"{i:2d}. {block_name:<50} {count:4d}회 ({percentage:5.1f}%)")
    
    # 질문 수별 블록 분석
    print(f"\n📋 블록별 평균 질문 수:")
    print("-" * 60)
    
    block_question_stats = {}
    for block_name, question_count in block_name_with_questions:
        if block_name not in block_question_stats:
            block_question_stats[block_name] = []
        block_question_stats[block_name].append(question_count)
    
    for block_name in sorted(block_question_stats.keys()):
        questions = block_question_stats[block_name]
        avg_questions = sum(questions) / len(questions)
        min_questions = min(questions)
        max_questions = max(questions)
        print(f"{block_name:<50} 평균: {avg_questions:4.1f} (범위: {min_questions}-{max_questions})")
    
    # 카테고리별 분류
    print(f"\n📂 카테고리별 블록 분류:")
    print("-" * 60)
    
    categories = {
        "인구통계": ["Demographics"],
        "성격": ["Personality"],
        "인지능력": ["Cognitive tests"],
        "경제적 선호도": ["Economic preferences", "Economic preferences - intro"],
        "제품 선호도": ["Product Preferences"],
        "심리학 실험": [
            "False consensus", "Base-rate", "Disease-loss", "Linda-conjunction",
            "Outcome bias", "Anchoring", "Less is More", "Proportion dominance",
            "Sunk cost", "Absolute vs. relative", "WTA/WTP", "Allais",
            "Myside", "Probability matching", "Non-experimental heuristics"
        ],
        "기타": ["Forward Flow"]
    }
    
    for category, keywords in categories.items():
        matching_blocks = []
        for block_name in unique_blocks.keys():
            for keyword in keywords:
                if keyword.lower() in block_name.lower():
                    matching_blocks.append(block_name)
                    break
        
        if matching_blocks:
            print(f"\n🔹 {category}:")
            for block in matching_blocks:
                count = unique_blocks[block]
                print(f"  - {block} ({count}회)")
    
    print(f"\n✅ 모든 블록 이름 출력 완료!")

if __name__ == "__main__":
    show_all_block_names()
