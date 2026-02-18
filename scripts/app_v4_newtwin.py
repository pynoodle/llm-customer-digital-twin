"""
디지털 트윈 서베이 시스템 - Streamlit GUI
newTwin 폴더 구조를 참고한 새로운 GUI
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from digital_twin_survey_system import (
    SimulationConfig,
    PersonaDataLoader,
    QuestionTemplate,
    DigitalTwinSimulator,
    ResultAnalyzer
)

# 페이지 설정
st.set_page_config(
    page_title="🤖 디지털 트윈 서베이 시스템",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 커스텀 CSS
st.markdown("""
<style>
    /* 사이드바 숨기기 */
    .css-1d391kg {display: none;}
    
    /* 메인 컨텐츠 영역 확장 */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        padding: 2rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    .stButton>button {
        width: 100%;
        background-color: #667eea;
        color: white;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: bold;
    }
    
    .stButton>button:hover {
        background-color: #764ba2;
    }
    
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
    }
    
    /* 탭 스타일 개선 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
        background-color: #f0f2f6;
        border-radius: 8px 8px 0 0;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #667eea;
        color: white;
    }
</style>
""", unsafe_allow_html=True)


# 세션 상태 초기화
def init_session_state():
    """세션 상태 초기화"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False
        st.session_state.loader = None
        st.session_state.simulator = None
        st.session_state.sample_personas = []
        st.session_state.survey_results = []
        st.session_state.interview_results = []
        st.session_state.experiment_results = []


def initialize_system(api_key, model, temperature):
    """시스템 초기화"""
    try:
        config = SimulationConfig(
            api_key=api_key,
            model=model,
            temperature=temperature,
            max_tokens=2000
        )
        
        loader = PersonaDataLoader(config)
        loader.load_dataset()
        
        simulator = DigitalTwinSimulator(config)
        
        st.session_state.loader = loader
        st.session_state.simulator = simulator
        st.session_state.initialized = True
        
        return True, "✅ 시스템이 성공적으로 초기화되었습니다!"
    except Exception as e:
        return False, f"❌ 초기화 실패: {str(e)}"


def main():
    """메인 애플리케이션"""
    init_session_state()
    
    # 헤더
    st.markdown('<h1 class="main-header">🤖 디지털 트윈 서베이 시스템</h1>', unsafe_allow_html=True)
    st.markdown("---")
    
    # 사이드바 - 설정
    with st.sidebar:
        st.header("⚙️ 시스템 설정")
        
        # API 키 입력
        api_key = st.text_input(
            "API Key",
            type="password",
            value=os.getenv("OPENAI_API_KEY", ""),
            help="OpenAI API 키를 입력하세요"
        )
        
        # 모델 선택
        model = st.selectbox(
            "모델 선택",
            ["gpt-4o-mini", "gpt-4o", "gpt-4-turbo"],
            help="사용할 OpenAI 모델을 선택하세요"
        )
        
        # Temperature 설정
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.7,
            step=0.1,
            help="응답의 창의성 조절 (높을수록 더 창의적)"
        )
        
        st.markdown("---")
        
        # 초기화 버튼
        if st.button("🚀 시스템 초기화", type="primary"):
            if not api_key:
                st.error("API 키를 입력해주세요!")
            else:
                with st.spinner("시스템 초기화 중..."):
                    success, message = initialize_system(api_key, model, temperature)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
        
        st.markdown("---")
        
        # 시스템 상태
        if st.session_state.initialized:
            st.success("✅ 시스템 준비 완료")
            dataset_size = len(st.session_state.loader.dataset['data'])
            st.metric("데이터셋 크기", f"{dataset_size:,}명")
        else:
            st.warning("⚠️ 시스템을 초기화해주세요")
    
    # 메인 화면
    if not st.session_state.initialized:
        st.info("👈 왼쪽 사이드바에서 API 키를 입력하고 시스템을 초기화해주세요.")
        
        # 사용 가이드
        st.markdown("### 📚 사용 가이드")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 1️⃣ 준비")
            st.markdown("""
            - OpenAI API 키 준비
            - 사이드바에서 설정
            - 시스템 초기화 버튼 클릭
            """)
        
        with col2:
            st.markdown("#### 2️⃣ 실행")
            st.markdown("""
            - 페르소나 선택
            - 서베이/인터뷰/실험 선택
            - 실행 버튼 클릭
            """)
        
        with col3:
            st.markdown("#### 3️⃣ 분석")
            st.markdown("""
            - 결과 확인
            - 데이터 다운로드
            - 추가 분석 수행
            """)
        
        return
    
    # 탭 생성
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "👥 페르소나 선택",
        "📋 서베이",
        "🎤 인터뷰",
        "🧪 실험",
        "📊 결과 분석"
    ])
    
    # ==================== 탭 1: 페르소나 선택 ====================
    with tab1:
        st.header("👥 페르소나 선택")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("페르소나 샘플링")
            
            sampling_method = st.radio(
                "샘플링 방법",
                ["랜덤 샘플링", "조건별 필터링"],
                horizontal=True
            )
            
            if sampling_method == "랜덤 샘플링":
                num_personas = st.number_input(
                    "샘플 수",
                    min_value=1,
                    max_value=100,
                    value=10,
                    step=1
                )
                
                if st.button("🎲 랜덤 샘플링 실행"):
                    with st.spinner("페르소나 샘플링 중..."):
                        st.session_state.sample_personas = st.session_state.loader.get_random_personas(n=num_personas)
                        st.success(f"✅ {len(st.session_state.sample_personas)}명의 페르소나를 샘플링했습니다!")
            
            else:
                st.markdown("**필터 조건 설정**")
                
                # 여기서는 간단한 예시만 제공
                # 실제 데이터셋 구조에 맞게 수정 필요
                st.info("💡 실제 데이터셋 구조에 맞게 필터 조건을 커스터마이징하세요")
                
                if st.button("🔍 필터링 실행"):
                    # 예시: 전체 데이터 가져오기
                    st.session_state.sample_personas = st.session_state.loader.get_random_personas(n=10)
                    st.success(f"✅ {len(st.session_state.sample_personas)}명의 페르소나를 선택했습니다!")
        
        with col2:
            st.subheader("📊 선택된 페르소나")
            if st.session_state.sample_personas:
                st.metric("총 인원", len(st.session_state.sample_personas))
                
                # 첫 번째 페르소나 미리보기
                with st.expander("첫 번째 페르소나 미리보기"):
                    persona_preview = st.session_state.sample_personas[0]
                    # 주요 필드만 표시
                    preview_data = {k: v for k, v in list(persona_preview.items())[:5]}
                    st.json(preview_data)
            else:
                st.info("페르소나를 선택해주세요")
    
    # ==================== 탭 2: 서베이 ====================
    with tab2:
        st.header("📋 서베이 시뮬레이션")
        
        if not st.session_state.sample_personas:
            st.warning("⚠️ 먼저 '페르소나 선택' 탭에서 페르소나를 선택해주세요!")
            return
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.subheader("서베이 설정")
            
            # 서베이 타입 선택
            survey_type = st.selectbox(
                "서베이 카테고리",
                list(QuestionTemplate.SURVEY_QUESTIONS.keys())
            )
            
            # 선택된 카테고리의 질문 표시
            questions = QuestionTemplate.get_questions_by_category(survey_type)
            st.markdown("**질문 미리보기:**")
            for i, q in enumerate(questions, 1):
                st.markdown(f"{i}. {q}")
            
            # 커스텀 질문 옵션
            use_custom = st.checkbox("커스텀 질문 사용")
            if use_custom:
                custom_questions_text = st.text_area(
                    "질문 입력 (한 줄에 하나씩)",
                    height=150,
                    placeholder="질문1\n질문2\n질문3"
                )
                if custom_questions_text:
                    questions = [q.strip() for q in custom_questions_text.split('\n') if q.strip()]
            
            # 컨텍스트 입력
            survey_context = st.text_area(
                "서베이 컨텍스트",
                value="신규 서비스에 대한 사용자 피드백 조사",
                help="서베이의 배경이나 목적을 설명하세요"
            )
        
        with col2:
            st.subheader("실행 설정")
            
            # 응답자 수 선택
            max_respondents = len(st.session_state.sample_personas)
            num_respondents = st.slider(
                "응답자 수",
                min_value=1,
                max_value=min(max_respondents, 20),
                value=min(5, max_respondents)
            )
            
            st.info(f"📊 총 {num_respondents}명이 {len(questions)}개 질문에 답변합니다")
            
            # 실행 버튼
            if st.button("▶️ 서베이 실행", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                results = []
                for i, persona in enumerate(st.session_state.sample_personas[:num_respondents]):
                    status_text.text(f"진행 중... {i+1}/{num_respondents}")
                    
                    result = st.session_state.simulator.conduct_survey(
                        persona,
                        questions,
                        survey_context=survey_context
                    )
                    results.append(result)
                    
                    progress_bar.progress((i + 1) / num_respondents)
                
                st.session_state.survey_results = results
                status_text.empty()
                progress_bar.empty()
                st.success(f"✅ 서베이 완료! {len(results)}개의 응답을 수집했습니다.")
        
        # 결과 미리보기
        if st.session_state.survey_results:
            st.markdown("---")
            st.subheader("📄 최근 결과 미리보기")
            
            latest_result = st.session_state.survey_results[-1]
            for i, response in enumerate(latest_result['responses'][:3], 1):  # 처음 3개만
                with st.expander(f"Q{i}: {response['question']}"):
                    st.write(response.get('response', 'N/A'))
    
    # ==================== 탭 3: 인터뷰 ====================
    with tab3:
        st.header("🎤 인터뷰 시뮬레이션")
        
        if not st.session_state.sample_personas:
            st.warning("⚠️ 먼저 '페르소나 선택' 탭에서 페르소나를 선택해주세요!")
            return
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.subheader("인터뷰 설정")
            
            # 인터뷰 가이드 선택
            interview_guide_name = st.selectbox(
                "인터뷰 가이드",
                list(QuestionTemplate.INTERVIEW_GUIDES.keys())
            )
            
            interview_guide = QuestionTemplate.INTERVIEW_GUIDES[interview_guide_name]
            
            # 가이드 미리보기
            with st.expander("📋 인터뷰 가이드 미리보기"):
                st.markdown(f"**Opening:** {interview_guide['opening']}")
                st.markdown("**Main Questions:**")
                for i, q in enumerate(interview_guide['main_questions'], 1):
                    st.markdown(f"{i}. {q}")
        
        with col2:
            st.subheader("실행 설정")
            
            max_interviewees = len(st.session_state.sample_personas)
            num_interviewees = st.slider(
                "인터뷰 대상자 수",
                min_value=1,
                max_value=min(max_interviewees, 10),
                value=min(2, max_interviewees)
            )
            
            st.info(f"🎤 {num_interviewees}명과 심층 인터뷰를 진행합니다")
            
            # 실행 버튼
            if st.button("▶️ 인터뷰 실행", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                results = []
                for i, persona in enumerate(st.session_state.sample_personas[:num_interviewees]):
                    status_text.text(f"인터뷰 진행 중... {i+1}/{num_interviewees}")
                    
                    result = st.session_state.simulator.conduct_interview(
                        persona,
                        interview_guide
                    )
                    results.append(result)
                    
                    progress_bar.progress((i + 1) / num_interviewees)
                
                st.session_state.interview_results = results
                status_text.empty()
                progress_bar.empty()
                st.success(f"✅ 인터뷰 완료! {len(results)}개의 인터뷰를 수행했습니다.")
        
        # 결과 미리보기
        if st.session_state.interview_results:
            st.markdown("---")
            st.subheader("💬 최근 인터뷰 내용")
            
            latest_interview = st.session_state.interview_results[-1]
            for turn in latest_interview['conversation'][:4]:  # 처음 4개만
                with st.expander(f"[{turn['type']}] {turn['interviewer'][:50]}..."):
                    if 'respondent' in turn:
                        st.write(turn['respondent'])
    
    # ==================== 탭 4: 실험 ====================
    with tab4:
        st.header("🧪 행동 실험")
        
        if not st.session_state.sample_personas:
            st.warning("⚠️ 먼저 '페르소나 선택' 탭에서 페르소나를 선택해주세요!")
            return
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.subheader("실험 설정")
            
            # 실험 선택
            experiment_name = st.selectbox(
                "실험 유형",
                list(QuestionTemplate.BEHAVIORAL_EXPERIMENTS.keys())
            )
            
            experiment = QuestionTemplate.BEHAVIORAL_EXPERIMENTS[experiment_name]
            
            # 실험 내용 표시
            st.markdown("**실험 시나리오:**")
            st.info(experiment['scenario'])
            
            st.markdown("**조건:**")
            for i, condition in enumerate(experiment['conditions'], 1):
                st.markdown(f"{i}. {condition}")
            
            st.markdown(f"**질문:** {experiment['question']}")
        
        with col2:
            st.subheader("실행 설정")
            
            max_participants = len(st.session_state.sample_personas)
            num_participants = st.slider(
                "참가자 수",
                min_value=1,
                max_value=min(max_participants, 20),
                value=min(10, max_participants)
            )
            
            st.info(f"🧪 {num_participants}명이 실험에 참여합니다")
            
            # 실행 버튼
            if st.button("▶️ 실험 실행", type="primary"):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                results = []
                for i, persona in enumerate(st.session_state.sample_personas[:num_participants]):
                    status_text.text(f"실험 진행 중... {i+1}/{num_participants}")
                    
                    result = st.session_state.simulator.run_experiment(
                        persona,
                        experiment
                    )
                    results.append(result)
                    
                    progress_bar.progress((i + 1) / num_participants)
                
                st.session_state.experiment_results = results
                status_text.empty()
                progress_bar.empty()
                st.success(f"✅ 실험 완료! {len(results)}개의 결과를 수집했습니다.")
        
        # 결과 요약
        if st.session_state.experiment_results:
            st.markdown("---")
            st.subheader("📊 실험 결과 요약")
            
            # 조건별 분포
            conditions_count = {}
            for result in st.session_state.experiment_results:
                condition_str = str(result['condition'])
                conditions_count[condition_str] = conditions_count.get(condition_str, 0) + 1
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**조건별 분포:**")
                for condition, count in conditions_count.items():
                    st.metric(condition, f"{count}명")
            
            with col2:
                # 최근 응답 미리보기
                st.markdown("**최근 응답 샘플:**")
                latest = st.session_state.experiment_results[-1]
                with st.expander("응답 보기"):
                    st.write(latest['response'][:300] + "...")
    
    # ==================== 탭 5: 결과 분석 ====================
    with tab5:
        st.header("📊 결과 분석")
        
        analyzer = ResultAnalyzer()
        
        # 서베이 결과 분석
        if st.session_state.survey_results:
            st.subheader("📋 서베이 결과")
            
            survey_df = analyzer.aggregate_survey_results(st.session_state.survey_results)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("총 응답 수", len(survey_df))
            with col2:
                st.metric("응답자 수", survey_df['persona_id'].nunique())
            with col3:
                st.metric("질문 수", survey_df['question'].nunique())
            
            # DataFrame 표시
            st.dataframe(survey_df, use_container_width=True, height=300)
            
            # 감성 분석
            all_responses = survey_df['response'].dropna().tolist()
            if all_responses:
                sentiment = analyzer.analyze_sentiment(all_responses)
                
                st.markdown("**💭 감성 분석:**")
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("긍정", sentiment['positive'])
                with col2:
                    st.metric("부정", sentiment['negative'])
                with col3:
                    st.metric("중립", sentiment['neutral'])
                with col4:
                    st.metric("총", sentiment['total'])
            
            # 다운로드 버튼
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                csv = survey_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 CSV 다운로드",
                    data=csv,
                    file_name=f"survey_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            with col2:
                json_data = json.dumps(st.session_state.survey_results, ensure_ascii=False, indent=2)
                st.download_button(
                    label="📥 JSON 다운로드",
                    data=json_data,
                    file_name=f"survey_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
        
        # 인터뷰 결과
        if st.session_state.interview_results:
            st.markdown("---")
            st.subheader("🎤 인터뷰 결과")
            
            st.metric("인터뷰 수", len(st.session_state.interview_results))
            
            # 다운로드
            json_data = json.dumps(st.session_state.interview_results, ensure_ascii=False, indent=2)
            st.download_button(
                label="📥 인터뷰 결과 다운로드 (JSON)",
                data=json_data,
                file_name=f"interview_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        # 실험 결과
        if st.session_state.experiment_results:
            st.markdown("---")
            st.subheader("🧪 실험 결과")
            
            st.metric("실험 참가자 수", len(st.session_state.experiment_results))
            
            # 다운로드
            json_data = json.dumps(st.session_state.experiment_results, ensure_ascii=False, indent=2)
            st.download_button(
                label="📥 실험 결과 다운로드 (JSON)",
                data=json_data,
                file_name=f"experiment_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json"
            )
        
        if not (st.session_state.survey_results or st.session_state.interview_results or st.session_state.experiment_results):
            st.info("아직 수집된 결과가 없습니다. 서베이, 인터뷰 또는 실험을 먼저 실행해주세요.")


if __name__ == "__main__":
    main()
