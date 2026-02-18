"""
persona_json 데이터를 블록별 피쳐로 변환하여 설문대상 선정용 데이터셋 생성
"""

import pandas as pd
from datasets import load_dataset
import json
from collections import Counter
import numpy as np

def create_block_based_dataset():
    """persona_json을 블록별 피쳐로 변환한 데이터셋을 생성합니다."""
    print("🚀 블록 기반 설문대상 선정용 데이터셋 생성")
    print("="*60)
    
    # 1. 원본 데이터셋 로드
    print("📦 원본 데이터셋 로딩 중...")
    dataset = load_dataset("LLM-Digital-Twin/Twin-2K-500", "full_persona")
    df = dataset['data'].to_pandas()
    
    print(f"✅ 원본 데이터 로드 완료: {len(df)}개 레코드")
    
    # 2. 모든 블록 이름 수집
    print("\n🔍 모든 블록 이름 수집 중...")
    all_block_names = set()
    
    for idx, row in df.iterrows():
        try:
            parsed = json.loads(row['persona_json'])
            if isinstance(parsed, list):
                for block in parsed:
                    if isinstance(block, dict) and 'BlockName' in block:
                        all_block_names.add(block['BlockName'])
        except:
            pass
    
    print(f"✅ 총 {len(all_block_names)}개의 고유 블록 발견")
    
    # 3. 블록별 피쳐 데이터 생성
    print("\n📊 블록별 피쳐 데이터 생성 중...")
    
    # 기본 정보 컬럼
    feature_columns = ['pid', 'persona_text', 'persona_summary']
    
    # 블록 존재 여부 컬럼 (0/1)
    block_presence_columns = [f"has_{block_name.replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '').lower()}" 
                             for block_name in sorted(all_block_names)]
    
    # 블록별 질문 수 컬럼
    block_question_count_columns = [f"questions_{block_name.replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '').lower()}" 
                                  for block_name in sorted(all_block_names)]
    
    # 모든 컬럼 결합
    all_columns = feature_columns + block_presence_columns + block_question_count_columns
    
    # 새로운 데이터프레임 생성
    new_data = []
    
    for idx, row in df.iterrows():
        record = {
            'pid': row.get('pid', idx),
            'persona_text': row.get('persona_text', ''),
            'persona_summary': row.get('persona_summary', '')
        }
        
        # 블록 정보 초기화
        block_info = {block_name: {'present': 0, 'question_count': 0} 
                     for block_name in sorted(all_block_names)}
        
        try:
            parsed = json.loads(row['persona_json'])
            if isinstance(parsed, list):
                for block in parsed:
                    if isinstance(block, dict) and 'BlockName' in block:
                        block_name = block['BlockName']
                        if block_name in block_info:
                            block_info[block_name]['present'] = 1
                            block_info[block_name]['question_count'] = len(block.get('Questions', []))
        except:
            pass
        
        # 블록 정보를 레코드에 추가
        for block_name in sorted(all_block_names):
            safe_name = block_name.replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '').lower()
            record[f"has_{safe_name}"] = block_info[block_name]['present']
            record[f"questions_{safe_name}"] = block_info[block_name]['question_count']
        
        new_data.append(record)
    
    # 4. 새로운 데이터프레임 생성
    print("\n📋 새로운 데이터프레임 생성 중...")
    new_df = pd.DataFrame(new_data)
    
    print(f"✅ 새로운 데이터셋 생성 완료:")
    print(f"  - 레코드 수: {len(new_df):,}")
    print(f"  - 컬럼 수: {len(new_df.columns)}")
    print(f"  - 블록 피쳐 수: {len(block_presence_columns)}")
    
    # 5. 데이터 저장
    output_dir = "processed_dataset"
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # CSV 저장
    csv_path = os.path.join(output_dir, "block_based_dataset.csv")
    new_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"\n💾 CSV 저장 완료: {csv_path}")
    
    # 6. 통계 정보 생성
    print("\n📊 데이터셋 통계:")
    
    # 블록별 존재 비율
    print(f"\n🏷️ 블록별 존재 비율 (상위 20개):")
    block_stats = []
    for col in block_presence_columns:
        block_name = col.replace('has_', '').replace('_', ' ').title()
        presence_rate = new_df[col].mean() * 100
        block_stats.append((block_name, presence_rate, new_df[col].sum()))
    
    block_stats.sort(key=lambda x: x[1], reverse=True)
    
    for i, (block_name, rate, count) in enumerate(block_stats[:20], 1):
        print(f"  {i:2d}. {block_name:<40} {rate:5.1f}% ({count:,}명)")
    
    # 7. 샘플 데이터 출력
    print(f"\n👤 샘플 데이터 (첫 번째 레코드):")
    sample_record = new_df.iloc[0]
    
    print(f"  - PID: {sample_record['pid']}")
    print(f"  - Persona Text: {sample_record['persona_text'][:100]}...")
    
    # 존재하는 블록들만 표시
    present_blocks = []
    for col in block_presence_columns:
        if sample_record[col] == 1:
            block_name = col.replace('has_', '').replace('_', ' ').title()
            question_count = sample_record[f"questions_{col.replace('has_', '')}"]
            present_blocks.append((block_name, question_count))
    
    print(f"  - 존재하는 블록 수: {len(present_blocks)}")
    print(f"  - 블록 목록:")
    for block_name, q_count in present_blocks[:10]:  # 처음 10개만
        print(f"    • {block_name} ({q_count}개 질문)")
    if len(present_blocks) > 10:
        print(f"    ... 외 {len(present_blocks) - 10}개 블록")
    
    # 8. 필터링 가능한 피쳐 목록 생성
    print(f"\n🎯 설문대상 선정용 피쳐 목록:")
    
    # 카테고리별 분류
    categories = {
        "핵심_블록": [
            "Demographics", "Personality", "Cognitive_tests", 
            "Economic_preferences", "Product_Preferences_Pricing"
        ],
        "심리학_실험": [
            "False_consensus", "Base_rate_30_engineers", "Base_rate_70_engineers",
            "Disease_loss", "Disease_gain", "Linda_conjunction", "Linda_no_conjunction",
            "Outcome_bias_success", "Outcome_bias_failure", "Anchoring_african_countries_high",
            "Anchoring_african_countries_low", "Anchoring_redwood_high", "Anchoring_redwood_low",
            "Sunk_cost_yes", "Sunk_cost_no", "Absolute_vs_relative_calculator",
            "Absolute_vs_relative_jacket", "Wta_wtp_thaler_problem_wta_certainty",
            "Wta_wtp_thaler_problem_wtp_certainty", "Wta_wtp_thaler_wtp_noncertainty",
            "Allais_form_1", "Allais_form_2", "Myside_german", "Myside_ford",
            "Probability_matching_vs_maximizing_problem_1", "Probability_matching_vs_maximizing_problem_2",
            "Non_experimental_heuristics_and_biases"
        ],
        "게임_이론": [
            "Less_is_more_gamble_a", "Less_is_more_gamble_b", "Less_is_more_gamble_c",
            "Proportion_dominance_1a", "Proportion_dominance_1b", "Proportion_dominance_1c",
            "Proportion_dominance_2a", "Proportion_dominance_2b", "Proportion_dominance_2c"
        ],
        "기타": ["Forward_flow"]
    }
    
    for category, blocks in categories.items():
        print(f"\n🔹 {category}:")
        available_blocks = []
        for block in blocks:
            safe_name = block.lower().replace(' ', '_').replace('-', '_').replace('(', '').replace(')', '')
            has_col = f"has_{safe_name}"
            if has_col in new_df.columns:
                presence_rate = new_df[has_col].mean() * 100
                available_blocks.append((block, presence_rate))
        
        for block_name, rate in sorted(available_blocks, key=lambda x: x[1], reverse=True):
            print(f"  - {block_name}: {rate:.1f}%")
    
    # 9. 메타데이터 저장
    metadata = {
        'total_records': len(new_df),
        'total_columns': len(new_df.columns),
        'block_features': len(block_presence_columns),
        'question_count_features': len(block_question_count_columns),
        'unique_blocks': len(all_block_names),
        'block_list': sorted(list(all_block_names)),
        'categories': categories
    }
    
    metadata_path = os.path.join(output_dir, "block_dataset_metadata.json")
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"\n📊 메타데이터 저장 완료: {metadata_path}")
    
    print(f"\n🎉 블록 기반 데이터셋 생성 완료!")
    print(f"📁 저장 위치: {output_dir}/")
    print(f"📄 메인 파일: block_based_dataset.csv")
    print(f"📊 메타데이터: block_dataset_metadata.json")
    
    return new_df, metadata

if __name__ == "__main__":
    try:
        dataset, metadata = create_block_based_dataset()
        print(f"\n✅ 성공적으로 완료되었습니다!")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
