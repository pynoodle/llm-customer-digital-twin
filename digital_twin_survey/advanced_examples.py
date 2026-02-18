"""
고급 예제 1: 특정 그룹 타겟팅 설문
특정 특성을 가진 응답자를 선택하여 맞춤형 설문 진행
"""

import os
import pandas as pd
from digital_twin_survey_system import DigitalTwinSurveySystem


def targeted_survey_example():
    """특정 그룹에 대한 타겟 설문"""
    
    print("="*80)
    print("🎯 타겟 그룹 설문 예제")
    print("="*80)
    print("\n이 예제는 특정 특성(예: 기술 관련 직종)을 가진 응답자를 선택하여")
    print("맞춤형 설문을 진행합니다.\n")
    
    # API 키
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        api_key = input("OpenAI API 키: ")
    
    # 시스템 초기화
    system = DigitalTwinSurveySystem(api_key)
    
    if not system.load_dataset():
        return
    
    # 1단계: 기술 관련 키워드로 필터링
    print("\n1️⃣ 기술 관련 직종 종사자 필터링...")
    tech_keywords = ["engineer", "developer", "programmer", "technology", "IT", "software"]
    
    tech_personas = []
    for idx, row in enumerate(system.dataset['data'][:200]):  # 처음 200명 중에서
        persona_text = row.get('persona_text', '').lower()
        if any(keyword.lower() in persona_text for keyword in tech_keywords):
            tech_personas.append(idx)
            if len(tech_personas) >= 20:  # 최대 20명
                break
    
    print(f"✅ {len(tech_personas)}명의 기술 관련 종사자 발견")
    system.selected_personas = tech_personas[:10]  # 10명으로 제한
    
    # 2단계: 기술 관련 맞춤 설문
    print("\n2️⃣ 기술 트렌드 관련 설문 준비...")
    
    tech_survey = system.create_survey([
        {
            "question": "How important is AI/ML knowledge in your current role? (1=전혀 중요하지 않음, 7=매우 중요)",
            "scale": "1-7",
            "type": "likert"
        },
        {
            "question": "Rate your organization's adoption of new technologies (1=매우 느림, 7=매우 빠름)",
            "scale": "1-7",
            "type": "likert"
        },
        {
            "question": "How satisfied are you with your technical tools and infrastructure? (1=매우 불만족, 7=매우 만족)",
            "scale": "1-7",
            "type": "likert"
        },
        {
            "question": "How likely are you to pursue further technical certifications? (1=전혀 계획 없음, 7=매우 확실)",
            "scale": "1-7",
            "type": "likert"
        }
    ])
    
    # 3단계: 설문 실시
    print("\n3️⃣ 설문 진행 중...")
    results = system.conduct_survey(tech_survey)
    
    # 4단계: 결과 분석
    print("\n4️⃣ 결과 분석")
    analysis = system.analyze_survey_results(results)
    
    # 5단계: 추가 인사이트
    print("\n5️⃣ 추가 인사이트")
    
    # AI/ML 중요도 평균
    ai_importance = results['Q1'].mean()
    print(f"\n💡 AI/ML 중요도 평균: {ai_importance:.2f}/7")
    
    if ai_importance > 5.5:
        print("   → 기술 직군에서 AI/ML이 매우 중요한 스킬로 인식됨")
    elif ai_importance > 4.0:
        print("   → 기술 직군에서 AI/ML이 중요한 스킬로 인식됨")
    else:
        print("   → 기술 직군에서도 AI/ML의 중요성이 상대적으로 낮음")
    
    # 기술 도입 속도
    tech_adoption = results['Q2'].mean()
    print(f"\n💡 기술 도입 속도 평균: {tech_adoption:.2f}/7")
    
    # 상관관계 분석
    correlation = results[['Q1', 'Q2', 'Q3', 'Q4']].corr()
    print("\n📊 질문 간 상관관계:")
    print(correlation.round(2))
    
    # 6단계: 후속 인터뷰
    print("\n6️⃣ 후속 인터뷰 진행")
    
    # AI 중요도가 높다고 답한 사람들만 선택
    high_ai_importance = results[results['Q1'] >= 6]['persona_index'].tolist()
    
    if high_ai_importance:
        print(f"\nAI/ML을 매우 중요하게 생각하는 {len(high_ai_importance)}명에게 추가 인터뷰...")
        
        follow_up_interview = system.create_interview([
            "What specific AI/ML skills do you think are most valuable in your field?",
            "How has AI/ML changed your workflow in the past year?"
        ])
        
        interview_results = system.conduct_interview(
            follow_up_interview, 
            high_ai_importance[:3]  # 처음 3명만
        )
        
        print("\n💬 주요 인터뷰 응답:")
        for idx, row in interview_results.iterrows():
            print(f"\n참가자 {row['participant_id']}:")
            print(f"  {row['Q1'][:200]}...")
    
    # 결과 저장
    print("\n7️⃣ 결과 저장")
    system.export_results('tech_survey', format='csv')
    
    # 추가: 엑셀로도 저장
    with pd.ExcelWriter('tech_survey_complete.xlsx') as writer:
        results.to_excel(writer, sheet_name='Survey', index=False)
        if high_ai_importance and len(interview_results) > 0:
            interview_results.to_excel(writer, sheet_name='Interview', index=False)
        
        # 통계 시트
        stats_df = pd.DataFrame(analysis['statistics']).T
        stats_df.to_excel(writer, sheet_name='Statistics')
    
    print("✅ 완료! 생성된 파일:")
    print("  - tech_survey_survey_1.csv")
    print("  - tech_survey_complete.xlsx")


