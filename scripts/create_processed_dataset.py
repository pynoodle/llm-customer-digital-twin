"""
Twin-2K-500 데이터셋 전처리 스크립트
persona_json을 파싱하여 정리된 데이터셋을 생성합니다.
"""

import pandas as pd
import json
from datasets import load_dataset
from typing import Dict, Any
import os

def create_processed_dataset():
    """전처리된 데이터셋을 생성합니다."""
    print("🚀 Twin-2K-500 데이터셋 전처리 시작...")
    
    # 1. 원본 데이터셋 로드
    print("📦 원본 데이터셋 로딩 중...")
    dataset = load_dataset("LLM-Digital-Twin/Twin-2K-500", "full_persona")
    df = dataset['data'].to_pandas()
    
    print(f"✅ 원본 데이터 로드 완료: {len(df)}개 레코드")
    print(f"📊 원본 컬럼: {list(df.columns)}")
    
    # 2. persona_json 파싱
    print("\n🔍 persona_json 파싱 중...")
    parsed_data = []
    
    for idx, row in df.iterrows():
        record = {
            'id': row.get('pid', idx),
            'persona_text': row.get('persona_text', ''),
            'persona_summary': row.get('persona_summary', ''),
        }
        
        # persona_json 파싱
        persona_json = row.get('persona_json')
        if persona_json:
            try:
                if isinstance(persona_json, str):
                    json_data = json.loads(persona_json)
                else:
                    json_data = persona_json
                
                # 숫자 키를 question_N 형태로 변경
                for key, value in json_data.items():
                    if str(key).isdigit():
                        new_key = f"question_{key}"
                    else:
                        new_key = key
                    record[new_key] = value
                    
            except Exception as e:
                print(f"⚠️ 레코드 {idx} 파싱 실패: {e}")
        
        parsed_data.append(record)
    
    # 3. 새로운 DataFrame 생성
    print("\n📊 전처리된 DataFrame 생성 중...")
    processed_df = pd.DataFrame(parsed_data)
    
    print(f"✅ 전처리 완료: {len(processed_df)}개 레코드")
    print(f"📊 총 컬럼 수: {len(processed_df.columns)}")
    
    # 4. 컬럼 정보 출력
    print("\n📋 컬럼 정보:")
    basic_cols = ['id', 'persona_text', 'persona_summary']
    question_cols = [col for col in processed_df.columns if col.startswith('question_')]
    other_cols = [col for col in processed_df.columns if col not in basic_cols and not col.startswith('question_')]
    
    print(f"  - 기본 컬럼: {len(basic_cols)}개")
    print(f"  - 질문 컬럼: {len(question_cols)}개")
    print(f"  - 기타 컬럼: {len(other_cols)}개")
    
    if question_cols:
        print(f"  - 질문 예시: {question_cols[:5]}")
    
    # 5. 데이터 저장
    output_dir = "processed_dataset"
    os.makedirs(output_dir, exist_ok=True)
    
    # CSV 저장
    csv_path = os.path.join(output_dir, "twin2k500_processed.csv")
    processed_df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"\n💾 CSV 저장 완료: {csv_path}")
    
    # Excel 저장 (샘플 100개만)
    excel_path = os.path.join(output_dir, "twin2k500_sample.xlsx")
    sample_df = processed_df.head(100)
    sample_df.to_excel(excel_path, index=False)
    print(f"💾 Excel 샘플 저장 완료: {excel_path}")
    
    # 6. 통계 정보 생성
    stats = {
        'total_records': len(processed_df),
        'total_columns': len(processed_df.columns),
        'basic_columns': len(basic_cols),
        'question_columns': len(question_cols),
        'other_columns': len(other_cols),
        'question_columns_list': question_cols,
        'other_columns_list': other_cols
    }
    
    # 통계 JSON 저장
    stats_path = os.path.join(output_dir, "dataset_stats.json")
    with open(stats_path, 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"📊 통계 정보 저장 완료: {stats_path}")
    
    # 7. 샘플 데이터 출력
    print("\n👤 샘플 데이터 (첫 번째 레코드):")
    sample_record = processed_df.iloc[0]
    for col in ['id', 'persona_text', 'persona_summary']:
        if col in sample_record:
            value = str(sample_record[col])
            if len(value) > 100:
                value = value[:100] + "..."
            print(f"  {col}: {value}")
    
    # 질문 컬럼 샘플
    question_samples = [col for col in question_cols[:3] if col in sample_record]
    if question_samples:
        print(f"\n❓ 질문 응답 샘플:")
        for col in question_samples:
            value = str(sample_record[col])
            if len(value) > 50:
                value = value[:50] + "..."
            print(f"  {col}: {value}")
    
    print(f"\n🎉 전처리 완료!")
    print(f"📁 저장 위치: {output_dir}/")
    print(f"📄 메인 파일: twin2k500_processed.csv")
    
    return processed_df, stats

if __name__ == "__main__":
    try:
        processed_df, stats = create_processed_dataset()
        print(f"\n✅ 성공적으로 완료되었습니다!")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
