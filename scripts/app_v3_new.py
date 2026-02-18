"""
디지털 트윈 서베이 시스템 - 새로운 Streamlit GUI
기존 시스템과 통합된 현대적인 인터페이스
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from src.dataset_loader import DatasetLoader
from src.ai_agent import AIAgent
from block_based_selector import BlockBasedSelector
import io
import contextlib

# 페이지 설정
st.set_page_config(
    page_title="🤖 LLM Customer Digital Twin",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 환경 변수 로드
try:
    load_dotenv()
except:
    pass

# 커스텀 CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #667eea;
        color: white;
        border-radius: 10px;
        padding: 0.5rem 1rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #764ba2;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
    }
    .success-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        margin: 1rem 0;
    }
    .info-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #d1ecf1;
        border: 1px solid #bee5eb;
        color: #0c5460;
        margin: 1rem 0;
    }
    .warning-box {
        padding: 1rem;
        border-radius: 0.5rem;
        background-color: #fff3e0;
        border: 1px solid #ff9800;
        color: #e65100;
        margin: 1rem 0;
    }
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #e8e8e8;
        text-align: center;
        margin: 0.5rem 0;
    }
    .metric-number {
        font-size: 2.5rem;
        font-weight: bold;
        color: #667eea;
        margin-bottom: 0.5rem;
    }
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """세션 상태 초기화"""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False
        st.session_state.loader = None
        st.session_state.ai_agent = None
        st.session_state.block_selector = None
        st.session_state.sample_personas = []
        st.session_state.survey_results = []
        st.session_state.interview_results = []
        st.session_state.experiment_results = []
        st.session_state.api_key = os.getenv("OPENAI_API_KEY", "")


def initialize_system():
    """시스템 초기화"""
    if st.session_state.initialized:
        return True
    
    try:
        # 데이터셋 로더 초기화
        if st.session_state.loader is None:
            loader = DatasetLoader()
            loader.load()
            st.session_state.loader = loader
        
        # AI 에이전트 초기화
        if st.session_state.ai_agent is None:
            agent = AIAgent(api_key=st.session_state.api_key)
            st.session_state.ai_agent = agent
        
        # 블록 기반 선택 시스템 초기화
        if st.session_state.block_selector is None:
            try:
                # 인코딩 문제 방지를 위해 출력을 캡처
                captured_output = io.StringIO()
                with contextlib.redirect_stdout(captured_output):
                    with contextlib.redirect_stderr(captured_output):
                        block_selector = BlockBasedSelector()
                        block_selector.load()
                
                st.session_state.block_selector = block_selector
            except Exception as e:
                st.warning(f"⚠️ 블록 기반 선택 시스템 초기화 실패: {e}")
        
        st.session_state.initialized = True
        return True
        
    except Exception as e:
        st.error(f"❌ 시스템 초기화 실패: {e}")
        return False


def main():
    """메인 애플리케이션"""
    initialize_session_state()
    
    # 헤더
    st.markdown(
        '<div style="text-align: center; color: #999; font-size: 0.9rem; margin-bottom: 0.5rem;">LLM Customer Digital Twin</div>',
        unsafe_allow_html=True
    )
    st.markdown('<h1 class="main-header">🤖 美 고객 디지털 트윈</h1>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">AI 기반 설문조사 & 인터뷰 플랫폼</div>',
        unsafe_allow_html=True
    )
    
    # 사이드바 - 설정
    with st.sidebar:
        st.header("⚙️ 시스템 설정")
        
        # API 키 입력
        api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            value=st.session_state.api_key,
            help="OpenAI API 키를 입력하세요"
        )
        
        if api_key != st.session_state.api_key:
            st.session_state.api_key = api_key
        
        # 모델 선택
        model = st.selectbox(
            "모델 선택",
            ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo"],
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
                    if initialize_system():
                        st.success("✅ 시스템이 성공적으로 초기화되었습니다!")
                        st.rerun()
                    else:
                        st.error("❌ 초기화에 실패했습니다.")
        
        st.markdown("---")
        
        # 시스템 상태
        if st.session_state.initialized:
            st.success("✅ 시스템 준비 완료")
            if st.session_state.loader:
                dataset_size = len(st.session_state.loader.get_all_personas())
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
    
    # 통계 대시보드
    st.markdown("### 📊 시스템 현황")
    
    col1, col2, col3, col4 = st.columns(4)
    
    total_personas = len(st.session_state.loader.get_all_personas()) if st.session_state.loader else 0
    selected = len(st.session_state.sample_personas)
    survey_count = len(st.session_state.survey_results)
    interview_count = len(st.session_state.interview_results)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{total_personas:,}</div>
            <div class="metric-label">전체 페르소나</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{selected}</div>
            <div class="metric-label">선택된 응답자</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{survey_count}</div>
            <div class="metric-label">설문 응답</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-number">{interview_count}</div>
            <div class="metric-label">인터뷰 완료</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
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
                ["랜덤 샘플링", "블록 기반 필터링", "조건별 필터링"],
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
                        all_personas = st.session_state.loader.get_all_personas()
                        import random
                        st.session_state.sample_personas = random.sample(all_personas, min(num_personas, len(all_personas)))
                        st.success(f"✅ {len(st.session_state.sample_personas)}명의 페르소나를 샘플링했습니다!")
            
            elif sampling_method == "블록 기반 필터링":
                if st.session_state.block_selector:
                    st.info("💡 블록 기반 필터링을 사용하여 정밀한 응답자 선정이 가능합니다.")
                    
                    # 블록 카테고리 표시
                    block_categories = st.session_state.block_selector.get_block_categories()
                    if block_categories:
                        st.markdown("**사용 가능한 블록 카테고리:**")
                        for cat_name, blocks in block_categories.items():
                            st.markdown(f"- **{cat_name.replace('_', ' ').title()}**: {', '.join(blocks[:3])}{'...' if len(blocks) > 3 else ''}")
                    
                    if st.button("🔍 블록 기반 샘플링"):
                        # 간단한 블록 기반 샘플링 (실제로는 더 복잡한 필터링 가능)
                        all_personas = st.session_state.block_selector.get_all_personas()
                        st.session_state.sample_personas = all_personas[:10]  # 처음 10개
                        st.success(f"✅ {len(st.session_state.sample_personas)}명의 페르소나를 선택했습니다!")
                else:
                    st.warning("⚠️ 블록 기반 선택 시스템이 초기화되지 않았습니다.")
            
            else:  # 조건별 필터링
                st.markdown("**필터 조건 설정**")
                st.info("💡 실제 데이터셋 구조에 맞게 필터 조건을 커스터마이징하세요")
                
                if st.button("🔍 필터링 실행"):
                    all_personas = st.session_state.loader.get_all_personas()
                    st.session_state.sample_personas = all_personas[:10]  # 예시
                    st.success(f"✅ {len(st.session_state.sample_personas)}명의 페르소나를 선택했습니다!")
        
        with col2:
            st.subheader("📊 선택된 페르소나")
            if st.session_state.sample_personas:
                st.metric("총 인원", len(st.session_state.sample_personas))
                
                # 첫 번째 페르소나 미리보기
                with st.expander("첫 번째 페르소나 미리보기"):
                    persona_preview = st.session_state.sample_personas[0]
                    # 주요 필드만 표시
                    preview_data = {k: v for k, v in list(persona_preview.data.items())[:5]}
                    st.json(preview_data)
            else:
                st.info("페르소나를 선택해주세요")
    
    # ==================== 탭 2: 서베이 ====================
    with tab2:
        st.header("📋 서베이 시뮬레이션")
        
        if not st.session_state.sample_personas:
            st.warning("⚠️ 먼저 '페르소나 선택' 탭에서 페르소나를 선택해주세요!")
        else:
            col1, col2 = st.columns([3, 2])
            
            with col1:
                st.subheader("서베이 설정")
                
                # 서베이 질문 입력
                survey_questions = st.text_area(
                    "서베이 질문 (한 줄에 하나씩)",
                    height=200,
                    placeholder="질문1\n질문2\n질문3\n질문4\n질문5",
                    help="각 질문을 한 줄씩 입력하세요"
                )
                
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
                
                questions = [q.strip() for q in survey_questions.split('\n') if q.strip()]
                st.info(f"📊 총 {num_respondents}명이 {len(questions)}개 질문에 답변합니다")
                
                # 실행 버튼
                if st.button("▶️ 서베이 실행", type="primary"):
                    if not questions:
                        st.error("질문을 입력해주세요!")
                    else:
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        results = []
                        for i, persona in enumerate(st.session_state.sample_personas[:num_respondents]):
                            status_text.text(f"진행 중... {i+1}/{num_respondents}")
                            
                            # AI 에이전트를 사용한 서베이 응답 생성
                            try:
                                response = st.session_state.ai_agent.generate_survey_response(
                                    persona, questions, survey_context
                                )
                                results.append({
                                    'persona_id': persona.id,
                                    'questions': questions,
                                    'responses': response,
                                    'context': survey_context,
                                    'timestamp': datetime.now().isoformat()
                                })
                            except Exception as e:
                                st.error(f"응답 생성 실패: {e}")
                                break
                            
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
                for i, (question, response) in enumerate(zip(latest_result['questions'], latest_result['responses']), 1):
                    with st.expander(f"Q{i}: {question}"):
                        st.write(response)
    
    # ==================== 탭 3: 인터뷰 ====================
    with tab3:
        st.header("🎤 인터뷰 시뮬레이션")
        
        if not st.session_state.sample_personas:
            st.warning("⚠️ 먼저 '페르소나 선택' 탭에서 페르소나를 선택해주세요!")
        else:
            col1, col2 = st.columns([3, 2])
            
            with col1:
                st.subheader("인터뷰 설정")
                
                # 인터뷰 가이드 입력
                interview_guide = st.text_area(
                    "인터뷰 가이드",
                    height=200,
                    placeholder="오프닝 질문\n주요 질문 1\n주요 질문 2\n주요 질문 3\n마무리 질문",
                    help="인터뷰에서 사용할 질문들을 입력하세요"
                )
                
                # 인터뷰 스타일 설정
                interview_style = st.selectbox(
                    "인터뷰 스타일",
                    ["친근한 대화", "전문적 인터뷰", "캐주얼 대화"],
                    help="인터뷰의 톤앤매너를 선택하세요"
                )
            
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
                    if not interview_guide.strip():
                        st.error("인터뷰 가이드를 입력해주세요!")
                    else:
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        results = []
                        for i, persona in enumerate(st.session_state.sample_personas[:num_interviewees]):
                            status_text.text(f"인터뷰 진행 중... {i+1}/{num_interviewees}")
                            
                            try:
                                # AI 에이전트를 사용한 인터뷰 진행
                                interview_result = st.session_state.ai_agent.generate_interview_response(
                                    persona, interview_guide, interview_style
                                )
                                results.append({
                                    'persona_id': persona.id,
                                    'interview_guide': interview_guide,
                                    'style': interview_style,
                                    'conversation': interview_result,
                                    'timestamp': datetime.now().isoformat()
                                })
                            except Exception as e:
                                st.error(f"인터뷰 진행 실패: {e}")
                                break
                            
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
                with st.expander("인터뷰 내용 보기"):
                    st.write(latest_interview['conversation'])
    
    # ==================== 탭 4: 실험 ====================
    with tab4:
        st.header("🧪 행동 실험")
        
        if not st.session_state.sample_personas:
            st.warning("⚠️ 먼저 '페르소나 선택' 탭에서 페르소나를 선택해주세요!")
        else:
            col1, col2 = st.columns([3, 2])
            
            with col1:
                st.subheader("실험 설정")
                
                # 실험 시나리오 입력
                experiment_scenario = st.text_area(
                    "실험 시나리오",
                    height=150,
                    placeholder="실험 상황을 설명하세요...",
                    help="실험 참가자에게 제시할 상황을 입력하세요"
                )
                
                # 실험 질문
                experiment_question = st.text_input(
                    "실험 질문",
                    placeholder="실험 참가자에게 할 질문을 입력하세요",
                    help="실험의 핵심 질문을 입력하세요"
                )
                
                # 실험 조건
                experiment_conditions = st.text_area(
                    "실험 조건 (선택사항)",
                    height=100,
                    placeholder="조건1\n조건2\n조건3",
                    help="다양한 실험 조건을 입력하세요 (한 줄에 하나씩)"
                )
            
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
                    if not experiment_scenario.strip() or not experiment_question.strip():
                        st.error("실험 시나리오와 질문을 입력해주세요!")
                    else:
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        results = []
                        conditions = [c.strip() for c in experiment_conditions.split('\n') if c.strip()]
                        
                        for i, persona in enumerate(st.session_state.sample_personas[:num_participants]):
                            status_text.text(f"실험 진행 중... {i+1}/{num_participants}")
                            
                            try:
                                # AI 에이전트를 사용한 실험 응답 생성
                                experiment_result = st.session_state.ai_agent.generate_experiment_response(
                                    persona, experiment_scenario, experiment_question, conditions
                                )
                                results.append({
                                    'persona_id': persona.id,
                                    'scenario': experiment_scenario,
                                    'question': experiment_question,
                                    'conditions': conditions,
                                    'response': experiment_result,
                                    'timestamp': datetime.now().isoformat()
                                })
                            except Exception as e:
                                st.error(f"실험 진행 실패: {e}")
                                break
                            
                            progress_bar.progress((i + 1) / num_participants)
                        
                        st.session_state.experiment_results = results
                        status_text.empty()
                        progress_bar.empty()
                        st.success(f"✅ 실험 완료! {len(results)}개의 결과를 수집했습니다.")
            
            # 결과 요약
            if st.session_state.experiment_results:
                st.markdown("---")
                st.subheader("📊 실험 결과 요약")
                
                st.metric("참가자 수", len(st.session_state.experiment_results))
                
                # 최근 응답 미리보기
                st.markdown("**최근 응답 샘플:**")
                latest = st.session_state.experiment_results[-1]
                with st.expander("응답 보기"):
                    st.write(latest['response'])
    
    # ==================== 탭 5: 결과 분석 ====================
    with tab5:
        st.header("📊 결과 분석")
        
        # 서베이 결과 분석
        if st.session_state.survey_results:
            st.subheader("📋 서베이 결과")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("총 응답 수", len(st.session_state.survey_results))
            with col2:
                st.metric("응답자 수", len(set(r['persona_id'] for r in st.session_state.survey_results)))
            with col3:
                st.metric("평균 질문 수", len(st.session_state.survey_results[0]['questions']) if st.session_state.survey_results else 0)
            
            # 결과 표시
            st.markdown("**최근 서베이 결과:**")
            latest_survey = st.session_state.survey_results[-1]
            for i, (question, response) in enumerate(zip(latest_survey['questions'], latest_survey['responses']), 1):
                with st.expander(f"Q{i}: {question}"):
                    st.write(response)
            
            # 다운로드 버튼
            st.markdown("---")
            col1, col2 = st.columns(2)
            
            with col1:
                # CSV 다운로드
                survey_data = []
                for result in st.session_state.survey_results:
                    for question, response in zip(result['questions'], result['responses']):
                        survey_data.append({
                            'persona_id': result['persona_id'],
                            'question': question,
                            'response': response,
                            'timestamp': result['timestamp']
                        })
                
                df = pd.DataFrame(survey_data)
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label="📥 CSV 다운로드",
                    data=csv,
                    file_name=f"survey_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            with col2:
                # JSON 다운로드
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
