"""
설문조사 페이지
"""

import os
import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime
from src.survey_system import Survey, SurveyQuestion
from src.results_manager import ResultsManager

st.set_page_config(page_title="설문조사", page_icon="📊", layout="wide")

st.title("📊 설문조사 시스템")
st.markdown("구조화된 설문조사를 생성하고 진행하세요.")

# 세션 상태 자동 초기화
if 'loader' not in st.session_state:
    st.session_state.loader = None
if 'ai_agent' not in st.session_state:
    st.session_state.ai_agent = None
if 'selected_personas' not in st.session_state:
    st.session_state.selected_personas = []
if 'api_key' not in st.session_state:
    st.session_state.api_key = os.getenv("OPENAI_API_KEY", "")

# 자동 초기화 시도
if st.session_state.ai_agent is None:
    st.warning("⚠️ 시스템을 초기화하는 중...")
    try:
        from src.dataset_loader import DatasetLoader
        from src.ai_agent import AIAgent
        
        if st.session_state.loader is None:
            with st.spinner("데이터셋 로딩 중..."):
                loader = DatasetLoader()
                loader.load()
                st.session_state.loader = loader
        
        with st.spinner("AI 에이전트 초기화 중..."):
            agent = AIAgent(api_key=st.session_state.api_key)
            st.session_state.ai_agent = agent
        
        st.success("✅ 시스템 초기화 완료!")
        st.rerun()
    except Exception as e:
        st.error(f"❌ 시스템 초기화 실패: {e}")
        st.info("👈 홈페이지로 이동하여 수동으로 초기화하세요.")
        st.stop()

if not st.session_state.selected_personas:
    st.warning("⚠️ 먼저 응답자를 선택해주세요.")
    st.page_link("pages/1_📋_응답자_선택.py", label="응답자 선택하러 가기", icon="📋")
    st.stop()

# 현재 설문 상태 초기화
if 'current_survey' not in st.session_state:
    st.session_state.current_survey = None

if 'survey_questions' not in st.session_state:
    st.session_state.survey_questions = []

st.divider()

# 탭 구성
tab1, tab2, tab3 = st.tabs(["📝 설문 작성", "▶️ 설문 진행", "📈 결과 보기"])

