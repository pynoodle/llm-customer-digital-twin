"""
디지털 트윈 설문조사 & 인터뷰 시스템
Streamlit GUI 버전
"""

import streamlit as st
import os
import pandas as pd
import json
import time
from datetime import datetime
from digital_twin_survey_system import DigitalTwinSurveySystem
import plotly.express as px

# 페이지 설정
st.set_page_config(
    page_title="디지털 트윈 연구 시스템",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .stats-box {
        background-color: #e8f5e9;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
if 'system' not in st.session_state:
    st.session_state.system = None
if 'selected_personas' not in st.session_state:
    st.session_state.selected_personas = []
if 'survey_results' not in st.session_state:
    st.session_state.survey_results = None
if 'interview_results' not in st.session_state:
    st.session_state.interview_results = None
if 'api_key' not in st.session_state:
    st.session_state.api_key = os.getenv("OPENAI_API_KEY", "")

# 헤더
st.markdown('<div class="main-header">🤖 디지털 트윈 연구 시스템</div>', unsafe_allow_html=True)

# 사이드바 - 시스템 설정
with st.sidebar:
    st.markdown("## ⚙️ 시스템 설정")
    
    # API 키 입력
    api_key = st.text_input(
        "OpenAI API 키",
        value=st.session_state.api_key,
        type="password",
        help="OpenAI API 키를 입력하세요"
    )
    
    if api_key != st.session_state.api_key:
        st.session_state.api_key = api_key
    
    if st.button("🔄 시스템 초기화", use_container_width=True):
        if not st.session_state.api_key:
            st.error("API 키를 입력해주세요!")
        else:
            with st.spinner("시스템 초기화 중..."):
                try:
                    system = DigitalTwinSurveySystem(st.session_state.api_key)
                    if system.load_dataset():
                        st.session_state.system = system
                        st.success("✅ 초기화 완료!")
                        st.rerun()
                except Exception as e:
                    st.error(f"❌ 초기화 실패: {e}")
    
    st.divider()
    
    # 시스템 상태
    if st.session_state.system:
        st.success("✅ 시스템 준비됨")
        total_personas = len(st.session_state.system.dataset['data'])
        st.metric("전체 페르소나", f"{total_personas:,}")
        st.metric("선택된 응답자", len(st.session_state.selected_personas))
    else:
        st.warning("⚠️ 시스템 미초기화")

# 메인 영역
if not st.session_state.system:
    st.info("👈 왼쪽 사이드바에서 API 키를 입력하고 시스템을 초기화하세요.")
    st.stop()

# 탭 구성
tab1, tab2, tab3, tab4 = st.tabs(["📋 응답자 선택", "📊 설문조사", "💬 인터뷰", "📈 결과 분석"])

system = st.session_state.system

# 탭 1: 응답자 선택
with tab1:
    st.markdown("## 📋 응답자 선택")
    
    selection_method = st.radio(
        "선택 방법",
        ["무작위 샘플링", "범위 선택", "인덱스 직접 입력"],
        horizontal=True
    )
    
    if selection_method == "무작위 샘플링":
        col1, col2 = st.columns(2)
        
        with col1:
            sample_size = st.number_input(
                "샘플 크기",
                min_value=1,
                max_value=100,
                value=10
            )
        
        with col2:
            seed = st.number_input("랜덤 시드", value=42)
        
        if st.button("🎲 샘플 추출", type="primary"):
            import random
            random.seed(seed)
            total = len(system.dataset['data'])
            selected = random.sample(range(total), min(sample_size, total))
            st.session_state.selected_personas = selected
            system.selected_personas = selected
            st.success(f"✅ {len(selected)}명 선택됨!")
    
    elif selection_method == "범위 선택":
        col1, col2 = st.columns(2)
        
        with col1:
            start_idx = st.number_input("시작 인덱스", min_value=0, value=0)
        
        with col2:
            end_idx = st.number_input("종료 인덱스", min_value=0, value=49)
        
        if st.button("✅ 범위 선택", type="primary"):
            selected = list(range(start_idx, end_idx + 1))
            st.session_state.selected_personas = selected
            system.selected_personas = selected
            st.success(f"✅ {len(selected)}명 선택됨!")
    
    else:  # 인덱스 직접 입력
        indices_input = st.text_area(
            "인덱스 입력 (쉼표로 구분)",
            placeholder="0, 1, 2, 3, 4",
            height=100
        )
        
        if st.button("✅ 선택", type="primary"):
            try:
                selected = [int(i.strip()) for i in indices_input.split(",")]
                st.session_state.selected_personas = selected
                system.selected_personas = selected
                st.success(f"✅ {len(selected)}명 선택됨!")
            except:
                st.error("❌ 유효한 인덱스를 입력하세요!")
    
    # 선택된 응답자 표시
    if st.session_state.selected_personas:
        st.divider()
        st.markdown(f"### 👥 선택된 응답자: {len(st.session_state.selected_personas)}명")
        
        show_preview = st.checkbox("미리보기 표시", value=True)
        
        if show_preview:
            preview_count = min(5, len(st.session_state.selected_personas))
            
            for i in st.session_state.selected_personas[:preview_count]:
                persona_data = system.dataset['data'][i]
                with st.expander(f"응답자 #{i} - {persona_data.get('participant_id', 'N/A')}"):
                    summary = persona_data.get('persona_summary', 'No summary')
                    st.write(summary[:500] + "..." if len(summary) > 500 else summary)

# 탭 2: 설문조사
with tab2:
    st.markdown("## 📊 설문조사")
    
    if not st.session_state.selected_personas:
        st.warning("⚠️ 먼저 응답자를 선택해주세요!")
        st.stop()
    
    # 질문 입력
    st.markdown("### 📝 설문 질문 작성")
    
    use_sample = st.checkbox("샘플 질문 사용", value=True)
    
    if use_sample:
        st.info("샘플 질문 2개가 자동으로 설정됩니다.")
        questions = [
            {"question": "How satisfied are you with your current job? (1=매우 불만족, 7=매우 만족)", 
             "scale": "1-7", "type": "likert"},
            {"question": "How likely are you to recommend AI tools to colleagues? (1=전혀 추천 안함, 7=매우 추천)", 
             "scale": "1-7", "type": "likert"}
        ]
    else:
        num_questions = st.number_input("질문 개수", min_value=1, max_value=10, value=2)
        questions = []
        
        for i in range(num_questions):
            q_text = st.text_area(f"질문 {i+1}", key=f"survey_q_{i}")
            if q_text:
                questions.append({
                    "question": q_text,
                    "scale": "1-7",
                    "type": "likert"
                })
    
    # 설정
    st.divider()
    st.markdown("### ⚙️ 설정")
    
    col1, col2 = st.columns(2)
    with col1:
        delay = st.slider("API 호출 지연 (초)", 0.0, 2.0, 0.5, 0.1)
    with col2:
        test_mode = st.checkbox("테스트 모드 (3명만)", value=True)
    
    # 시작 버튼
    if st.button("▶️ 설문조사 시작", type="primary", use_container_width=True):
        if not questions:
            st.error("❌ 질문을 입력해주세요!")
        else:
            # 테스트 모드
            personas_to_survey = st.session_state.selected_personas[:3] if test_mode else st.session_state.selected_personas
            
            survey = system.create_survey(questions)
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            start_time = time.time()
            
            with st.spinner("설문조사 진행 중..."):
                results = system.conduct_survey(survey, personas_to_survey)
                st.session_state.survey_results = results
            
            progress_bar.progress(1.0)
            status_text.empty()
            
            elapsed = time.time() - start_time
            
            st.success(f"✅ 설문조사 완료! ({elapsed:.1f}초)")
            st.balloons()
            
            # 결과 미리보기
            st.markdown("### 📊 결과 미리보기")
            st.dataframe(results, use_container_width=True)

# 탭 3: 인터뷰
with tab3:
    st.markdown("## 💬 인터뷰")
    
    if not st.session_state.selected_personas:
        st.warning("⚠️ 먼저 응답자를 선택해주세요!")
        st.stop()
    
    # 질문 입력
    st.markdown("### 📝 인터뷰 질문 작성")
    
    use_sample_interview = st.checkbox("샘플 질문 사용", value=True, key="interview_sample")
    
    if use_sample_interview:
        st.info("샘플 질문 2개가 자동으로 설정됩니다.")
        interview_questions = [
            "What aspects of your work do you find most meaningful?",
            "How do you see AI impacting your profession in the next 5 years?"
        ]
    else:
        num_interview_q = st.number_input("질문 개수", min_value=1, max_value=10, value=2, key="interview_count")
        interview_questions = []
        
        for i in range(num_interview_q):
            q_text = st.text_area(f"질문 {i+1}", key=f"interview_q_{i}")
            if q_text:
                interview_questions.append(q_text)
    
    # 설정
    st.divider()
    st.markdown("### ⚙️ 설정")
    
    col1, col2 = st.columns(2)
    with col1:
        interview_delay = st.slider("API 호출 지연 (초)", 0.0, 2.0, 0.5, 0.1, key="interview_delay")
    with col2:
        interview_test = st.checkbox("테스트 모드 (3명만)", value=True, key="interview_test")
    
    # 시작 버튼
    if st.button("▶️ 인터뷰 시작", type="primary", use_container_width=True):
        if not interview_questions:
            st.error("❌ 질문을 입력해주세요!")
        else:
            personas_to_interview = st.session_state.selected_personas[:3] if interview_test else st.session_state.selected_personas
            
            interview = system.create_interview(interview_questions)
            
            progress_bar = st.progress(0)
            
            start_time = time.time()
            
            with st.spinner("인터뷰 진행 중..."):
                results = system.conduct_interview(interview, personas_to_interview)
                st.session_state.interview_results = results
            
            progress_bar.progress(1.0)
            
            elapsed = time.time() - start_time
            
            st.success(f"✅ 인터뷰 완료! ({elapsed:.1f}초)")
            st.balloons()
            
            # 결과 미리보기
            st.markdown("### 💬 결과 미리보기")
            st.dataframe(results, use_container_width=True)

# 탭 4: 결과 분석
with tab4:
    st.markdown("## 📈 결과 분석")
    
    has_survey = st.session_state.survey_results is not None
    has_interview = st.session_state.interview_results is not None
    
    if not has_survey and not has_interview:
        st.info("💡 아직 수집된 결과가 없습니다. 설문조사나 인터뷰를 먼저 진행하세요.")
        st.stop()
    
    # 설문조사 결과 분석
    if has_survey:
        st.markdown("### 📊 설문조사 결과")
        
        df = st.session_state.survey_results
        
        # 기본 통계
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("응답자 수", len(df))
        
        response_cols = [col for col in df.columns if col.startswith('Q') and not col.endswith('_reasoning')]
        
        with col2:
            st.metric("질문 수", len(response_cols))
        
        with col3:
            if response_cols:
                avg_score = df[response_cols].mean().mean()
                st.metric("전체 평균", f"{avg_score:.2f}")
        
        # 질문별 통계
        st.divider()
        st.markdown("#### 📊 질문별 통계")
        
        stats_data = []
        for col in response_cols:
            stats_data.append({
                '질문': col,
                '평균': df[col].mean(),
                '중앙값': df[col].median(),
                '표준편차': df[col].std(),
                '최소': df[col].min(),
                '최대': df[col].max()
            })
        
        stats_df = pd.DataFrame(stats_data)
        st.dataframe(stats_df, use_container_width=True)
        
        # 시각화
        st.divider()
        st.markdown("#### 📊 평균 점수 차트")
        
        fig = px.bar(
            stats_df,
            x='질문',
            y='평균',
            title='질문별 평균 점수',
            color='평균',
            color_continuous_scale='RdYlGn',
            range_color=[1, 7]
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 다운로드
        st.divider()
        st.markdown("#### 💾 다운로드")
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv_data = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                "📥 CSV 다운로드",
                data=csv_data,
                file_name=f"survey_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            json_data = df.to_json(orient='records', force_ascii=False, indent=2)
            st.download_button(
                "📥 JSON 다운로드",
                data=json_data,
                file_name=f"survey_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
    
    # 인터뷰 결과 분석
    if has_interview:
        st.divider()
        st.markdown("### 💬 인터뷰 결과")
        
        df_interview = st.session_state.interview_results
        
        # 기본 통계
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("인터뷰 수", len(df_interview))
        
        with col2:
            response_cols = [col for col in df_interview.columns if col.startswith('Q')]
            st.metric("질문 수", len(response_cols))
        
        # 응답 길이 분석
        st.divider()
        st.markdown("#### 📏 응답 길이 분석")
        
        length_data = []
        for col in response_cols:
            avg_length = df_interview[col].apply(lambda x: len(str(x))).mean()
            length_data.append({
                '질문': col,
                '평균 길이 (글자)': avg_length
            })
        
        length_df = pd.DataFrame(length_data)
        
        fig_length = px.bar(
            length_df,
            x='질문',
            y='평균 길이 (글자)',
            title='질문별 평균 응답 길이',
            color='평균 길이 (글자)',
            color_continuous_scale='Blues'
        )
        st.plotly_chart(fig_length, use_container_width=True)
        
        # 인터뷰 내용 보기
        st.divider()
        st.markdown("#### 📖 인터뷰 내용")
        
        selected_participant = st.selectbox(
            "응답자 선택",
            range(len(df_interview)),
            format_func=lambda x: f"응답자 #{df_interview.iloc[x]['participant_id']}"
        )
        
        if selected_participant is not None:
            row = df_interview.iloc[selected_participant]
            
            for col in response_cols:
                with st.expander(f"**{col}**"):
                    st.write(row[col])
        
        # 다운로드
        st.divider()
        st.markdown("#### 💾 다운로드")
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv_data_interview = df_interview.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                "📥 CSV 다운로드",
                data=csv_data_interview,
                file_name=f"interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col2:
            json_data_interview = df_interview.to_json(orient='records', force_ascii=False, indent=2)
            st.download_button(
                "📥 JSON 다운로드",
                data=json_data_interview,
                file_name=f"interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )

# 푸터
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 2rem;'>
    <p>Powered by OpenAI GPT-4 | Hugging Face Twin-2K-500</p>
    <p>Digital Twin Research System</p>
</div>
""", unsafe_allow_html=True)

