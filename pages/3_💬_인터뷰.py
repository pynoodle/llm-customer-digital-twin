"""
인터뷰 페이지
"""

import os
import streamlit as st
import pandas as pd
import json
import time
from datetime import datetime
from src.interview_system import InterviewGuide, InterviewQuestion
from src.results_manager import ResultsManager

st.set_page_config(page_title="인터뷰", page_icon="💬", layout="wide")

st.title("💬 인터뷰 시스템")
st.markdown("개방형 질문으로 심층 인터뷰를 진행하세요.")

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

# 현재 인터뷰 상태 초기화
if 'current_interview_guide' not in st.session_state:
    st.session_state.current_interview_guide = None

if 'interview_questions' not in st.session_state:
    st.session_state.interview_questions = []

st.divider()

# 탭 구성
tab1, tab2, tab3 = st.tabs(["📝 가이드 작성", "▶️ 인터뷰 진행", "📄 결과 보기"])

# 탭 1: 가이드 작성
with tab1:
    st.markdown("## 📝 인터뷰 가이드 작성")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        creation_mode = st.radio(
            "인터뷰 가이드 생성 방법",
            ["새로 만들기", "템플릿 불러오기"],
            horizontal=True
        )
    
    with col2:
        if st.button("🔄 초기화"):
            st.session_state.current_interview_guide = None
            st.session_state.interview_questions = []
            st.rerun()
    
    st.divider()
    
    if creation_mode == "새로 만들기":
        # 인터뷰 기본 정보
        st.markdown("### 기본 정보")
        
        interview_title = st.text_input(
            "인터뷰 제목*",
            placeholder="예: AI 기술 경험 심층 인터뷰",
            value=st.session_state.current_interview_guide.title if st.session_state.current_interview_guide else ""
        )
        
        interview_description = st.text_area(
            "설명 (선택사항)",
            placeholder="인터뷰에 대한 간단한 설명을 입력하세요.",
            value=st.session_state.current_interview_guide.description if st.session_state.current_interview_guide else ""
        )
        
        st.divider()
        
        # 질문 추가
        st.markdown("### 질문 관리")
        
        with st.expander("➕ 새 질문 추가", expanded=True):
            q_text = st.text_area(
                "질문 내용*",
                placeholder="예: AI 기술을 처음 접했을 때의 경험을 말씀해 주세요.",
                key="new_interview_question_text",
                height=100
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                q_category = st.text_input(
                    "카테고리 (선택사항)",
                    placeholder="예: 첫 경험",
                    key="new_interview_category"
                )
            
            with col2:
                q_context = st.text_input(
                    "추가 컨텍스트 (선택사항)",
                    placeholder="예: 구체적인 예시를 들어주세요.",
                    key="new_interview_context"
                )
            
            if st.button("➕ 질문 추가", type="primary"):
                if q_text.strip():
                    question = {
                        'id': f"IQ{len(st.session_state.interview_questions) + 1}",
                        'text': q_text,
                        'category': q_category if q_category else None,
                        'context': q_context if q_context else None
                    }
                    st.session_state.interview_questions.append(question)
                    st.success(f"✅ 질문이 추가되었습니다! (총 {len(st.session_state.interview_questions)}개)")
                    st.rerun()
                else:
                    st.error("❌ 질문 내용을 입력해주세요.")
        
        # 현재 질문 목록
        if st.session_state.interview_questions:
            st.markdown(f"### 📋 질문 목록 ({len(st.session_state.interview_questions)}개)")
            
            for i, q in enumerate(st.session_state.interview_questions):
                with st.expander(f"{q['id']}: {q['text'][:50]}...", expanded=False):
                    st.markdown(f"**질문:** {q['text']}")
                    if q['category']:
                        st.markdown(f"**카테고리:** {q['category']}")
                    if q['context']:
                        st.markdown(f"**컨텍스트:** {q['context']}")
                    
                    if st.button(f"🗑️ 삭제", key=f"delete_interview_{i}"):
                        st.session_state.interview_questions.pop(i)
                        st.rerun()
            
            # 가이드 저장
            st.divider()
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("💾 인터뷰 가이드 생성", type="primary", use_container_width=True):
                    if interview_title.strip():
                        guide = InterviewGuide(interview_title, interview_description)
                        for q in st.session_state.interview_questions:
                            guide.add_question(
                                text=q['text'],
                                question_id=q['id'],
                                category=q['category'],
                                context=q['context']
                            )
                        st.session_state.current_interview_guide = guide
                        st.success("✅ 인터뷰 가이드가 생성되었습니다!")
                    else:
                        st.error("❌ 인터뷰 제목을 입력해주세요.")
            
            with col2:
                if st.button("📥 템플릿으로 저장", use_container_width=True):
                    if interview_title.strip() and st.session_state.interview_questions:
                        template = {
                            'title': interview_title,
                            'description': interview_description,
                            'questions': [
                                {
                                    'question_id': q['id'],
                                    'text': q['text'],
                                    'category': q['category'],
                                    'context': q['context']
                                }
                                for q in st.session_state.interview_questions
                            ]
                        }
                        
                        st.download_button(
                            label="💾 JSON 다운로드",
                            data=json.dumps(template, ensure_ascii=False, indent=2),
                            file_name=f"{interview_title.replace(' ', '_')}_guide.json",
                            mime="application/json"
                        )
        else:
            st.info("💡 위에서 질문을 추가하세요.")
    
    else:  # 템플릿 불러오기
        st.markdown("### 📂 템플릿 불러오기")
        
        uploaded_file = st.file_uploader(
            "인터뷰 가이드 파일 (JSON)",
            type=['json'],
            help="이전에 저장한 인터뷰 가이드를 업로드하세요."
        )
        
        if uploaded_file is not None:
            try:
                template = json.load(uploaded_file)
                
                st.success("✅ 템플릿을 불러왔습니다!")
                
                st.markdown(f"**제목:** {template['title']}")
                st.markdown(f"**설명:** {template.get('description', 'N/A')}")
                st.markdown(f"**질문 수:** {len(template['questions'])}개")
                
                with st.expander("질문 미리보기"):
                    for q in template['questions']:
                        st.markdown(f"**{q['question_id']}:** {q['text']}")
                
                if st.button("✅ 이 템플릿 사용", type="primary"):
                    guide = InterviewGuide(template['title'], template.get('description', ''))
                    
                    st.session_state.interview_questions = []
                    
                    for q in template['questions']:
                        guide.add_question(
                            text=q['text'],
                            question_id=q.get('question_id'),
                            category=q.get('category'),
                            context=q.get('context')
                        )
                        
                        st.session_state.interview_questions.append({
                            'id': q.get('question_id', f"IQ{len(st.session_state.interview_questions) + 1}"),
                            'text': q['text'],
                            'category': q.get('category'),
                            'context': q.get('context')
                        })
                    
                    st.session_state.current_interview_guide = guide
                    st.rerun()
            
            except Exception as e:
                st.error(f"❌ 템플릿 로드 실패: {e}")
        
        # 예제 템플릿
        st.divider()
        st.markdown("### 📄 예제 템플릿")
        
        with open("examples/interview_guide.json", "r", encoding="utf-8") as f:
            example_template = f.read()
        
        st.download_button(
            label="📥 예제 템플릿 다운로드",
            data=example_template,
            file_name="interview_guide_example.json",
            mime="application/json"
        )

# 탭 2: 인터뷰 진행
with tab2:
    st.markdown("## ▶️ 인터뷰 진행")
    
    if not st.session_state.current_interview_guide:
        st.warning("⚠️ 먼저 인터뷰 가이드를 작성하거나 불러와주세요.")
    else:
        guide = st.session_state.current_interview_guide
        
        # 인터뷰 정보
        st.info(f"**인터뷰:** {guide.title}")
        st.info(f"**응답자:** {len(st.session_state.selected_personas)}명")
        st.info(f"**질문:** {len(guide.questions)}개")
        
        # 예상 시간 및 비용
        total_questions = len(st.session_state.selected_personas) * len(guide.questions)
        estimate_time = total_questions * 2.0 / 60  # 인터뷰는 더 오래 걸림
        estimate_cost = total_questions * 0.003  # 응답이 길어서 비용이 더 높음
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("예상 소요 시간", f"{estimate_time:.1f}분")
        with col2:
            st.metric("예상 API 비용", f"${estimate_cost:.2f}")
        
        st.divider()
        
        # 인터뷰 모드 선택
        st.markdown("### 🎬 인터뷰 모드")
        
        interview_mode = st.radio(
            "진행 방식 선택",
            ["배치 모드 (전체 자동)", "미리보기 모드 (샘플만)"],
            help="배치 모드: 모든 응답자에게 자동 진행 | 미리보기: 일부만 테스트"
        )
        
        # 설정
        st.markdown("### ⚙️ 설정")
        
        col1, col2 = st.columns(2)
        
        with col1:
            delay = st.slider(
                "API 호출 지연 시간 (초)",
                min_value=0.0,
                max_value=2.0,
                value=0.5,
                step=0.1
            )
        
        with col2:
            if interview_mode == "미리보기 모드 (샘플만)":
                preview_count = st.number_input(
                    "미리보기 응답자 수",
                    min_value=1,
                    max_value=min(10, len(st.session_state.selected_personas)),
                    value=min(3, len(st.session_state.selected_personas))
                )
            else:
                preview_count = len(st.session_state.selected_personas)
        
        show_responses = st.checkbox("실시간 응답 표시", value=True)
        
        st.divider()
        
        # 시작 버튼
        if st.button("▶️ 인터뷰 시작", type="primary", use_container_width=True):
            interviews = []
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            response_display = st.empty()
            
            ai_agent = st.session_state.ai_agent
            personas = st.session_state.selected_personas[:preview_count]
            
            total_tasks = len(personas) * len(guide.questions)
            completed = 0
            
            start_time = time.time()
            
            for persona_idx, persona in enumerate(personas, 1):
                interview_data = {
                    "persona_id": persona.id,
                    "interview_title": guide.title,
                    "timestamp": datetime.now().isoformat(),
                    "responses": []
                }
                
                for question in guide.questions:
                    status_text.text(
                        f"진행 중... 인터뷰 {persona_idx}/{len(personas)} | {question.question_id}"
                    )
                    
                    # AI 응답 생성
                    response = ai_agent.respond_to_interview_question(
                        persona,
                        question.text,
                        question.context
                    )
                    
                    response.update({
                        "question_id": question.question_id,
                        "category": question.category,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    interview_data["responses"].append(response)
                    
                    # 실시간 응답 표시
                    if show_responses and response.get('response'):
                        with response_display.container():
                            st.markdown(f"**응답자 #{persona.id} | {question.question_id}**")
                            st.write(response['response'])
                            st.markdown("---")
                    
                    completed += 1
                    progress_bar.progress(completed / total_tasks)
                    
                    time.sleep(delay)
                
                interviews.append(interview_data)
            
            elapsed_time = time.time() - start_time
            
            st.session_state.interview_results = interviews
            
            progress_bar.progress(1.0)
            status_text.empty()
            response_display.empty()
            
            st.success(f"✅ 인터뷰 완료! ({elapsed_time:.1f}초 소요)")
            st.balloons()
            
            st.info("💡 '결과 보기' 탭에서 전체 인터뷰 내용을 확인하세요.")

# 탭 3: 결과 보기
with tab3:
    st.markdown("## 📄 결과 보기")
    
    if not st.session_state.interview_results:
        st.info("💡 아직 진행된 인터뷰가 없습니다. '인터뷰 진행' 탭에서 인터뷰를 시작하세요.")
    else:
        interviews = st.session_state.interview_results
        
        st.success(f"✅ 총 {len(interviews)}개의 인터뷰가 완료되었습니다.")
        
        # 기본 통계
        total_responses = sum(len(i.get('responses', [])) for i in interviews)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("인터뷰 수", len(interviews))
        with col2:
            st.metric("총 응답", total_responses)
        with col3:
            avg_length = sum(
                len(r.get('response', '')) 
                for i in interviews 
                for r in i.get('responses', [])
            ) / total_responses if total_responses > 0 else 0
            st.metric("평균 응답 길이", f"{avg_length:.0f}자")
        
        st.divider()
        
        # 인터뷰 내용 보기
        st.markdown("### 📝 인터뷰 내용")
        
        # 인터뷰 선택
        interview_options = [f"응답자 #{i['persona_id']}" for i in interviews]
        selected_interview_idx = st.selectbox(
            "인터뷰 선택",
            range(len(interviews)),
            format_func=lambda x: interview_options[x]
        )
        
        if selected_interview_idx is not None:
            interview = interviews[selected_interview_idx]
            
            st.markdown(f"**인터뷰:** {interview['interview_title']}")
            st.markdown(f"**응답자 ID:** {interview['persona_id']}")
            st.markdown(f"**일시:** {interview['timestamp']}")
            
            st.divider()
            
            # 질문과 답변 표시
            for resp in interview.get('responses', []):
                with st.expander(f"**{resp['question_id']}:** {resp['question'][:60]}...", expanded=True):
                    st.markdown(f"**Q:** {resp['question']}")
                    st.markdown(f"**A:** {resp.get('response', '[응답 없음]')}")
                    if resp.get('category'):
                        st.caption(f"카테고리: {resp['category']}")
        
        st.divider()
        
        # 결과 다운로드
        st.markdown("### 💾 결과 다운로드")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # JSON 다운로드
            json_data = json.dumps(interviews, ensure_ascii=False, indent=2)
            st.download_button(
                label="📥 JSON 다운로드",
                data=json_data,
                file_name=f"interview_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col2:
            # CSV 다운로드
            rows = []
            for interview in interviews:
                for resp in interview.get('responses', []):
                    rows.append({
                        'persona_id': interview['persona_id'],
                        'question_id': resp.get('question_id'),
                        'question': resp.get('question'),
                        'response': resp.get('response'),
                        'category': resp.get('category')
                    })
            
            df = pd.DataFrame(rows)
            csv_data = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 CSV 다운로드",
                data=csv_data,
                file_name=f"interview_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col3:
            # 인터뷰록 생성
            if st.button("📄 인터뷰록 생성", use_container_width=True):
                results_manager = ResultsManager()
                saved = results_manager.save_interview_results(interviews)
                st.success("✅ 결과가 저장되었습니다!")
                for format_name, path in saved.items():
                    st.code(path, language="text")



