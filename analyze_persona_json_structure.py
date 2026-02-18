"""
Twin-2K-500 데이터셋의 persona_json 컬럼 구조 분석
"""

import pandas as pd
from datasets import load_dataset
import json
from collections import Counter
import numpy as np

def analyze_persona_json_structure():
    """persona_json 컬럼의 데이터 구조를 분석합니다."""
    print("🔍 Twin-2K-500 데이터셋 persona_json 구조 분석")
    print("="*60)
    
    # 1. 데이터셋 로드
    print("📦 데이터셋 로딩 중...")
    dataset = load_dataset("LLM-Digital-Twin/Twin-2K-500", "full_persona")
    df = dataset['data'].to_pandas()
    
    print(f"✅ 데이터 로드 완료: {len(df)}개 레코드")
    
    # 2. persona_json 컬럼 기본 정보
    print(f"\n📊 persona_json 컬럼 기본 정보:")
    print(f"  - 총 레코드 수: {len(df):,}")
    print(f"  - 비어있는 값: {df['persona_json'].isna().sum()}개")
    print(f"  - 비어있지 않은 값: {df['persona_json'].notna().sum()}개")
    
    # 3. 데이터 타입 분석
    print(f"\n🔍 데이터 타입 분석:")
    persona_json_types = df['persona_json'].apply(lambda x: type(x).__name__ if pd.notna(x) else 'NaN').value_counts()
    for dtype, count in persona_json_types.items():
        print(f"  - {dtype}: {count}개 ({count/len(df)*100:.1f}%)")
    
    # 4. 샘플 데이터 구조 분석
    print(f"\n📋 샘플 데이터 구조 분석:")
    
    # 비어있지 않은 데이터만 분석
    valid_data = df[df['persona_json'].notna()]
    print(f"  - 분석 대상: {len(valid_data)}개 레코드")
    
    if len(valid_data) > 0:
        # 첫 번째 샘플 분석
        sample = valid_data.iloc[0]['persona_json']
        print(f"\n👤 첫 번째 샘플 분석:")
        print(f"  - 데이터 타입: {type(sample)}")
        
        if isinstance(sample, str):
            print(f"  - 문자열 길이: {len(sample)}")
            try:
                parsed = json.loads(sample)
                print(f"  - JSON 파싱 성공")
                print(f"  - 파싱된 타입: {type(parsed)}")
                if isinstance(parsed, dict):
                    print(f"  - 딕셔너리 키 수: {len(parsed)}")
                    print(f"  - 키 예시: {list(parsed.keys())[:5]}")
            except:
                print(f"  - JSON 파싱 실패")
        elif isinstance(sample, dict):
            print(f"  - 딕셔너리 키 수: {len(sample)}")
            print(f"  - 키 예시: {list(sample.keys())[:5]}")
        elif isinstance(sample, list):
            print(f"  - 리스트 길이: {len(sample)}")
            if len(sample) > 0:
                print(f"  - 첫 번째 요소 타입: {type(sample[0])}")
    
    # 5. 모든 persona_json 파싱 시도
    print(f"\n🔄 전체 데이터 파싱 분석:")
    
    parse_results = {
        'success': 0,
        'failed': 0,
        'empty': 0,
        'parsed_data': []
    }
    
    key_frequency = Counter()
    value_types = Counter()
    
    for idx, row in valid_data.iterrows():
        persona_json = row['persona_json']
        
        if pd.isna(persona_json) or persona_json == '':
            parse_results['empty'] += 1
            continue
        
        try:
            # JSON 파싱 시도
            if isinstance(persona_json, str):
                parsed = json.loads(persona_json)
            else:
                parsed = persona_json
            
            parse_results['success'] += 1
            parse_results['parsed_data'].append(parsed)
            
            # 키 빈도 분석
            if isinstance(parsed, dict):
                for key in parsed.keys():
                    key_frequency[key] += 1
                    value_types[type(parsed[key]).__name__] += 1
            elif isinstance(parsed, list) and len(parsed) > 0:
                if isinstance(parsed[0], dict):
                    for item in parsed:
                        for key in item.keys():
                            key_frequency[key] += 1
                            value_types[type(item[key]).__name__] += 1
            
        except Exception as e:
            parse_results['failed'] += 1
    
    print(f"  - 파싱 성공: {parse_results['success']}개")
    print(f"  - 파싱 실패: {parse_results['failed']}개")
    print(f"  - 빈 데이터: {parse_results['empty']}개")
    
    if parse_results['success'] > 0:
        success_rate = parse_results['success'] / (parse_results['success'] + parse_results['failed']) * 100
        print(f"  - 성공률: {success_rate:.1f}%")
    
    # 6. 키 구조 분석
    if key_frequency:
        print(f"\n🔑 키 구조 분석:")
        print(f"  - 총 고유 키 수: {len(key_frequency)}")
        print(f"  - 가장 자주 나타나는 키 (Top 10):")
        
        for key, count in key_frequency.most_common(10):
            percentage = count / parse_results['success'] * 100
            print(f"    {key}: {count}회 ({percentage:.1f}%)")
    
    # 7. 값 타입 분석
    if value_types:
        print(f"\n📊 값 타입 분석:")
        for vtype, count in value_types.most_common():
            percentage = count / sum(value_types.values()) * 100
            print(f"  - {vtype}: {count}개 ({percentage:.1f}%)")
    
    # 8. 샘플 파싱된 데이터 구조
    if parse_results['parsed_data']:
        print(f"\n📋 파싱된 데이터 샘플 구조:")
        sample_parsed = parse_results['parsed_data'][0]
        
        if isinstance(sample_parsed, dict):
            print(f"  - 딕셔너리 구조:")
            for key, value in list(sample_parsed.items())[:5]:
                value_preview = str(value)[:50] + "..." if len(str(value)) > 50 else str(value)
                print(f"    {key}: {value_preview} (타입: {type(value).__name__})")
            
            if len(sample_parsed) > 5:
                print(f"    ... (총 {len(sample_parsed)}개 키)")
        
        elif isinstance(sample_parsed, list):
            print(f"  - 리스트 구조 (길이: {len(sample_parsed)})")
            if len(sample_parsed) > 0:
                print(f"  - 첫 번째 요소: {type(sample_parsed[0])}")
                if isinstance(sample_parsed[0], dict):
                    print(f"  - 첫 번째 요소 키: {list(sample_parsed[0].keys())[:5]}")
    
    # 9. 숫자 키 분석
    if key_frequency:
        numeric_keys = [k for k in key_frequency.keys() if str(k).isdigit()]
        if numeric_keys:
            print(f"\n🔢 숫자 키 분석:")
            print(f"  - 숫자 키 수: {len(numeric_keys)}")
            print(f"  - 숫자 키 범위: {min(numeric_keys)} ~ {max(numeric_keys)}")
            print(f"  - 숫자 키 예시: {sorted(numeric_keys)[:10]}")
    
    print(f"\n✅ 분석 완료!")
    
    return {
        'total_records': len(df),
        'valid_records': len(valid_data),
        'parse_results': parse_results,
        'key_frequency': dict(key_frequency),
        'value_types': dict(value_types)
    }

if __name__ == "__main__":
    try:
        results = analyze_persona_json_structure()
        print(f"\n📊 최종 요약:")
        print(f"  - 총 레코드: {results['total_records']:,}")
        print(f"  - 유효 레코드: {results['valid_records']:,}")
        print(f"  - 파싱 성공: {results['parse_results']['success']:,}")
        print(f"  - 고유 키 수: {len(results['key_frequency'])}")
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
