"""
persona_json의 상세 구조 분석
"""

import pandas as pd
from datasets import load_dataset
import json

def detailed_persona_json_analysis():
    """persona_json의 상세 구조를 분석합니다."""
    print("🔍 persona_json 상세 구조 분석")
    print("="*50)
    
    # 데이터셋 로드
    dataset = load_dataset("LLM-Digital-Twin/Twin-2K-500", "full_persona")
    df = dataset['data'].to_pandas()
    
    # 첫 번째 레코드의 persona_json 분석
    sample_persona_json = df.iloc[0]['persona_json']
    parsed_data = json.loads(sample_persona_json)
    
    print(f"📊 첫 번째 레코드 분석:")
    print(f"  - 원본 타입: {type(sample_persona_json)}")
    print(f"  - 원본 길이: {len(sample_persona_json):,} 문자")
    print(f"  - 파싱된 타입: {type(parsed_data)}")
    print(f"  - 파싱된 길이: {len(parsed_data)}개 요소")
    
    print(f"\n📋 구조 분석:")
    if isinstance(parsed_data, list):
        print(f"  - 리스트 구조: {len(parsed_data)}개 블록")
        
        # 각 블록 분석
        for i, block in enumerate(parsed_data[:3]):  # 처음 3개 블록만
            print(f"\n  📦 블록 {i+1}:")
            print(f"    - 타입: {type(block)}")
            if isinstance(block, dict):
                print(f"    - 키: {list(block.keys())}")
                for key, value in block.items():
                    if key == 'Questions' and isinstance(value, list):
                        print(f"    - {key}: {len(value)}개 질문")
                        if len(value) > 0:
                            first_question = str(value[0])
                            print(f"      첫 번째 질문: {first_question[:100]}...")
                    else:
                        value_preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                        print(f"    - {key}: {value_preview}")
    
    # 모든 레코드의 구조 통계
    print(f"\n📊 전체 데이터셋 구조 통계:")
    
    block_counts = []
    question_counts = []
    
    for idx, row in df.head(10).iterrows():  # 처음 10개만 분석
        try:
            parsed = json.loads(row['persona_json'])
            if isinstance(parsed, list):
                block_counts.append(len(parsed))
                
                # 각 블록의 질문 수 계산
                total_questions = 0
                for block in parsed:
                    if isinstance(block, dict) and 'Questions' in block:
                        if isinstance(block['Questions'], list):
                            total_questions += len(block['Questions'])
                question_counts.append(total_questions)
        except:
            pass
    
    if block_counts:
        print(f"  - 평균 블록 수: {sum(block_counts)/len(block_counts):.1f}")
        print(f"  - 블록 수 범위: {min(block_counts)} ~ {max(block_counts)}")
    
    if question_counts:
        print(f"  - 평균 질문 수: {sum(question_counts)/len(question_counts):.1f}")
        print(f"  - 질문 수 범위: {min(question_counts)} ~ {max(question_counts)}")
    
    # 샘플 질문 내용 분석
    print(f"\n❓ 샘플 질문 내용:")
    if isinstance(parsed_data, list) and len(parsed_data) > 0:
        first_block = parsed_data[0]
        if isinstance(first_block, dict) and 'Questions' in first_block:
            questions = first_block['Questions']
            if isinstance(questions, list) and len(questions) > 0:
                print(f"  - 첫 번째 질문: {questions[0]}")
                if len(questions) > 1:
                    print(f"  - 두 번째 질문: {questions[1]}")
    
    # 블록 타입 분석
    print(f"\n🏷️ 블록 타입 분석:")
    block_types = []
    for block in parsed_data:
        if isinstance(block, dict) and 'BlockType' in block:
            block_types.append(block['BlockType'])
    
    from collections import Counter
    type_counts = Counter(block_types)
    for block_type, count in type_counts.most_common():
        print(f"  - {block_type}: {count}개")
    
    print(f"\n✅ 상세 분석 완료!")

if __name__ == "__main__":
    detailed_persona_json_analysis()
