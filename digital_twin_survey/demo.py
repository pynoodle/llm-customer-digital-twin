"""
간단한 데모 스크립트
3명의 응답자에게 샘플 설문과 인터뷰 진행
"""

import os
from digital_twin_survey_system import DigitalTwinSurveySystem


def quick_demo():
    """빠른 데모 실행"""
    print("="*80)
    print("🚀 디지털 트윈 시스템 빠른 데모")
    print("="*80)
    print("\n이 데모는 3명의 응답자에게 샘플 설문과 인터뷰를 진행합니다.")
    print("예상 소요 시간: 약 2-3분")
    print("예상 비용: $0.05-0.10 (GPT-4o-mini 기준)\n")
    
    # API 키 확인
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️ OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
        api_key = input("OpenAI API 키를 입력하세요: ").strip()
        if not api_key:
            print("❌ API 키가 필요합니다. 프로그램을 종료합니다.")
            return
    
    # 시스템 초기화
    print("\n1️⃣ 시스템 초기화 중...")
    system = DigitalTwinSurveySystem(api_key)
    
    # 데이터셋 로드
    print("\n2️⃣ 데이터셋 로딩 중...")
    if not system.load_dataset():
        print("❌ 데이터셋 로드 실패")
        return
    
    # 3명의 응답자 선택 (처음 3명)
    print("\n3️⃣ 응답자 선택: 처음 3명")
    system.selected_personas = [0, 1, 2]
    
    # 설문조사 예시
    print("\n" + "="*80)
    print("📝 파트 1: 설문조사 (Survey)")
    print("="*80)
    
    survey_questions = [
        {
            "question": "How satisfied are you with your current job? (1=매우 불만족, 7=매우 만족)",
            "scale": "1-7",
            "type": "likert"
        },
        {
            "question": "How likely are you to recommend AI tools to colleagues? (1=전혀 추천 안함, 7=매우 추천)",
            "scale": "1-7",
            "type": "likert"
        }
    ]
    
    print("\n질문 목록:")
    for i, q in enumerate(survey_questions, 1):
        print(f"  {i}. {q['question']}")
    
    # 설문 생성 및 실시
    survey = system.create_survey(survey_questions)
    print("\n⏳ 설문조사 진행 중... (약 30초 소요)")
    survey_results = system.conduct_survey(survey)
    
    # 결과 출력
    print("\n📊 설문 결과:")
    print(survey_results[['participant_id', 'Q1', 'Q2']].to_string(index=False))
    
    # 통계 분석
    print("\n📈 통계 분석:")
    system.analyze_survey_results(survey_results)
    
    # 인터뷰 예시
    print("\n" + "="*80)
    print("🎤 파트 2: 인터뷰 (Interview)")
    print("="*80)
    
    interview_questions = [
        "What aspects of your work do you find most meaningful?",
        "How do you see AI impacting your profession in the next 5 years?"
    ]
    
    print("\n질문 목록:")
    for i, q in enumerate(interview_questions, 1):
        print(f"  {i}. {q}")
    
    # 인터뷰 생성 및 실시
    interview = system.create_interview(interview_questions)
    print("\n⏳ 인터뷰 진행 중... (약 30초 소요)")
    interview_results = system.conduct_interview(interview)
    
    # 인터뷰 결과 출력
    print("\n💬 인터뷰 결과:")
    for idx, row in interview_results.iterrows():
        print(f"\n참가자 {row['participant_id']}:")
        print(f"  Q1: {row['Q1'][:150]}...")
        print(f"  Q2: {row['Q2'][:150]}...")
    
    # 결과 저장
    print("\n" + "="*80)
    print("💾 결과 저장")
    print("="*80)
    
    system.export_results('demo_results', format='csv')
    
    print("\n✅ 데모 완료!")
    print("\n생성된 파일:")
    print("  - demo_results_survey_1.csv")
    print("  - demo_results_interview_1.csv")
    print("\n이제 digital_twin_survey_system.py를 실행하여 전체 기능을 사용해보세요!")


if __name__ == "__main__":
    quick_demo()