def demographic_comparison_example():
    """인구통계학적 그룹 간 비교 분석"""
    
    print("\n" + "="*80)
    print("📊 그룹 간 비교 분석 예제")
    print("="*80)
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        api_key = input("OpenAI API 키: ")
    
    system = DigitalTwinSurveySystem(api_key)
    
    if not system.load_dataset():
        return
    
    # 예시: 연령대별 비교를 위한 키워드 (실제로는 데이터에서 추출해야 함)
    print("\n젊은 층 (18-35) vs 중장년층 (45+) 비교 분석\n")
    
    # 간단히 처음 10명씩 선택 (실제로는 연령 필터링 필요)
    young_group = list(range(0, 10))
    older_group = list(range(100, 110))
    
    # 공통 설문
    common_survey = system.create_survey([
        {
            "question": "How comfortable are you with using new technology? (1=매우 불편, 7=매우 편함)",
            "scale": "1-7",
            "type": "likert"
        },
        {
            "question": "How important is work-life balance to you? (1=전혀 중요하지 않음, 7=매우 중요)",
            "scale": "1-7",
            "type": "likert"
        }
    ])
    
    # 젊은 층 설문
    print("1️⃣ 젊은 층 설문 진행...")
    young_results = system.conduct_survey(common_survey, young_group)
    
    # 중장년층 설문
    print("\n2️⃣ 중장년층 설문 진행...")
    older_results = system.conduct_survey(common_survey, older_group)
    
    # 비교 분석
    print("\n3️⃣ 그룹 간 비교")
    print("\n기술 친화도 (Q1):")
    print(f"  젊은 층: {young_results['Q1'].mean():.2f}")
    print(f"  중장년층: {older_results['Q1'].mean():.2f}")
    print(f"  차이: {abs(young_results['Q1'].mean() - older_results['Q1'].mean()):.2f}")
    
    print("\n일과 삶의 균형 중요도 (Q2):")
    print(f"  젊은 층: {young_results['Q2'].mean():.2f}")
    print(f"  중장년층: {older_results['Q2'].mean():.2f}")
    print(f"  차이: {abs(young_results['Q2'].mean() - older_results['Q2'].mean()):.2f}")
    
    # 시각화를 위한 데이터 준비
    comparison_df = pd.DataFrame({
        '그룹': ['젊은층', '중장년층'],
        '기술친화도': [young_results['Q1'].mean(), older_results['Q1'].mean()],
        '워라밸중요도': [young_results['Q2'].mean(), older_results['Q2'].mean()]
    })
    
    print("\n📊 비교 요약:")
    print(comparison_df)
    
    # 결과 저장
    with pd.ExcelWriter('demographic_comparison.xlsx') as writer:
        young_results.to_excel(writer, sheet_name='Young_Group', index=False)
        older_results.to_excel(writer, sheet_name='Older_Group', index=False)
        comparison_df.to_excel(writer, sheet_name='Comparison', index=False)
    
    print("\n✅ 비교 분석 완료!")
    print("  생성 파일: demographic_comparison.xlsx")


if __name__ == "__main__":
    # 예제 1: 타겟 설문
    targeted_survey_example()
    
    # 예제 2: 그룹 비교 (선택사항)
    # run_comparison = input("\n그룹 비교 예제도 실행하시겠습니까? (y/n): ")
    # if run_comparison.lower() == 'y':
    #     demographic_comparison_example()
