"""
SurveyMonkey 스타일 설문 플랫폼
단계별로 리서치 계획 → 조사 대상 선택 → 설문 작성 → 결과 분석
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from digital_twin_survey_system import DigitalTwinSurveySystem
import os
import json
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

# Railway 환경변수에서 PORT 가져오기
port = int(os.environ.get("PORT", 8501))

# 페이지 설정
st.set_page_config(
    page_title="Digital Twin Survey Platform",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS 스타일
st.markdown("""
<style>
    /* 사이드바 완전히 숨기기 */
    .css-1d391kg {
        display: none !important;
    }
    
    /* 사이드바 버튼 숨기기 */
    [data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* 사이드바 토글 버튼 숨기기 */
    [data-testid="stSidebarToggler"] {
        display: none !important;
    }
    
    /* 사이드바 관련 모든 요소 숨기기 */
    button[kind="header"] {
        display: none !important;
    }
    
    /* 메인 콘텐츠 영역 전체 너비 사용 */
    .css-1lcbmhc, .css-1outpf7 {
        padding-left: 1rem !important;
        max-width: 100% !important;
    }
    
    /* 스크롤 영역 전체 너비 */
    .css-1v0mbdj {
        max-width: 100% !important;
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .step-card {
        background-color: #F3F4F6;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid #3B82F6;
    }
    .completed-step {
        border-left-color: #10B981;
        background-color: #ECFDF5;
    }
    .current-step {
        border-left-color: #F59E0B;
        background-color: #FEF3C7;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

def get_client_ip():
    """클라이언트 IP 주소 가져오기"""
    try:
        # Streamlit에서 IP 주소 가져오기
        headers = st.get_option("server.headers")
        if headers and 'X-Forwarded-For' in headers:
            return headers['X-Forwarded-For'].split(',')[0].strip()
        return "unknown"
    except:
        return "unknown"

def log_survey_activity(user_id, question_text, num_respondents, num_questions, estimated_cost):
    """설문 활동 로그 기록"""
    log_file = Path("logs") / "survey_logs.json"
    log_file.parent.mkdir(exist_ok=True)
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "ip_address": get_client_ip(),
        "question_text": question_text,
        "num_respondents": num_respondents,
        "num_questions": num_questions,
        "estimated_cost": estimated_cost
    }
    
    # 기존 로그 로드
    if log_file.exists():
        with open(log_file, 'r', encoding='utf-8') as f:
            logs = json.load(f)
    else:
        logs = []
    
    # 새 로그 추가
    logs.append(log_entry)
    
    # 로그 저장
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

def initialize_system(api_key):
    """시스템 초기화"""
    try:
        system = DigitalTwinSurveySystem(api_key=api_key)
        system.load_dataset()
        return system
    except Exception as e:
        st.error(f"시스템 초기화 오류: {e}")
        return None

def show_admin_page():
    """관리자 페이지"""
    st.markdown('<p style="font-size: 0.9rem; color: #6B7280; text-align: center; margin-bottom: 0.5rem;">LLM Customer Digital Twin</p>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">🔐 관리자 페이지</h1>', unsafe_allow_html=True)
    
    log_file = Path("logs") / "survey_logs.json"
    
    if not log_file.exists():
        st.info("아직 로그가 없습니다.")
        return
    
    # 로그 로드
    with open(log_file, 'r', encoding='utf-8') as f:
        logs = json.load(f)
    
    if not logs:
        st.info("아직 로그가 없습니다.")
        return
    
    # 통계 표시
    df = pd.DataFrame(logs)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("총 설문 수", len(df))
    
    with col2:
        total_respondents = df['num_respondents'].sum()
        st.metric("총 응답자 수", f"{total_respondents:,}명")
    
    with col3:
        total_cost = df['estimated_cost'].sum()
        st.metric("총 예상 비용", f"${total_cost:.2f}")
    
    with col4:
        unique_users = df['user_id'].nunique()
        st.metric("사용자 수", f"{unique_users}명")
    
    st.markdown("---")
    
    # 로그 테이블
    st.markdown("### 상세 로그")
    
    # IP별 통계
    st.markdown("#### IP별 사용 통계")
    ip_stats = df.groupby('ip_address').agg({
        'num_respondents': 'sum',
        'estimated_cost': 'sum',
        'timestamp': 'count'
    }).reset_index()
    ip_stats.columns = ['IP 주소', '총 응답자 수', '총 비용', '설문 수']
    st.dataframe(ip_stats, use_container_width=True)
    
    st.markdown("---")
    
    # 전체 로그
    st.markdown("#### 전체 활동 로그")
    
    # 데이터프레임 변환 및 정렬
    display_df = df[['timestamp', 'user_id', 'ip_address', 'question_text', 'num_respondents', 'num_questions', 'estimated_cost']].copy()
    display_df.columns = ['시간', '사용자', 'IP 주소', '질문', '응답자 수', '질문 수', '예상 비용']
    display_df = display_df.sort_values('시간', ascending=False)
    
    st.dataframe(display_df, use_container_width=True)
    
    # 다운로드 버튼
    st.markdown("---")
    csv = display_df.to_csv(index=False, encoding='utf-8-sig')
    st.download_button(
        label="📥 로그 다운로드 (CSV)",
        data=csv,
        file_name=f"survey_logs_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )

def reset_session_state():
    """세션 상태 초기화"""
    keys_to_reset = [
        'research_title', 'research_objective', 'step', 'selected_personas',
        'survey_questions', 'survey_results', 'current_question'
    ]
    for key in keys_to_reset:
        if key in st.session_state:
            del st.session_state[key]

def render_step_indicator(current_step):
    """단계 표시기"""
    steps = [
        ("1", "리서치 계획", "🔬"),
        ("2", "조사 대상 선택", "👥"),
        ("3", "설문 작성", "📝"),
        ("4", "결과 분석", "📊")
    ]
    
    cols = st.columns(4)
    for idx, (num, name, icon) in enumerate(steps):
        with cols[idx]:
            if idx < current_step:
                st.markdown(f"""
                <div class="step-card completed-step">
                    <h3>{icon} {num}</h3>
                    <p style="font-weight: bold; color: #10B981;">{name}</p>
                    <p style="font-size: 0.8rem; color: #059669;">✓ 완료</p>
                </div>
                """, unsafe_allow_html=True)
            elif idx == current_step:
                st.markdown(f"""
                <div class="step-card current-step">
                    <h3>{icon} {num}</h3>
                    <p style="font-weight: bold; color: #F59E0B;">{name}</p>
                    <p style="font-size: 0.8rem; color: #D97706;">진행 중</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="step-card">
                    <h3>{icon} {num}</h3>
                    <p style="font-weight: bold; color: #6B7280;">{name}</p>
                    <p style="font-size: 0.8rem; color: #9CA3AF;">대기 중</p>
                </div>
                """, unsafe_allow_html=True)

def step1_research_planning(system):
    """1단계: 리서치 계획"""
    st.markdown("## 🔬 1단계: 리서치 계획")
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 리서치 기본 정보")
        
        research_title = st.text_input(
            "📌 리서치 제목",
            value=st.session_state.get('research_title', ''),
            placeholder="예: AI 도구 사용 만족도 조사"
        )
        
        research_objective = st.text_area(
            "🎯 리서치 목적",
            value=st.session_state.get('research_objective', ''),
            placeholder="이 리서치를 통해 무엇을 알아보고 싶으신가요?",
            height=100
        )
        
        st.session_state['research_title'] = research_title
        st.session_state['research_objective'] = research_objective
    
    with col2:
        st.markdown("### 데이터셋 정보")
        
        # 인구통계 데이터 정의
        demographics_data = {
            "Region": [
                ("South", 834, 40.5),
                ("West", 494, 24.0),
                ("Midwest", 372, 18.1),
                ("Northeast", 342, 16.6),
                ("Pacific", 16, 0.8)
            ],
            "Sex": [
                ("Female", 1044, 50.7),
                ("Male", 1014, 49.3)
            ],
            "Age": [
                ("18-29", 388, 18.9),
                ("30-49", 735, 35.7),
                ("50-64", 658, 32.0),
                ("65+", 277, 13.5)
            ],
            "Education": [
                ("Less than high school", 17, 0.8),
                ("High school graduate", 272, 13.2),
                ("Some college, no degree", 468, 22.7),
                ("Associate's degree", 253, 12.3),
                ("College graduate/some postgrad", 735, 35.7),
                ("Postgraduate", 313, 15.2)
            ],
            "Race": [
                ("White", 1361, 66.1),
                ("Black", 251, 12.2),
                ("Hispanic", 194, 9.4),
                ("Asian", 140, 6.8),
                ("Other", 112, 5.4)
            ],
            "Citizenship": [
                ("Yes", 2054, 99.8),
                ("No", 4, 0.2)
            ],
            "Marital Status": [
                ("Married", 813, 39.5),
                ("Never been married", 714, 34.7),
                ("Divorced", 218, 10.6),
                ("Living with a partner", 212, 10.3),
                ("Widowed", 70, 3.4),
                ("Separated", 31, 1.5)
            ],
            "Religion": [
                ("Protestant", 510, 24.8),
                ("Roman Catholic", 358, 17.4),
                ("Nothing in particular", 327, 15.9),
                ("Agnostic", 311, 15.1),
                ("Atheist", 216, 10.5),
                ("Other", 215, 10.4),
                ("Jewish", 39, 1.9),
                ("Buddhist", 25, 1.2),
                ("Muslim", 18, 0.9),
                ("Orthodox", 17, 0.8),
                ("Mormon", 15, 0.7),
                ("Hindu", 7, 0.3)
            ],
            "Religious Attendance": [
                ("Never", 838, 40.7),
                ("Seldom", 463, 22.5),
                ("Once a week", 295, 14.3),
                ("A few times a year", 246, 12.0),
                ("Once or twice a month", 129, 6.3),
                ("More than once a week", 87, 4.2)
            ],
            "Political Party": [
                ("Democrat", 847, 41.2),
                ("Independent", 609, 29.6),
                ("Republican", 540, 26.2),
                ("Something else", 62, 3.0)
            ],
            "Household Income": [
                ("Less than $30,000", 367, 17.9),
                ("$30,000-$50,000", 412, 20.0),
                ("$50,000-$75,000", 411, 20.0),
                ("$75,000-$100,000", 316, 15.4),
                ("$100,000 or more", 552, 26.8)
            ],
            "Political Ideology": [
                ("Moderate", 582, 28.3),
                ("Liberal", 564, 27.4),
                ("Conservative", 430, 20.9),
                ("Very liberal", 345, 16.8),
                ("Very conservative", 137, 6.7)
            ],
            "Household Size": [
                ("1", 412, 20.0),
                ("2", 650, 31.6),
                ("3", 423, 20.6),
                ("4", 352, 17.1),
                ("More than 4", 221, 10.7)
            ],
            "Employment Status": [
                ("Full-time employment", 871, 42.3),
                ("Self-employed", 280, 13.6),
                ("Part-time employment", 269, 13.1),
                ("Unemployed", 249, 12.1),
                ("Retired", 245, 11.9),
                ("Student", 78, 3.8),
                ("Home-maker", 66, 3.2)
            ]
        }
        
        st.info(f"""
        **미국 소비자 디지털 트윈 데이터**
        
        - 총 페르소나: **2,058명**
        - [논문 보기](https://arxiv.org/abs/2505.17479)
        """)
        
        # 인구통계 데이터 상세 표시 (expander)
        with st.expander("📊 데이터 상세 보기", expanded=False):
            st.markdown("### Demographic characteristics of sample")
            
            for category, data in demographics_data.items():
                st.markdown(f"#### {category}")
                df = pd.DataFrame(data, columns=["Category", "Count", "Percentage"])
                df['Percentage'] = df['Percentage'].apply(lambda x: f"{x}%")
                st.dataframe(df, use_container_width=True, hide_index=True)
                st.markdown("---")
    
    # 다음 단계로 이동
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("다음 단계: 조사 대상 선택 →", type="primary", use_container_width=True):
            if research_title and research_objective:
                st.session_state['step'] = 2
                st.rerun()
            else:
                st.warning("리서치 제목과 목적을 입력해주세요.")

def calculate_estimated_cost(num_respondents, num_questions):
    """예상 비용 계산"""
    # OpenAI API 비용 (GPT-4 기준)
    # Input: $0.03 per 1K tokens
    # Output: $0.06 per 1K tokens
    
    # 평균 토큰 수 추정
    avg_input_tokens_per_question = 200  # 질문당 입력 토큰
    avg_output_tokens_per_question = 50  # 질문당 출력 토큰
    
    # 총 토큰 수 계산
    total_input_tokens = num_respondents * num_questions * avg_input_tokens_per_question
    total_output_tokens = num_respondents * num_questions * avg_output_tokens_per_question
    
    # 비용 계산
    input_cost = (total_input_tokens / 1000) * 0.03
    output_cost = (total_output_tokens / 1000) * 0.06
    total_cost = input_cost + output_cost
    
    return {
        'input_tokens': total_input_tokens,
        'output_tokens': total_output_tokens,
        'input_cost': input_cost,
        'output_cost': output_cost,
        'total_cost': total_cost
    }

def step2_audience_selection(system):
    """2단계: 조사 대상 선택"""
    st.markdown("## 👥 2단계: 조사 대상 선택")
    st.markdown("---")
    
    # 필터링 옵션
    st.markdown("### 인구통계학적 필터")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 기본 정보")
        
        # 연령대
        age_options = ["18-29", "30-49", "50-64", "65+"]
        selected_ages = st.multiselect(
            "연령대",
            options=age_options,
            default=age_options,
            key="age_select"
        )
        
        # 성별
        gender_options = ["Male", "Female"]
        selected_genders = st.multiselect(
            "성별",
            options=gender_options,
            default=gender_options,
            key="gender_select"
        )
    
    with col2:
        st.markdown("#### 지역")
        
        location_options = ["South", "West", "Midwest", "Northeast", "Pacific"]
        selected_locations = st.multiselect(
            "지역",
            options=location_options,
            default=location_options,
            key="location_select"
        )
        
        # 교육 수준
        education_options = [
            "Less than high school", "High school graduate", 
            "Some college, no degree", "Associate's degree",
            "College graduate/some postgrad", "Postgraduate"
        ]
        selected_educations = st.multiselect(
            "교육 수준",
            options=education_options,
            default=education_options,
            key="education_select"
        )
    
    # 샘플 크기
    st.markdown("---")
    st.markdown("### 샘플 크기")
    max_respondents = st.slider(
        "선택할 응답자 수",
        1, len(system.dataset['data']), 50,
        key="max_respondents"
    )
    
    # 예상 비용 표시 (질문 수가 있는 경우)
    if 'survey_questions' in st.session_state and len(st.session_state.get('survey_questions', [])) > 0:
        num_questions = len(st.session_state['survey_questions'])
        cost_info = calculate_estimated_cost(max_respondents, num_questions)
        
        st.success(f"""
        💰 **예상 비용**: {max_respondents}명 × {num_questions}개 질문 = **${cost_info['total_cost']:.2f}**
        """)
    
    # 필터링 실행
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔍 필터링 실행", type="primary", use_container_width=True):
            criteria = {
                'age_ranges': selected_ages,
                'genders': selected_genders,
                'locations': selected_locations,
                'educations': selected_educations
            }
            
            selected_indices = system.select_personas_by_criteria(criteria)
            
            if selected_indices:
                # 샘플 크기 조정
                if len(selected_indices) > max_respondents:
                    import random
                    selected_indices = random.sample(selected_indices, max_respondents)
                
                st.session_state['selected_personas'] = selected_indices
                st.success(f"✅ {len(selected_indices)}명의 조사 대상이 선택되었습니다!")
                
                # 선택된 대상 요약
                with st.expander("선택된 조사 대상 요약"):
                    display_audience_summary(system, selected_indices)
            else:
                st.warning("선택된 조건에 맞는 조사 대상이 없습니다.")
    
    # 이전/다음 단계
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← 이전 단계", use_container_width=True):
            st.session_state['step'] = 1
            st.rerun()
    with col3:
        if st.button("다음 단계: 설문 작성 →", type="primary", use_container_width=True):
            if 'selected_personas' in st.session_state:
                st.session_state['step'] = 3
                st.rerun()
            else:
                st.warning("먼저 조사 대상을 선택해주세요.")

def display_audience_summary(system, selected_indices):
    """조사 대상 요약 표시"""
    # 통계 계산
    age_dist = {"18-29": 0, "30-49": 0, "50-64": 0, "65+": 0}
    gender_dist = {"Male": 0, "Female": 0}
    
    for idx in selected_indices:
        row = system.dataset['data'][idx]
        summary = row.get('persona_summary', '')
        
        if "Age: 18-29" in summary:
            age_dist["18-29"] += 1
        elif "Age: 30-49" in summary:
            age_dist["30-49"] += 1
        elif "Age: 50-64" in summary:
            age_dist["50-64"] += 1
        elif "Age: 65+" in summary:
            age_dist["65+"] += 1
        
        if "Gender: Male" in summary:
            gender_dist["Male"] += 1
        elif "Gender: Female" in summary:
            gender_dist["Female"] += 1
    
    # 통계 표시
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**연령 분포**")
        for age, count in age_dist.items():
            if count > 0:
                percentage = (count / len(selected_indices)) * 100
                st.write(f"• {age}: {count}명 ({percentage:.1f}%)")
    
    with col2:
        st.markdown("**성별 분포**")
        for gender, count in gender_dist.items():
            if count > 0:
                percentage = (count / len(selected_indices)) * 100
                st.write(f"• {gender}: {count}명 ({percentage:.1f}%)")

def step3_survey_creation(system):
    """3단계: 설문 작성"""
    st.markdown("## 📝 3단계: 설문 작성")
    st.markdown("---")
    
    # 예상 비용 표시
    if 'selected_personas' in st.session_state and 'survey_questions' in st.session_state and st.session_state['survey_questions']:
        num_respondents = len(st.session_state['selected_personas'])
        num_questions = len(st.session_state['survey_questions'])
        cost_info = calculate_estimated_cost(num_respondents, num_questions)
        
        st.info(f"""
        💰 **예상 비용**
        - 조사 대상: {num_respondents}명
        - 질문 수: {num_questions}개
        - 예상 총 비용: **${cost_info['total_cost']:.2f}**
        - 입력 토큰: {cost_info['input_tokens']:,} 토큰 (${cost_info['input_cost']:.2f})
        - 출력 토큰: {cost_info['output_tokens']:,} 토큰 (${cost_info['output_cost']:.2f})
        """)
        st.markdown("---")
    
    # 질문 작성
    st.markdown("### 설문 질문 작성")
    
    if 'survey_questions' not in st.session_state:
        st.session_state['survey_questions'] = []
    
    # 질문 리스트
    st.markdown("#### 작성된 질문")
    if st.session_state['survey_questions']:
        for idx, q in enumerate(st.session_state['survey_questions']):
            with st.expander(f"질문 {idx+1}: {q['question']}"):
                st.write(f"**척도**: {q['scale']}")
                if st.button(f"삭제", key=f"delete_{idx}"):
                    st.session_state['survey_questions'].pop(idx)
                    st.rerun()
    else:
        st.info("아직 질문이 없습니다. 아래에서 질문을 추가하세요.")
    
    st.markdown("---")
    
    # 새 질문 추가
    st.markdown("#### 새 질문 추가")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        new_question = st.text_input(
            "질문 내용",
            placeholder="예: 현재 직업에 대한 만족도는 어느 정도인가요?",
            key="new_question"
        )
    
    with col2:
        scale = st.selectbox(
            "척도",
            ["1-7", "1-5", "1-10"],
            key="new_scale"
        )
    
    if st.button("질문 추가", type="primary"):
        if new_question:
            st.session_state['survey_questions'].append({
                'question': new_question,
                'scale': scale,
                'type': 'likert'
            })
            st.success("질문이 추가되었습니다!")
            st.rerun()
        else:
            st.warning("질문 내용을 입력해주세요.")
    
    # 샘플 질문
    st.markdown("---")
    st.markdown("#### 샘플 질문 사용")
    if st.button("샘플 질문 로드"):
        st.session_state['survey_questions'] = [
            {
                "question": "How satisfied are you with your current job? (1=very dissatisfied, 7=very satisfied)",
                "scale": "1-7",
                "type": "likert"
            },
            {
                "question": "How likely are you to recommend AI tools to colleagues? (1=not at all, 7=very likely)",
                "scale": "1-7",
                "type": "likert"
            },
            {
                "question": "Rate your work-life balance (1=very poor, 7=excellent)",
                "scale": "1-7",
                "type": "likert"
            }
        ]
        st.rerun()
    
    # 설문 실행
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← 이전 단계", use_container_width=True):
            st.session_state['step'] = 2
            st.rerun()
    
    with col3:
        if st.button("설문 실행 →", type="primary", use_container_width=True):
            if st.session_state['survey_questions'] and 'selected_personas' in st.session_state:
                with st.spinner("설문을 실행하는 중..."):
                    questions = st.session_state['survey_questions']
                    selected_indices = st.session_state['selected_personas']
                    
                    # 설문 실행
                    survey = system.create_survey(questions)
                    results = system.conduct_survey(survey, selected_indices)
                    
                    if results is not None and not results.empty:
                        st.session_state['survey_results'] = [results]
                        st.session_state['step'] = 4
                        
                        # 로그 기록
                        num_respondents = len(selected_indices)
                        num_questions = len(questions)
                        cost_info = calculate_estimated_cost(num_respondents, num_questions)
                        question_text = ", ".join([q['question'] for q in questions])
                        
                        log_survey_activity(
                            user_id=st.session_state.get('user_id', 'anonymous'),
                            question_text=question_text,
                            num_respondents=num_respondents,
                            num_questions=num_questions,
                            estimated_cost=cost_info['total_cost']
                        )
                        
                        st.success("설문이 완료되었습니다!")
                        st.rerun()
            else:
                st.warning("질문을 추가하고 조사 대상을 선택해주세요.")

def step4_results_analysis(system):
    """4단계: 결과 분석"""
    st.markdown("## 📊 4단계: 결과 분석")
    st.markdown("---")
    
    if 'survey_results' not in st.session_state or not st.session_state['survey_results']:
        st.warning("아직 설문 결과가 없습니다.")
        if st.button("설문 작성으로 돌아가기"):
            st.session_state['step'] = 3
            st.rerun()
        return
    
    # 리서치 정보 요약
    st.markdown("### 리서치 요약")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("조사 대상", f"{len(st.session_state['selected_personas'])}명")
    
    with col2:
        st.metric("질문 수", f"{len(st.session_state['survey_questions'])}개")
    
    with col3:
        if st.session_state['survey_results']:
            df = st.session_state['survey_results'][0]
            # 숫자형 컬럼만 선택
            numeric_cols = [col for col in df.columns if col.startswith('Q') and df[col].dtype in ['int64', 'float64']]
            if numeric_cols:
                avg_score = df[numeric_cols].mean().mean()
                st.metric("평균 점수", f"{avg_score:.2f}")
            else:
                st.metric("평균 점수", "N/A")
    
    st.markdown("---")
    
    # 질문별 분석
    st.markdown("### 질문별 상세 분석")
    
    for idx, df in enumerate(st.session_state['survey_results']):
        st.markdown(f"#### 설문 {idx+1}")
        
        # 질문별 통계 (숫자형 컬럼만)
        question_cols = [col for col in df.columns if col.startswith('Q') and df[col].dtype in ['int64', 'float64']]
        
        for col in question_cols:
            # 질문 텍스트 찾기
            question_text = f"{col}"
            if 'survey_questions' in st.session_state:
                question_idx = int(col.replace('Q', '')) - 1
                if 0 <= question_idx < len(st.session_state['survey_questions']):
                    question_text = st.session_state['survey_questions'][question_idx]['question']
            
            with st.expander(f"📋 {question_text[:80]}{'...' if len(question_text) > 80 else ''}"):
                responses = df[col].dropna()
                
                if len(responses) > 0:
                    # 전체 질문 텍스트 표시
                    st.markdown(f"**질문**: {question_text}")
                    st.markdown("---")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.markdown("**통계 정보**")
                        stats = {
                            '평균': f"{responses.mean():.2f}",
                            '중앙값': f"{responses.median():.1f}",
                            '표준편차': f"{responses.std():.2f}",
                            '최소값': f"{int(responses.min())}",
                            '최대값': f"{int(responses.max())}"
                        }
                        
                        for key, value in stats.items():
                            st.write(f"• **{key}**: {value}")
                    
                    with col2:
                        st.markdown("**응답 분포**")
                        fig = px.histogram(
                            df, 
                            x=col,
                            nbins=7,
                            color_discrete_sequence=['#3B82F6']
                        )
                        fig.update_layout(
                            xaxis_title="응답 점수",
                            yaxis_title="응답자 수",
                            showlegend=False
                        )
                        st.plotly_chart(fig, use_container_width=True)
    
    # 다운로드
    st.markdown("---")
    st.markdown("### 결과 다운로드")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.session_state['survey_results']:
            csv = st.session_state['survey_results'][0].to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 CSV 다운로드",
                data=csv,
                file_name=f"survey_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
    
    # 새로운 리서치 시작
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("새로운 리서치 시작", type="primary", use_container_width=True):
            reset_session_state()
            st.session_state['step'] = 1
            st.rerun()

def main():
    """메인 애플리케이션"""
    # 로그인 체크
    if 'authenticated' not in st.session_state:
        st.session_state['authenticated'] = False
    
    # 페이지 설정
    if 'page' not in st.session_state:
        st.session_state['page'] = 'main'
    
    # 로그인 페이지
    if not st.session_state['authenticated']:
        show_login_page()
        return
    
    # 관리자 페이지
    if st.session_state['page'] == 'admin':
        show_admin_page()
        # 관리자 페이지에서 돌아가기 버튼
        if st.button("← 메인으로 돌아가기"):
            st.session_state['page'] = 'main'
            st.rerun()
        return
    
    # 메인 페이지
    show_main_page()

def show_login_page():
    """로그인 페이지"""
    st.markdown('<p style="font-size: 0.9rem; color: #6B7280; text-align: center; margin-bottom: 0.5rem;">LLM Customer Digital Twin</p>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">📊 美 디지털 트윈 소비자 조사</h1>', unsafe_allow_html=True)
    
    # 로그인 폼
    st.markdown("---")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("### 로그인")
        
        user_id = st.text_input("아이디", key="login_id")
        user_pw = st.text_input("비밀번호", type="password", key="login_pw")
        
        login_button = st.button("로그인", type="primary", use_container_width=True)
        
        if login_button:
            # 환경 변수에서 인증 정보 가져오기
            auth_user_id = os.getenv("AUTH_USER_ID")
            auth_user_pw = os.getenv("AUTH_USER_PW")
            auth_admin_id = os.getenv("AUTH_ADMIN_ID")
            auth_admin_pw = os.getenv("AUTH_ADMIN_PW")
            if not all([auth_user_id, auth_user_pw, auth_admin_id, auth_admin_pw]):
                st.error("인증 정보가 설정되지 않았습니다. 환경 변수를 확인하세요.")
                st.stop()
            
            # 일반 사용자 로그인
            if user_id == auth_user_id and user_pw == auth_user_pw:
                st.session_state['authenticated'] = True
                st.session_state['user_role'] = 'user'
                st.rerun()
            # 관리자 로그인
            elif user_id == auth_admin_id and user_pw == auth_admin_pw:
                st.session_state['authenticated'] = True
                st.session_state['user_role'] = 'admin'
                st.session_state['page'] = 'admin'
                st.rerun()
            else:
                st.error("아이디 또는 비밀번호가 올바르지 않습니다.")

def show_main_page():
    """메인 페이지"""
    # 헤더
    st.markdown('<p style="font-size: 0.9rem; color: #6B7280; text-align: center; margin-bottom: 0.5rem;">LLM Customer Digital Twin</p>', unsafe_allow_html=True)
    st.markdown('<h1 class="main-header">📊 美 디지털 트윈 소비자 조사</h1>', unsafe_allow_html=True)
    st.markdown("**미국 소비자 디지털 트윈 데이터를 활용한 단계별 설문조사 플랫폼**")
    
    # 사용자 정보 및 설정 (메인 화면으로 이동)
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col2:
        user_role = st.session_state.get('user_role', 'user')
        if user_role == 'admin':
            st.success("👤 관리자 모드")
        else:
            st.info("👤 일반 사용자 모드")
    
    with col3:
        if st.button("로그아웃"):
            st.session_state['authenticated'] = False
            reset_session_state()
            st.rerun()
    
    # 관리자 페이지 버튼 (관리자만 접근 가능)
    if user_role == 'admin':
        col1, col2, col3 = st.columns([2, 1, 1])
        with col2:
            if st.button("🔐 관리자 페이지", use_container_width=True):
                st.session_state['page'] = 'admin'
                st.rerun()
    
    st.markdown("---")
    
    # API 키 (환경 변수에서 가져오기)
    api_key = os.getenv("OPENAI_API_KEY")
    
    # Railway나 로컬에서 환경 변수가 설정되지 않은 경우
    if not api_key:
        st.warning("⚠️ OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")
        st.info("""
        **해결 방법:**
        1. Railway 프로젝트 설정에서 환경 변수 추가
        2. 로컬 실행 시 .env 파일 생성
        """)
        st.stop()
    
    os.environ["OPENAI_API_KEY"] = api_key
    
    # 시스템 초기화
    try:
        system = initialize_system(api_key)
        if not system:
            st.error("시스템 초기화에 실패했습니다.")
            st.stop()
    except Exception as e:
        st.error(f"시스템 초기화 오류: {str(e)}")
        st.stop()
    
    # 단계 설정
    if 'step' not in st.session_state:
        st.session_state['step'] = 1
    
    # 단계 표시기
    render_step_indicator(st.session_state['step'] - 1)
    
    st.markdown("---")
    
    # 단계별 페이지
    if st.session_state['step'] == 1:
        step1_research_planning(system)
    elif st.session_state['step'] == 2:
        step2_audience_selection(system)
    elif st.session_state['step'] == 3:
        step3_survey_creation(system)
    elif st.session_state['step'] == 4:
        step4_results_analysis(system)

if __name__ == "__main__":
    main()

