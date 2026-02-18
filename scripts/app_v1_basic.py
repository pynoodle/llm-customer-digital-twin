"""
디지털 트윈 설문조사 & 인터뷰 시스템
Streamlit GUI 애플리케이션
"""

import streamlit as st
import os
import pandas as pd
from dotenv import load_dotenv
from src.dataset_loader import DatasetLoader
from src.ai_agent import AIAgent
from block_based_selector import BlockBasedSelector

# 페이지 설정
st.set_page_config(
    page_title="LLM Customer Digital Twin",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 환경 변수 로드 (에러 무시)
try:
    load_dotenv()
except:
    pass  # .env 파일이 없거나 잘못되어도 계속 진행

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
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .warning-box {
        background-color: #fff3e0;
        padding: 1rem;
        border-radius: 8px;
        border-left: 5px solid #ff9800;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """세션 상태를 초기화합니다."""
    if 'initialized' not in st.session_state:
        st.session_state.initialized = False
    
    if 'loader' not in st.session_state:
        st.session_state.loader = None
    
    if 'ai_agent' not in st.session_state:
        st.session_state.ai_agent = None
    
    if 'block_selector' not in st.session_state:
        st.session_state.block_selector = None
    
    if 'selected_personas' not in st.session_state:
        st.session_state.selected_personas = []
    
    if 'survey_responses' not in st.session_state:
        st.session_state.survey_responses = []
    
    if 'interview_results' not in st.session_state:
        st.session_state.interview_results = []
    
    if 'api_key' not in st.session_state:
        # 환경 변수에서 API 키 읽기
        api_key = os.getenv("OPENAI_API_KEY", "")
        st.session_state.api_key = api_key


def check_api_key():
    """API 키를 확인하고 설정합니다."""
    # API 키가 이미 세션에 있으면 통과
    if st.session_state.api_key and len(st.session_state.api_key) > 20:
        return True
    
    st.warning("⚠️ OpenAI API 키가 설정되지 않았습니다.")
    
    with st.expander("API 키 설정 방법", expanded=True):
        st.markdown("""
        **API 키를 입력하세요**
        """)
        
        api_key_input = st.text_input(
            "OpenAI API 키를 입력하세요",
            type="password",
            key="api_key_input",
            value=""
        )
        
        if st.button("API 키 저장"):
            if api_key_input:
                st.session_state.api_key = api_key_input
                st.success("✅ API 키가 저장되었습니다!")
                st.rerun()
            else:
                st.error("API 키를 입력해주세요.")
    
    return False


def initialize_system():
    """시스템을 초기화합니다."""
    if st.session_state.initialized:
        return True
    
    if not check_api_key():
        return False
    
    with st.spinner("🔄 시스템 초기화 중..."):
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
                    import io
                    import contextlib
                    
                    # 출력 캡처
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
    """메인 함수"""
    initialize_session_state()
    
    # 헤더
    st.markdown(
        '<div style="text-align: center; color: #999; font-size: 0.9rem; margin-bottom: 0.5rem;">LLM Customer Digital Twin</div>',
        unsafe_allow_html=True
    )
    st.markdown('<div class="main-header">🤖 美 고객 디지털 트윈</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">AI 기반 설문조사 & 인터뷰 플랫폼</div>',
        unsafe_allow_html=True
    )
    
    # 시스템 초기화
    if not initialize_system():
        st.stop()
    
    # 초기화 성공 메시지
    st.success("✅ 시스템이 준비되었습니다!")
    
    # 통계 정보
    col1, col2, col3, col4 = st.columns(4)
    
    total_personas = len(st.session_state.loader.get_all_personas())
    selected = len(st.session_state.selected_personas)
    survey_count = len(st.session_state.survey_responses)
    interview_count = len(st.session_state.interview_results)
    
    with col1:
        st.metric("전체 페르소나", f"{total_personas:,}")
    
    with col2:
        st.metric("선택된 응답자", selected)
    
    with col3:
        st.metric("설문 응답", survey_count)
    
    with col4:
        st.metric("인터뷰 완료", interview_count)
    
    st.divider()
    
    # 주요 기능 소개
    st.markdown("## 📋 주요 기능")
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container():
            st.markdown("### 📊 설문조사")
            st.markdown("""
            - **1-7점 리커트 척도** 응답
            - 구조화된 질문 관리
            - 자동 통계 분석
            - 다양한 형식으로 내보내기
            """)
        
        st.markdown("")
        
        with st.container():
            st.markdown("### 🎯 응답자 선택")
            st.markdown("""
            - 무작위 샘플링
            - 조건 기반 필터링
            - 미리보기 기능
            - ID 직접 선택
            """)
    
    with col2:
        with st.container():
            st.markdown("### 💬 인터뷰")
            st.markdown("""
            - 개방형 질문 응답
            - 자연스러운 대화
            - 인터뷰록 자동 생성
            - 심층 분석 지원
            """)
        
        st.markdown("")
        
        with st.container():
            st.markdown("### 📁 결과 관리")
            st.markdown("""
            - JSON, CSV, Excel 형식
            - 실시간 시각화
            - 통계 자동 계산
            - 인터뷰록 다운로드
            """)

    
    st.divider()
    
    # 시작 가이드
    st.markdown("## 🚀 시작하기")
    
    st.markdown("""
    1. **왼쪽 사이드바**에서 원하는 메뉴를 선택하세요
    2. **응답자 선택** 페이지에서 연구 대상을 선택합니다
    3. **설문조사** 또는 **인터뷰** 페이지에서 연구를 진행합니다
    4. **결과 보기** 페이지에서 분석 결과를 확인하고 다운로드합니다
    """)
    
    # 경고 메시지
    if not st.session_state.selected_personas:
        st.markdown('<div class="warning-box">', unsafe_allow_html=True)
        st.warning("⚠️ 아직 응답자를 선택하지 않았습니다. '응답자 선택' 페이지로 이동하세요.")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()
    
    # 데이터셋 정보
    with st.expander("📊 데이터셋 정보", expanded=False):
        st.markdown("### Twin-2K-500 데이터셋")
        st.markdown("""
        - **출처**: [Hugging Face - LLM-Digital-Twin](https://huggingface.co/datasets/LLM-Digital-Twin/Twin-2K-500)
        - **참가자**: 2,058명의 디지털 트윈
        - **설명**: 실제 사람들의 500개 이상 질문 응답 데이터 기반
        - **활용**: AI 기반 설문조사 및 인터뷰 시뮬레이션
        """)
        
        st.divider()
        
        if st.session_state.loader:
            # 기존 데이터셋 정보
            categorized = st.session_state.loader.get_categorized_fields()
            
            # 블록 기반 데이터셋 정보 추가
            if st.session_state.block_selector:
                st.markdown("### 🎯 블록 기반 설문대상 선정")
                st.markdown("블록별 특성을 활용한 정밀한 응답자 선정이 가능합니다.")
                
                # 블록 통계 표시
                block_stats = st.session_state.block_selector.get_block_statistics()
                if block_stats:
                    st.markdown("#### 📊 주요 블록 분포")
                    
                    # 블록 설명 매핑
                    block_descriptions = {
                        "Demographics": "인구통계학적 특성 (나이, 성별, 지역 등)",
                        "Personality": "성격 특성 및 심리적 특성",
                        "Cognitive Tests": "인지능력 및 사고력 테스트",
                        "Economic Preferences": "경제적 선호도 및 의사결정",
                        "Product Preferences - Pricing": "제품 가격 선호도",
                        "False Consensus": "거짓 합의 효과 실험",
                        "Base Rate 70 Engineers": "기본률 오류 실험 (70명 엔지니어)",
                        "Base Rate 30 Engineers": "기본률 오류 실험 (30명 엔지니어)",
                        "Disease Loss": "질병 손실 프레이밍 실험",
                        "Disease Gain": "질병 이익 프레이밍 실험",
                        "Anchoring - African Countries High": "앵커링 효과 (아프리카 국가 - 높은 앵커)",
                        "Anchoring - African Countries Low": "앵커링 효과 (아프리카 국가 - 낮은 앵커)",
                        "Anchoring - Redwood High": "앵커링 효과 (세쿼이아 - 높은 앵커)",
                        "Anchoring - Redwood Low": "앵커링 효과 (세쿼이아 - 낮은 앵커)",
                        "Outcome Bias - Success": "결과 편향 (성공 사례)",
                        "Outcome Bias - Failure": "결과 편향 (실패 사례)",
                        "Sunk Cost - Yes": "매몰비용 효과 (예)",
                        "Sunk Cost - No": "매몰비용 효과 (아니오)",
                        "Allais Form 1": "앨리스 패러독스 (형태 1)",
                        "Allais Form 2": "앨리스 패러독스 (형태 2)",
                        "Linda Conjunction": "린다 문제 (연접)",
                        "Linda -No Conjunction": "린다 문제 (비연접)",
                        "Myside German": "내 편향 (독일 관련)",
                        "Myside Ford": "내 편향 (포드 관련)",
                        "Probability Matching vs. Maximizing - Problem 1": "확률 매칭 vs 최대화 (문제 1)",
                        "Probability Matching vs. Maximizing - Problem 2": "확률 매칭 vs 최대화 (문제 2)",
                        "Less is More Gamble A": "덜이 더 효과 (게임 A)",
                        "Less is More Gamble B": "덜이 더 효과 (게임 B)",
                        "Less is More Gamble C": "덜이 더 효과 (게임 C)",
                        "Proportion Dominance 1A": "비율 지배 (1A)",
                        "Proportion Dominance 1B": "비율 지배 (1B)",
                        "Proportion Dominance 1C": "비율 지배 (1C)",
                        "Proportion Dominance 2A": "비율 지배 (2A)",
                        "Proportion Dominance 2B": "비율 지배 (2B)",
                        "Proportion Dominance 2C": "비율 지배 (2C)",
                        "WTA/WTP Thaler Problem - WTA Certainty": "지불의사/수용의사 (확실성)",
                        "WTA/WTP Thaler Problem - WTP Certainty": "지불의사/수용의사 (확실성)",
                        "WTA/WTP Thaler - WTP Noncertainty": "지불의사/수용의사 (불확실성)",
                        "Absolute vs. Relative - Calculator": "절대 vs 상대 (계산기)",
                        "Absolute vs. Relative - Jacket": "절대 vs 상대 (재킷)",
                        "Non-Experimental Heuristics and Biases": "비실험적 휴리스틱 및 편향",
                        "Forward Flow": "순방향 흐름"
                    }
                    
                    # 상위 10개 블록 표시
                    sorted_stats = sorted(block_stats.items(), key=lambda x: x[1]['presence_rate'], reverse=True)
                    
                    for i, (block_name, stat) in enumerate(sorted_stats[:10]):
                        description = block_descriptions.get(block_name, "심리학/행동경제학 실험")
                        
                        with st.expander(f"**{block_name}** ({stat['presence_rate']:.1f}%)", expanded=(i < 3)):
                            st.write(f"**설명**: {description}")
                            st.write(f"**참여자 수**: {stat['presence_count']:,}명")
                            if stat['avg_questions'] > 0:
                                st.write(f"**평균 질문 수**: {stat['avg_questions']:.1f}개")
                    
                    st.caption("💡 '응답자 선택' 페이지에서 블록 기반 필터링을 사용할 수 있습니다.")
                
                st.divider()
            
            if categorized:
                st.markdown("### 📂 데이터 카테고리 구성")
                st.markdown("응답자를 필터링할 때 사용할 수 있는 데이터 카테고리입니다.")
                st.markdown("")
                
                # 카테고리별 설명과 필드 수
                category_info = {
                    "인구통계": ("📊", "나이, 성별, 인종 등 기본 인구통계학적 정보"),
                    "직업경제": ("💼", "직업, 산업, 소득, 고용 상태 등"),
                    "교육": ("🎓", "학력, 전공, 학교 등 교육 관련 정보"),
                    "성격심리": ("🧠", "성격 특성, Big Five 지표 등"),
                    "경제특성": ("💰", "재정 상태, 자산, 소비 패턴 등"),
                    "라이프스타일": ("🏠", "취미, 관심사, 건강, 여가 활동 등"),
                    "지리위치": ("🌍", "거주지, 도시, 지역 등"),
                    "관계가족": ("❤️", "결혼 상태, 자녀, 가족 구성 등"),
                    "가치관태도": ("🎯", "설문 응답 데이터 (question_1~31)"),
                    "기술미디어": ("📱", "기술 사용, SNS, 디지털 리터러시 등"),
                    "기타": ("🔢", "기타 분류되지 않은 필드")
                }
                
                for category, fields in categorized.items():
                    emoji, description = category_info.get(category, ("📂", ""))
                    
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        
                        with col1:
                            st.markdown(f"**{emoji} {category}**")
                            st.caption(description)
                        
                        with col2:
                            st.metric("필드 수", len(fields))
                        
                        # 처음 5개 필드만 표시
                        with st.expander(f"필드 목록 보기 ({len(fields)}개)", expanded=False):
                            for i, field in enumerate(fields[:10], 1):
                                st.text(f"{i}. {field}")
                            if len(fields) > 10:
                                st.caption(f"... 외 {len(fields) - 10}개")
                
                st.divider()
                
                # 전체 통계
                total_fields = sum(len(f) for f in categorized.values())
                st.success(f"✅ 총 **{total_fields}개**의 필드로 응답자 필터링 가능")
            
            st.divider()
            
            # 샘플 페르소나 미리보기
            if st.session_state.loader.personas:
                st.markdown("### 👤 샘플 페르소나 데이터")
                st.caption("첫 번째 페르소나의 데이터 예시입니다.")
                
                sample_persona = st.session_state.loader.personas[0]
                
                # 실제 데이터에서 사용 가능한 필드 찾기
                available_fields = []
                for key, value in sample_persona.data.items():
                    if value and str(value).strip() and key not in ['persona_text', 'persona_summary', 'persona_json']:
                        available_fields.append(key)
                
                # 처음 10개 필드만 표시
                display_fields = available_fields[:10]
                
                if display_fields:
                    sample_data = {}
                    for field in display_fields:
                        value = sample_persona.data[field]
                        # 너무 긴 값은 잘라냄
                        if isinstance(value, str) and len(value) > 100:
                            value = value[:100] + "..."
                        sample_data[field] = value
                    
                    df_sample = pd.DataFrame([sample_data]).T
                    df_sample.columns = ['값']
                    st.dataframe(df_sample, use_container_width=True)
                    
                    if len(available_fields) > 10:
                        st.caption(f"총 {len(available_fields)}개 필드 중 처음 10개만 표시")
                else:
                    # 모든 데이터 표시 (너무 많을 수 있음)
                    st.info("주요 필드가 없어 전체 데이터를 표시합니다.")
                    all_data = {}
                    for key, value in sample_persona.data.items():
                        if value and str(value).strip():
                            if isinstance(value, str) and len(value) > 50:
                                value = value[:50] + "..."
                            all_data[key] = value
                    
                    if all_data:
                        df_all = pd.DataFrame([all_data]).T
                        df_all.columns = ['값']
                        st.dataframe(df_all, use_container_width=True)
                    else:
                        st.info("샘플 데이터를 표시할 수 없습니다.")
    
    # 도움말
    with st.expander("❓ 도움말", expanded=False):
        st.markdown("""
        ### 자주 묻는 질문
        
        **Q: API 비용은 얼마나 드나요?**  
        A: GPT-4o-mini 모델을 사용하여 비용을 최소화했습니다. 응답당 약 $0.001-0.002 정도입니다.
        
        **Q: 응답 시간은 얼마나 걸리나요?**  
        A: 응답자 1명당 약 1-2초가 소요됩니다. 지연 시간을 조절할 수 있습니다.
        
        **Q: 결과를 어떻게 저장하나요?**  
        A: '결과 보기' 페이지에서 JSON, CSV, Excel 형식으로 다운로드할 수 있습니다.
        
        **Q: 설문조사 템플릿을 재사용할 수 있나요?**  
        A: 예, 설문조사와 인터뷰 가이드를 JSON 파일로 저장/로드할 수 있습니다.
        """)
    
    st.divider()
    
    # 푸터
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>Powered by OpenAI GPT-4o-mini | Hugging Face Twin-2K-500</p>
        <p>🤖 LLM Customer Digital Twin System</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()



