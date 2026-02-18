"""
Twin-2K-500 데이터셋에서 persona_json 컬럼만 추출하는 스크립트
"""

import pandas as pd
from datasets import load_dataset
import json
import os

def extract_persona_json():
    """persona_json 컬럼만 추출하여 저장"""
    print("🚀 Twin-2K-500 데이터셋에서 persona_json 추출 중...")
    
    # 1. 원본 데이터셋 로드
    print("📦 원본 데이터셋 로딩 중...")
    dataset = load_dataset("LLM-Digital-Twin/Twin-2K-500", "full_persona")
    df = dataset['data'].to_pandas()
    
    print(f"✅ 원본 데이터 로드 완료: {len(df)}개 레코드")
    print(f"📊 원본 컬럼: {list(df.columns)}")
    
    # 2. persona_json 컬럼만 추출
    print("\n🔍 persona_json 컬럼 추출 중...")
    
    # 필요한 컬럼만 선택 (id와 persona_json)
    persona_json_data = df[['pid', 'persona_json']].copy()
    
    print(f"✅ 추출 완료: {len(persona_json_data)}개 레코드")
    
    # 3. 데이터 저장
    output_dir = "processed_dataset"
    os.makedirs(output_dir, exist_ok=True)
    
    # CSV 저장
    csv_path = os.path.join(output_dir, "persona_json_only.csv")
    persona_json_data.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"\n💾 CSV 저장 완료: {csv_path}")
    
    # JSON 저장 (구조화된 형태로)
    json_path = os.path.join(output_dir, "persona_json_only.json")
    
    # 각 persona_json을 파싱하여 저장
    parsed_data = []
    parse_success = 0
    parse_fail = 0
    
    for idx, row in persona_json_data.iterrows():
        record = {
            'pid': row['pid'],
            'persona_json_raw': row['persona_json']
        }
        
        # persona_json 파싱 시도
        if row['persona_json']:
            try:
                if isinstance(row['persona_json'], str):
                    parsed_json = json.loads(row['persona_json'])
                else:
                    parsed_json = row['persona_json']
                
                record['persona_json_parsed'] = parsed_json
                parse_success += 1
            except Exception as e:
                record['parse_error'] = str(e)
                parse_fail += 1
        else:
            record['persona_json_parsed'] = None
            parse_fail += 1
        
        parsed_data.append(record)
    
    # JSON 파일로 저장
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(parsed_data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 JSON 저장 완료: {json_path}")
    print(f"📊 파싱 결과: 성공 {parse_success}개, 실패 {parse_fail}개")
    
    # 4. 샘플 데이터 출력
    print("\n👤 샘플 데이터 (첫 번째 레코드):")
    sample_record = persona_json_data.iloc[0]
    print(f"PID: {sample_record['pid']}")
    
    if sample_record['persona_json']:
        try:
            if isinstance(sample_record['persona_json'], str):
                sample_json = json.loads(sample_record['persona_json'])
            else:
                sample_json = sample_record['persona_json']
            
            print(f"Persona JSON (처음 3개 키):")
            for i, (key, value) in enumerate(sample_json.items()):
                if i >= 3:
                    print(f"  ... (총 {len(sample_json)}개 키)")
                    break
                print(f"  {key}: {str(value)[:100]}...")
        except Exception as e:
            print(f"JSON 파싱 실패: {e}")
            print(f"Raw data: {str(sample_record['persona_json'])[:200]}...")
    else:
        print("Persona JSON이 비어있습니다.")
    
    # 5. 통계 정보
    print(f"\n📈 통계 정보:")
    print(f"  - 총 레코드 수: {len(persona_json_data):,}")
    print(f"  - 비어있는 persona_json: {persona_json_data['persona_json'].isna().sum()}개")
    print(f"  - 파싱 성공률: {parse_success/(parse_success+parse_fail)*100:.1f}%")
    
    print(f"\n🎉 추출 완료!")
    print(f"📁 저장 위치: {output_dir}/")
    print(f"📄 파일들:")
    print(f"  - persona_json_only.csv (CSV 형태)")
    print(f"  - persona_json_only.json (구조화된 JSON)")
    
    return persona_json_data, parsed_data

if __name__ == "__main__":
    try:
        csv_data, json_data = extract_persona_json()
        print(f"\n✅ 성공적으로 완료되었습니다!")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
