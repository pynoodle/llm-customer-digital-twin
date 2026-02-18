"""
전처리된 데이터셋 내용 확인
"""

import pandas as pd
import json

def check_processed_dataset():
    """전처리된 데이터셋 내용을 확인합니다."""
    print("📊 전처리된 데이터셋 내용 확인")
    print("="*50)
    
    # CSV 파일 로드
    df = pd.read_csv('processed_dataset/twin2k500_processed.csv', encoding='utf-8-sig')
    
    print(f"📈 데이터셋 기본 정보:")
    print(f"  - 총 레코드 수: {len(df):,}개")
    print(f"  - 총 컬럼 수: {len(df.columns)}개")
    print(f"  - 메모리 사용량: {df.memory_usage(deep=True).sum() / 1024**2:.1f} MB")
    
    print(f"\n📋 컬럼 목록:")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i:2d}. {col}")
    
    print(f"\n👤 샘플 데이터 (첫 번째 레코드):")
    sample = df.iloc[0]
    for col in df.columns:
        value = str(sample[col])
        if len(value) > 100:
            value = value[:100] + "..."
        print(f"  {col}: {value}")
    
    print(f"\n📊 데이터 타입:")
    print(df.dtypes)
    
    print(f"\n🔍 결측값 정보:")
    missing = df.isnull().sum()
    for col, count in missing.items():
        if count > 0:
            print(f"  {col}: {count}개 ({count/len(df)*100:.1f}%)")
    
    # 통계 정보 로드
    try:
        with open('processed_dataset/dataset_stats.json', 'r', encoding='utf-8') as f:
            stats = json.load(f)
        
        print(f"\n📈 통계 정보:")
        print(f"  - 기본 컬럼: {stats.get('basic_columns', 0)}개")
        print(f"  - 질문 컬럼: {stats.get('question_columns', 0)}개")
        print(f"  - 기타 컬럼: {stats.get('other_columns', 0)}개")
        
        if stats.get('question_columns_list'):
            print(f"  - 질문 컬럼 예시: {stats['question_columns_list'][:5]}")
        
    except FileNotFoundError:
        print("통계 파일을 찾을 수 없습니다.")
    
    print(f"\n✅ 데이터셋 확인 완료!")

if __name__ == "__main__":
    check_processed_dataset()
