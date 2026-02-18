#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
고도화된 디지털 트윈 서베이 인터뷰 시뮬레이션 GUI
Digital-Twin-Simulation 프로젝트의 방법론을 적용한 향상된 Streamlit 애플리케이션
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from typing import List, Dict, Any
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 로컬 모듈 임포트
from src.dataset_loader import DatasetLoader, Persona
from src.enhanced_ai_agent import EnhancedAIAgent, ResponseMetadata
from advanced_simulation_system import (
    AdvancedPersonaSimulator, SimulationConfig, 
    SurveyQuestion, InterviewGuide, SimulationAnalyzer
)

# 페이지 설정
st.set_page_config(
    page_title="🤖 고도화된 디지털 트윈 시뮬레이션",
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
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        border-left: 4px solid #667eea;
    }
    
    .simulation-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border: 1px solid #dee2e6;
        margin-bottom: 1rem;
    }
    
    .response-box {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2196f3;
        margin: 0.5rem 0;
    }
    
    .persona-info {
        background: #f3e5f5;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #9c27b0;
        margin: 0.5rem 0;
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

def initialize_session_state():
    """세션 상태 초기화"""
    if 'system_initialized' not in st.session_state:
        st.session_state.system_initialized = False
    
    if 'loader' not in st.session_state:
        st.session_state.loader = None
    
    if 'enhanced_ai_agent' not in st.session_state:
        st.session_state.enhanced_ai_agent = None
    
    if 'simulator' not in st.session_state:
        st.session_state.simulator = None
    
    if 'selected_personas' not in st.session_state:
        st.session_state.selected_personas = []
    
    if 'simulation_results' not in st.session_state:
        st.session_state.simulation_results = []
    
    if 'simulation_config' not in st.session_state:
        st.session_state.simulation_config = None

def initialize_system():
    """시스템 초기화"""
    try:
        # 데이터 로더 초기화
        if st.session_state.loader is None:
            with st.spinner("데이터셋 로딩 중..."):
                st.session_state.loader = DatasetLoader()
                st.session_state.loader.load()
        
        # 향상된 AI 에이전트 초기화
        if st.session_state.enhanced_ai_agent is None:
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                st.error("OpenAI API 키가 설정되지 않았습니다.")
                return False
            
            st.session_state.enhanced_ai_agent = EnhancedAIAgent(api_key)
        
        # 시뮬레이터 초기화
        if st.session_state.simulator is None:
            config = SimulationConfig(
                model_name="gpt-4o-mini",
                temperature=0.7,
                batch_size=5
            )
            st.session_state.simulator = AdvancedPersonaSimulator(config)
            st.session_state.simulation_config = config
        
        st.session_state.system_initialized = True
        return True
        
    except Exception as e:
        st.error(f"시스템 초기화 실패: {str(e)}")
        return False

def display_header():
    """헤더 표시"""
    st.markdown("""
    <div class="main-header">
        <h1>🤖 고도화된 디지털 트윈 시뮬레이션</h1>
        <p>Digital-Twin-Simulation 방법론을 적용한 AI 기반 서베이 및 인터뷰 시뮬레이션</p>
    </div>
    """, unsafe_allow_html=True)

def display_system_status():
    """시스템 상태 표시"""
    if st.session_state.system_initialized:
        st.success("✅ 시스템이 초기화되었습니다.")
        
        # 통계 표시
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("총 페르소나", len(st.session_state.loader.get_all_personas()))
        
        with col2:
            st.metric("선택된 응답자", len(st.session_state.selected_personas))
        
        with col3:
            st.metric("시뮬레이션 결과", len(st.session_state.simulation_results))
        
        with col4:
            if st.session_state.enhanced_ai_agent:
                stats = st.session_state.enhanced_ai_agent.get_response_statistics()
                st.metric("평균 신뢰도", f"{stats.get('average_confidence', 0):.2f}")
    else:
        st.error("❌ 시스템이 초기화되지 않았습니다.")

def persona_selection_page():
    """페르소나 선택 페이지"""
    st.header("👥 페르소나 선택")
    
    if not st.session_state.system_initialized:
        st.warning("시스템을 먼저 초기화해주세요.")
        return
    
    # 선택 방법
    selection_method = st.radio(
        "선택 방법",
        ["랜덤 샘플링", "ID 직접 입력", "특성 기반 필터링", "고급 시뮬레이션"]
    )
    
    if selection_method == "랜덤 샘플링":
        num_personas = st.slider("선택할 페르소나 수", 1, 20, 5)
        if st.button("랜덤 선택"):
            all_personas = st.session_state.loader.get_all_personas()
            selected = st.session_state.loader.get_random_sample(num_personas)
            st.session_state.selected_personas = selected
            st.success(f"✅ {len(selected)}개의 페르소나를 선택했습니다.")
    
    elif selection_method == "ID 직접 입력":
        persona_ids = st.text_area(
            "페르소나 ID 입력 (쉼표로 구분)",
            placeholder="예: 100, 200, 300"
        )
        if st.button("ID로 선택"):
            try:
                ids = [id.strip() for id in persona_ids.split(',')]
                selected = []
                for id in ids:
                    persona = st.session_state.loader.get_persona_by_id(id)
                    if persona:
                        selected.append(persona)
                    else:
                        st.warning(f"페르소나 {id}를 찾을 수 없습니다.")
                
                st.session_state.selected_personas = selected
                st.success(f"✅ {len(selected)}개의 페르소나를 선택했습니다.")
            except Exception as e:
                st.error(f"선택 실패: {str(e)}")
    
    elif selection_method == "특성 기반 필터링":
        st.info("특성 기반 필터링 기능은 개발 중입니다.")
    
    elif selection_method == "고급 시뮬레이션":
        st.info("고급 시뮬레이션 기능은 개발 중입니다.")
    
    # 선택된 페르소나 표시
    if st.session_state.selected_personas:
        st.subheader("선택된 페르소나")
        
        for i, persona in enumerate(st.session_state.selected_personas):
            with st.expander(f"페르소나 {persona.id}"):
                st.markdown(f"""
                <div class="persona-info">
                    <strong>ID:</strong> {persona.id}<br>
                    <strong>요약:</strong> {persona.get_summary()[:200]}...
                </div>
                """, unsafe_allow_html=True)

def survey_simulation_page():
    """서베이 시뮬레이션 페이지"""
    st.header("📊 서베이 시뮬레이션")
    
    if not st.session_state.system_initialized:
        st.warning("시스템을 먼저 초기화해주세요.")
        return
    
    if not st.session_state.selected_personas:
        st.warning("먼저 페르소나를 선택해주세요.")
        return
    
    # 질문 설정
    st.subheader("질문 설정")
    
    question_type = st.selectbox(
        "질문 유형",
        ["likert", "multiple_choice", "open_ended"]
    )
    
    question_text = st.text_area(
        "질문 내용",
        placeholder="예: 새로운 기술 제품을 얼마나 자주 구매하시나요?"
    )
    
    if question_type == "likert":
        scale_min = st.number_input("최소 점수", 1, 10, 1)
        scale_max = st.number_input("최대 점수", 1, 10, 7)
        scale_range = (scale_min, scale_max)
    else:
        scale_range = (1, 7)
    
    if question_type == "multiple_choice":
        options_text = st.text_area(
            "선택지 (한 줄에 하나씩)",
            placeholder="가격\n성능\n디자인\n브랜드"
        )
        options = [opt.strip() for opt in options_text.split('\n') if opt.strip()]
    else:
        options = None
    
    context = st.text_input("컨텍스트", placeholder="기술 제품 선호도 조사")
    
    # 시뮬레이션 실행
    if st.button("🚀 시뮬레이션 실행", type="primary"):
        if not question_text:
            st.error("질문 내용을 입력해주세요.")
            return
        
        # 질문 객체 생성
        question = SurveyQuestion(
            question_id=f"q_{datetime.now().strftime('%H%M%S')}",
            question_text=question_text,
            question_type=question_type,
            scale_range=scale_range,
            options=options
        )
        
        # 시뮬레이션 실행
        with st.spinner("시뮬레이션 실행 중..."):
            try:
                # 페르소나 데이터 변환
                persona_data = []
                for persona in st.session_state.selected_personas:
                    persona_data.append({
                        'id': persona.id,
                        'persona_summary': persona.data.get('persona_summary', ''),
                        'persona_text': persona.data.get('persona_text', '')
                    })
                
                # 향상된 AI 에이전트로 응답 생성
                results = []
                for persona in st.session_state.selected_personas:
                    result = st.session_state.enhanced_ai_agent.generate_enhanced_survey_response(
                        persona=persona,
                        question=question_text,
                        question_type=question_type,
                        scale_range=scale_range,
                        context=context,
                        options=options
                    )
                    results.append({
                        'persona_id': persona.id,
                        'question': question_text,
                        'result': result
                    })
                
                st.session_state.simulation_results.extend(results)
                st.success(f"✅ {len(results)}개의 응답을 생성했습니다.")
                
            except Exception as e:
                st.error(f"시뮬레이션 실패: {str(e)}")
    
    # 결과 표시
    if st.session_state.simulation_results:
        st.subheader("시뮬레이션 결과")
        
        for result in st.session_state.simulation_results[-len(st.session_state.selected_personas):]:
            with st.expander(f"페르소나 {result['persona_id']} 응답"):
                response_data = result['result']
                
                st.markdown(f"""
                <div class="response-box">
                    <strong>응답:</strong> {response_data.get('response', 'N/A')}<br>
                    <strong>점수:</strong> {response_data.get('score', 'N/A')}<br>
                    <strong>이유:</strong> {response_data.get('reasoning', 'N/A')}
                </div>
                """, unsafe_allow_html=True)
                
                # 메타데이터 표시
                if 'metadata' in response_data:
                    metadata = response_data['metadata']
                    st.write(f"**신뢰도:** {metadata.confidence:.2f}")
                    st.write(f"**응답 스타일:** {metadata.response_style}")
                    st.write(f"**사용된 특성:** {', '.join(metadata.persona_traits_used)}")

def interview_simulation_page():
    """인터뷰 시뮬레이션 페이지"""
    st.header("💬 인터뷰 시뮬레이션")
    
    if not st.session_state.system_initialized:
        st.warning("시스템을 먼저 초기화해주세요.")
        return
    
    if not st.session_state.selected_personas:
        st.warning("먼저 페르소나를 선택해주세요.")
        return
    
    # 인터뷰 가이드 설정
    st.subheader("인터뷰 가이드 설정")
    
    interview_title = st.text_input("인터뷰 제목", "기술 제품 사용 경험 인터뷰")
    
    questions_text = st.text_area(
        "인터뷰 질문들 (한 줄에 하나씩)",
        placeholder="평소 어떤 기술 제품을 주로 사용하시나요?\n최근 구매한 제품 중 만족도가 높은 것은 무엇인가요?\n제품 구매 시 가장 중요하게 생각하는 요소는 무엇인가요?",
        height=150
    )
    
    interview_style = st.selectbox(
        "인터뷰 스타일",
        ["친근한 대화", "전문적", "캐주얼", "공식적"]
    )
    
    context = st.text_input("인터뷰 컨텍스트", "기술 제품 사용 경험과 선호도에 대한 심층 인터뷰")
    
    # 인터뷰 시뮬레이션 실행
    if st.button("🎤 인터뷰 시뮬레이션 실행", type="primary"):
        if not questions_text:
            st.error("인터뷰 질문을 입력해주세요.")
            return
        
        questions = [q.strip() for q in questions_text.split('\n') if q.strip()]
        
        # 인터뷰 가이드 생성
        interview_guide = InterviewGuide(
            guide_id=f"interview_{datetime.now().strftime('%H%M%S')}",
            title=interview_title,
            questions=questions,
            context=context,
            style=interview_style
        )
        
        # 시뮬레이션 실행
        with st.spinner("인터뷰 시뮬레이션 실행 중..."):
            try:
                results = []
                for persona in st.session_state.selected_personas:
                    result = st.session_state.enhanced_ai_agent.generate_enhanced_interview_response(
                        persona=persona,
                        interview_questions=questions,
                        interview_style=interview_style,
                        context=context
                    )
                    results.append({
                        'persona_id': persona.id,
                        'interview_guide': interview_guide,
                        'result': result
                    })
                
                st.session_state.simulation_results.extend(results)
                st.success(f"✅ {len(results)}개의 인터뷰를 완료했습니다.")
                
            except Exception as e:
                st.error(f"인터뷰 시뮬레이션 실패: {str(e)}")
    
    # 결과 표시
    if st.session_state.simulation_results:
        st.subheader("인터뷰 결과")
        
        interview_results = [r for r in st.session_state.simulation_results if 'interview_guide' in r]
        
        for result in interview_results[-len(st.session_state.selected_personas):]:
            with st.expander(f"페르소나 {result['persona_id']} 인터뷰"):
                response_data = result['result']
                
                st.markdown(f"""
                <div class="response-box">
                    <strong>인터뷰 응답:</strong><br>
                    {response_data.get('conversation', 'N/A')}
                </div>
                """, unsafe_allow_html=True)
                
                # 메타데이터 표시
                if 'metadata' in response_data:
                    metadata = response_data['metadata']
                    st.write(f"**신뢰도:** {metadata.confidence:.2f}")
                    st.write(f"**응답 스타일:** {metadata.response_style}")

def analysis_page():
    """분석 페이지"""
    st.header("📈 결과 분석")
    
    if not st.session_state.simulation_results:
        st.warning("분석할 시뮬레이션 결과가 없습니다.")
        return
    
    # 기본 통계
    st.subheader("기본 통계")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("총 응답 수", len(st.session_state.simulation_results))
    
    with col2:
        unique_personas = len(set(r['persona_id'] for r in st.session_state.simulation_results))
        st.metric("참여 페르소나", unique_personas)
    
    with col3:
        if st.session_state.enhanced_ai_agent:
            stats = st.session_state.enhanced_ai_agent.get_response_statistics()
            st.metric("평균 신뢰도", f"{stats.get('average_confidence', 0):.2f}")
    
    # 응답 분포 분석
    st.subheader("응답 분포")
    
    # 점수 분포 (리커트 척도)
    scores = []
    for result in st.session_state.simulation_results:
        if 'result' in result and 'score' in result['result'] and result['result']['score'] is not None:
            scores.append(result['result']['score'])
    
    if scores:
        fig = px.histogram(
            x=scores, 
            title="점수 분포",
            labels={'x': '점수', 'y': '빈도'},
            nbins=10
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # 페르소나별 응답 다양성
    st.subheader("페르소나별 응답 다양성")
    
    persona_responses = {}
    for result in st.session_state.simulation_results:
        persona_id = result['persona_id']
        if persona_id not in persona_responses:
            persona_responses[persona_id] = []
        persona_responses[persona_id].append(result)
    
    diversity_data = []
    for persona_id, responses in persona_responses.items():
        diversity_data.append({
            'persona_id': persona_id,
            'response_count': len(responses),
            'unique_responses': len(set(str(r['result']) for r in responses))
        })
    
    if diversity_data:
        df_diversity = pd.DataFrame(diversity_data)
        
        fig = px.bar(
            df_diversity, 
            x='persona_id', 
            y='unique_responses',
            title="페르소나별 고유 응답 수"
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # 신뢰도 분석
    st.subheader("신뢰도 분석")
    
    confidences = []
    for result in st.session_state.simulation_results:
        if 'result' in result and 'metadata' in result['result']:
            metadata = result['result']['metadata']
            if hasattr(metadata, 'confidence'):
                confidences.append(metadata.confidence)
    
    if confidences:
        fig = px.box(
            y=confidences,
            title="신뢰도 분포",
            labels={'y': '신뢰도'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # 결과 내보내기
    st.subheader("결과 내보내기")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("JSON으로 내보내기"):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"simulation_results_{timestamp}.json"
            
            # 결과를 JSON으로 변환
            export_data = []
            for result in st.session_state.simulation_results:
                export_data.append({
                    'persona_id': result['persona_id'],
                    'result': result['result'],
                    'timestamp': datetime.now().isoformat()
                })
            
            json_str = json.dumps(export_data, ensure_ascii=False, indent=2)
            st.download_button(
                label="JSON 파일 다운로드",
                data=json_str,
                file_name=filename,
                mime="application/json"
            )
    
    with col2:
        if st.button("CSV로 내보내기"):
            # DataFrame으로 변환
            df_data = []
            for result in st.session_state.simulation_results:
                df_data.append({
                    'persona_id': result['persona_id'],
                    'response': result['result'].get('response', ''),
                    'score': result['result'].get('score', ''),
                    'reasoning': result['result'].get('reasoning', ''),
                    'timestamp': datetime.now().isoformat()
                })
            
            df = pd.DataFrame(df_data)
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"simulation_results_{timestamp}.csv"
            
            st.download_button(
                label="CSV 파일 다운로드",
                data=csv,
                file_name=filename,
                mime="text/csv"
            )

def main():
    """메인 함수"""
    initialize_session_state()
    
    # 시스템 초기화
    if not st.session_state.system_initialized:
        if st.button("🚀 시스템 초기화", type="primary"):
            initialize_system()
    
    if st.session_state.system_initialized:
        display_header()
        display_system_status()
        
        # 탭 생성
        tab1, tab2, tab3, tab4 = st.tabs([
            "👥 페르소나 선택", 
            "📊 서베이 시뮬레이션", 
            "💬 인터뷰 시뮬레이션", 
            "📈 결과 분석"
        ])
        
        with tab1:
            persona_selection_page()
        
        with tab2:
            survey_simulation_page()
        
        with tab3:
            interview_simulation_page()
        
        with tab4:
            analysis_page()
    
    else:
        st.markdown("""
        <div class="main-header">
            <h1>🤖 고도화된 디지털 트윈 시뮬레이션</h1>
            <p>Digital-Twin-Simulation 방법론을 적용한 AI 기반 서베이 및 인터뷰 시뮬레이션</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.info("시스템을 초기화하려면 위의 '시스템 초기화' 버튼을 클릭하세요.")

if __name__ == "__main__":
    main()