# 탭 1: 설문 작성
with tab1:
    st.markdown("## 📝 설문조사 작성")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # 새 설문 vs 템플릿 로드
        creation_mode = st.radio(
            "설문조사 생성 방법",
            ["새로 만들기", "템플릿 불러오기"],
            horizontal=True
        )
    
    with col2:
        if st.button("🔄 초기화"):
            st.session_state.current_survey = None
            st.session_state.survey_questions = []
            st.rerun()
    
    st.divider()
    
    if creation_mode == "새로 만들기":
        # 설문조사 기본 정보
        st.markdown("### 기본 정보")
        
        survey_title = st.text_input(
            "설문조사 제목*",
            placeholder="예: 기술 수용도 조사",
            value=st.session_state.current_survey.title if st.session_state.current_survey else ""
        )
        
        survey_description = st.text_area(
            "설명 (선택사항)",
            placeholder="설문조사에 대한 간단한 설명을 입력하세요.",
            value=st.session_state.current_survey.description if st.session_state.current_survey else ""
        )
        
        st.divider()
        
        # 질문 추가
        st.markdown("### 질문 관리")
        
        with st.expander("➕ 새 질문 추가", expanded=True):
            q_text = st.text_area(
                "질문 내용*",
                placeholder="예: 나는 AI 기술이 사회에 긍정적인 영향을 미칠 것이라고 생각한다.",
                key="new_question_text"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                q_scale = st.text_input(
                    "척도 설명",
                    value="1(전혀 동의하지 않음) ~ 7(매우 동의함)",
                    key="new_question_scale"
                )
            
            with col2:
                q_category = st.text_input(
                    "카테고리 (선택사항)",
                    placeholder="예: 긍정적 태도",
                    key="new_question_category"
                )
            
            if st.button("➕ 질문 추가", type="primary"):
                if q_text.strip():
                    question = {
                        'id': f"Q{len(st.session_state.survey_questions) + 1}",
                        'text': q_text,
                        'scale': q_scale,
                        'category': q_category if q_category else None
                    }
                    st.session_state.survey_questions.append(question)
                    st.success(f"✅ 질문이 추가되었습니다! (총 {len(st.session_state.survey_questions)}개)")
                    st.rerun()
                else:
                    st.error("❌ 질문 내용을 입력해주세요.")
        
        # 현재 질문 목록
        if st.session_state.survey_questions:
            st.markdown(f"### 📋 질문 목록 ({len(st.session_state.survey_questions)}개)")
            
            for i, q in enumerate(st.session_state.survey_questions):
                with st.expander(f"{q['id']}: {q['text'][:50]}...", expanded=False):
                    st.markdown(f"**질문:** {q['text']}")
                    st.markdown(f"**척도:** {q['scale']}")
                    if q['category']:
                        st.markdown(f"**카테고리:** {q['category']}")
                    
                    if st.button(f"🗑️ 삭제", key=f"delete_{i}"):
                        st.session_state.survey_questions.pop(i)
                        st.rerun()
            
            # 설문 저장
            st.divider()
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("💾 설문조사 생성", type="primary", use_container_width=True):
                    if survey_title.strip():
                        survey = Survey(survey_title, survey_description)
                        for q in st.session_state.survey_questions:
                            survey.add_question(
                                text=q['text'],
                                question_id=q['id'],
                                scale_description=q['scale'],
                                category=q['category']
                            )
                        st.session_state.current_survey = survey
                        st.success("✅ 설문조사가 생성되었습니다!")
                    else:
                        st.error("❌ 설문조사 제목을 입력해주세요.")
            
            with col2:
                # 템플릿 저장
                if st.button("📥 템플릿으로 저장", use_container_width=True):
                    if survey_title.strip() and st.session_state.survey_questions:
                        template = {
                            'title': survey_title,
                            'description': survey_description,
                            'questions': [
                                {
                                    'question_id': q['id'],
                                    'text': q['text'],
                                    'scale_description': q['scale'],
                                    'category': q['category']
                                }
                                for q in st.session_state.survey_questions
                            ]
                        }
                        
                        # JSON 다운로드
                        st.download_button(
                            label="💾 JSON 다운로드",
                            data=json.dumps(template, ensure_ascii=False, indent=2),
                            file_name=f"{survey_title.replace(' ', '_')}_template.json",
                            mime="application/json"
                        )
        else:
            st.info("💡 위에서 질문을 추가하세요.")
    
    else:  # 템플릿 불러오기
        st.markdown("### 📂 템플릿 불러오기")
        
        uploaded_file = st.file_uploader(
            "설문조사 템플릿 파일 (JSON)",
            type=['json'],
            help="이전에 저장한 설문조사 템플릿을 업로드하세요."
        )
        
        if uploaded_file is not None:
            try:
                template = json.load(uploaded_file)
                
                st.success("✅ 템플릿을 불러왔습니다!")
                
                st.markdown(f"**제목:** {template['title']}")
                st.markdown(f"**설명:** {template.get('description', 'N/A')}")
                st.markdown(f"**질문 수:** {len(template['questions'])}개")
                
                # 미리보기
                with st.expander("질문 미리보기"):
                    for q in template['questions']:
                        st.markdown(f"**{q['question_id']}:** {q['text']}")
                
                if st.button("✅ 이 템플릿 사용", type="primary"):
                    survey = Survey(template['title'], template.get('description', ''))
                    
                    st.session_state.survey_questions = []
                    
                    for q in template['questions']:
                        survey.add_question(
                            text=q['text'],
                            question_id=q.get('question_id'),
                            scale_description=q.get('scale_description', "1(전혀 동의하지 않음) ~ 7(매우 동의함)"),
                            category=q.get('category')
                        )
                        
                        st.session_state.survey_questions.append({
                            'id': q.get('question_id', f"Q{len(st.session_state.survey_questions) + 1}"),
                            'text': q['text'],
                            'scale': q.get('scale_description', "1(전혀 동의하지 않음) ~ 7(매우 동의함)"),
                            'category': q.get('category')
                        })
                    
                    st.session_state.current_survey = survey
                    st.rerun()
            
            except Exception as e:
                st.error(f"❌ 템플릿 로드 실패: {e}")
        
        # 예제 템플릿 다운로드
        st.divider()
        st.markdown("### 📄 예제 템플릿")
        
        with open("examples/survey_template.json", "r", encoding="utf-8") as f:
            example_template = f.read()
        
        st.download_button(
            label="📥 예제 템플릿 다운로드",
            data=example_template,
            file_name="survey_template_example.json",
            mime="application/json"
        )

# 탭 2: 설문 진행
with tab2:
    st.markdown("## ▶️ 설문조사 진행")
    
    if not st.session_state.current_survey:
        st.warning("⚠️ 먼저 설문조사를 작성하거나 불러와주세요.")
    else:
        survey = st.session_state.current_survey
        
        # 설문 정보 표시
        st.info(f"**설문조사:** {survey.title}")
        st.info(f"**응답자:** {len(st.session_state.selected_personas)}명")
        st.info(f"**질문:** {len(survey.questions)}개")
        st.info(f"**총 응답:** {len(st.session_state.selected_personas) * len(survey.questions)}개")
        
        # 예상 시간 및 비용
        total_responses = len(st.session_state.selected_personas) * len(survey.questions)
        estimate_time = total_responses * 1.5 / 60  # 분
        estimate_cost = total_responses * 0.0015  # 대략적인 비용
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("예상 소요 시간", f"{estimate_time:.1f}분")
        with col2:
            st.metric("예상 API 비용", f"${estimate_cost:.2f}")
        
        st.divider()
        
        # 설정
        st.markdown("### ⚙️ 설정")
        
        col1, col2 = st.columns(2)
        
        with col1:
            delay = st.slider(
                "API 호출 지연 시간 (초)",
                min_value=0.0,
                max_value=2.0,
                value=0.5,
                step=0.1,
                help="레이트 리밋 방지를 위한 지연 시간"
            )
        
        with col2:
            show_progress = st.checkbox("실시간 진행 상황 표시", value=True)
        
        st.divider()
        
        # 시작 버튼
        if st.button("▶️ 설문조사 시작", type="primary", use_container_width=True):
            responses = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            ai_agent = st.session_state.ai_agent
            personas = st.session_state.selected_personas
            
            total_tasks = len(personas) * len(survey.questions)
            completed = 0
            
            start_time = time.time()
            
            for persona_idx, persona in enumerate(personas, 1):
                for question in survey.questions:
                    if show_progress:
                        status_text.text(
                            f"진행 중... 응답자 {persona_idx}/{len(personas)} | {question.question_id}"
                        )
                    
                    # AI 응답 생성
                    response = ai_agent.respond_to_survey_question(
                        persona,
                        question.text,
                        question.scale_description
                    )
                    
                    response.update({
                        "survey_title": survey.title,
                        "question_id": question.question_id,
                        "category": question.category,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    responses.append(response)
                    
                    completed += 1
                    progress_bar.progress(completed / total_tasks)
                    
                    time.sleep(delay)
            
            elapsed_time = time.time() - start_time
            
            st.session_state.survey_responses = responses
            
            progress_bar.progress(1.0)
            status_text.empty()
            
            st.success(f"✅ 설문조사 완료! ({elapsed_time:.1f}초 소요)")
            st.balloons()
            
            # 간단한 통계
            st.divider()
            st.markdown("### 📊 간단한 통계")
            
            # 질문별 평균 계산
            question_stats = {}
            for resp in responses:
                qid = resp.get('question_id', 'Unknown')
                score = resp.get('score')
                
                if qid not in question_stats:
                    question_stats[qid] = {'scores': [], 'question': resp.get('question', '')}
                
                if score is not None:
                    question_stats[qid]['scores'].append(score)
            
            stats_data = []
            for qid, stats in question_stats.items():
                if stats['scores']:
                    stats_data.append({
                        '질문 ID': qid,
                        '질문': stats['question'][:50] + "...",
                        '평균': f"{sum(stats['scores']) / len(stats['scores']):.2f}",
                        '응답 수': len(stats['scores'])
                    })
            
            if stats_data:
                st.dataframe(pd.DataFrame(stats_data), use_container_width=True)
            
            st.info("💡 '결과 보기' 탭에서 자세한 분석을 확인하세요.")

# 탭 3: 결과 보기
with tab3:
    st.markdown("## 📈 결과 보기")
    
    if not st.session_state.survey_responses:
        st.info("💡 아직 진행된 설문조사가 없습니다. '설문 진행' 탭에서 설문을 진행하세요.")
    else:
        responses = st.session_state.survey_responses
        
        st.success(f"✅ 총 {len(responses)}개의 응답이 수집되었습니다.")
        
        # 통계 분석
        results_manager = ResultsManager()
        analysis = results_manager.analyze_survey_results(responses)
        
        # 기본 정보
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("총 응답", analysis['total_responses'])
        with col2:
            st.metric("응답자", analysis['unique_personas'])
        with col3:
            st.metric("질문 수", analysis['unique_questions'])
        
        st.divider()
        
        # 질문별 통계
        st.markdown("### 📊 질문별 통계")
        
        stats_data = []
        for qid, data in analysis['questions'].items():
            if 'mean' in data:
                stats_data.append({
                    '질문 ID': qid,
                    '질문': data['question'][:60] + "..." if len(data['question']) > 60 else data['question'],
                    '평균': f"{data['mean']:.2f}",
                    '최소': data['min'],
                    '최대': data['max'],
                    '응답 수': data['count']
                })
        
        if stats_data:
            df = pd.DataFrame(stats_data)
            st.dataframe(df, use_container_width=True)
            
            # 시각화
            st.markdown("### 📊 평균 점수 시각화")
            
            chart_data = pd.DataFrame(stats_data)
            chart_data['평균_숫자'] = chart_data['평균'].astype(float)
            
            st.bar_chart(
                chart_data.set_index('질문 ID')['평균_숫자'],
                use_container_width=True
            )
        
        st.divider()
        
        # 결과 다운로드
        st.markdown("### 💾 결과 다운로드")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # JSON 다운로드
            json_data = json.dumps(responses, ensure_ascii=False, indent=2)
            st.download_button(
                label="📥 JSON 다운로드",
                data=json_data,
                file_name=f"survey_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col2:
            # CSV 다운로드
            df = pd.DataFrame(responses)
            csv_data = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 CSV 다운로드",
                data=csv_data,
                file_name=f"survey_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col3:
            # 요약 보고서
            if st.button("📄 요약 보고서 생성", use_container_width=True):
                saved = results_manager.save_survey_results(responses)
                st.success("✅ 결과가 저장되었습니다!")
                for format_name, path in saved.items():
                    st.code(path, language="text")



