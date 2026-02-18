"""
persona_json의 블록 이름들 분석
"""

import pandas as pd
from datasets import load_dataset
import json
from collections import Counter

def analyze_block_names():
    """persona_json의 블록 이름들을 분석합니다."""
    print("🏷️ persona_json 블록 이름 분석")
    print("="*50)
    
    # 데이터셋 로드
    dataset = load_dataset("LLM-Digital-Twin/Twin-2K-500", "full_persona")
    df = dataset['data'].to_pandas()
    
    # 첫 번째 레코드의 블록 이름들 추출
    sample_persona_json = df.iloc[0]['persona_json']
    parsed_data = json.loads(sample_persona_json)
    
    print(f"📋 첫 번째 레코드의 블록 구조:")
    print(f"  - 총 블록 수: {len(parsed_data)}")
    print(f"\n📦 블록 목록:")
    
    for i, block in enumerate(parsed_data, 1):
        if isinstance(block, dict) and 'BlockName' in block:
            block_name = block['BlockName']
            question_count = len(block.get('Questions', []))
            print(f"  {i:2d}. {block_name} ({question_count}개 질문)")
    
    # 모든 레코드의 블록 이름 통계 (처음 100개만)
    print(f"\n📊 블록 이름 통계 (처음 100개 레코드):")
    
    all_block_names = []
    for idx, row in df.head(100).iterrows():
        try:
            parsed = json.loads(row['persona_json'])
            if isinstance(parsed, list):
                for block in parsed:
                    if isinstance(block, dict) and 'BlockName' in block:
                        all_block_names.append(block['BlockName'])
        except:
            pass
    
    block_name_counts = Counter(all_block_names)
    
    print(f"  - 총 고유 블록 이름: {len(block_name_counts)}")
    print(f"  - 가장 자주 나타나는 블록:")
    
    for block_name, count in block_name_counts.most_common(10):
        percentage = count / len(df.head(100)) * 100
        print(f"    {block_name}: {count}회 ({percentage:.1f}%)")
    
    # 질문 타입 분석
    print(f"\n❓ 질문 타입 분석:")
    question_types = []
    
    for block in parsed_data:
        if isinstance(block, dict) and 'Questions' in block:
            questions = block['Questions']
            if isinstance(questions, list):
                for question in questions:
                    if isinstance(question, dict) and 'QuestionType' in question:
                        question_types.append(question['QuestionType'])
    
    type_counts = Counter(question_types)
    for qtype, count in type_counts.most_common():
        print(f"  - {qtype}: {count}개")
    
    # 샘플 질문의 구조
    print(f"\n📋 샘플 질문 구조:")
    if len(parsed_data) > 0 and 'Questions' in parsed_data[0]:
        sample_question = parsed_data[0]['Questions'][0]
        print(f"  - 질문 키: {list(sample_question.keys())}")
        for key, value in sample_question.items():
            if key == 'Options' and isinstance(value, list):
                print(f"  - {key}: {len(value)}개 옵션")
            elif key == 'Answers':
                print(f"  - {key}: {value}")
            else:
                value_preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                print(f"  - {key}: {value_preview}")
    
    print(f"\n✅ 블록 분석 완료!")

if __name__ == "__main__":
    analyze_block_names()
