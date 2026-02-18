"""
결과 분석 및 다운로드 페이지
"""

import streamlit as st
import pandas as pd
import json
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from src.results_manager import ResultsManager

st.set_page_config(page_title="결과 분석", page_icon="📊", layout="wide")

st.title("📊 결과 분석 & 다운로드")
st.markdown("수집된 데이터를 분석하고 다양한 형식으로 다운로드하세요.")

st.divider()

# 세션 상태 확인
has_survey = bool(st.session_state.get('survey_responses', []))
has_interview = bool(st.session_state.get('interview_results', []))

if not has_survey and not has_interview:
    st.warning("⚠️ 아직 수집된 결과가 없습니다.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.page_link("pages/2_📊_설문조사.py", label="📊 설문조사 시작", icon="📊")
    with col2:
        st.page_link("pages/3_💬_인터뷰.py", label="💬 인터뷰 시작", icon="💬")
    
    st.stop()

# 탭 구성
tabs = []
if has_survey:
    tabs.append("📊 설문조사 분석")
if has_interview:
    tabs.append("💬 인터뷰 분석")
tabs.append("📥 통합 다운로드")

selected_tab = st.tabs(tabs)

# 결과 매니저
results_manager = ResultsManager()

# 설문조사 분석 탭
tab_idx = 0
if has_survey:
    with selected_tab[tab_idx]:
        st.markdown("## 📊 설문조사 결과 분석")
        
        responses = st.session_state.survey_responses
        analysis = results_manager.analyze_survey_results(responses)
        
        # 기본 통계
        st.markdown("### 📈 기본 통계")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "총 응답",
                f"{analysis['total_responses']:,}",
                help="수집된 총 응답 개수"
            )
        
        with col2:
            st.metric(
                "응답자 수",
                analysis['unique_personas'],
                help="참여한 응답자 수"
            )
        
        with col3:
            st.metric(
                "질문 수",
                analysis['unique_questions'],
                help="설문조사의 총 질문 개수"
            )
        
        with col4:
            # 평균 점수 계산
            all_scores = []
            for q_data in analysis['questions'].values():
                if 'mean' in q_data:
                    all_scores.append(q_data['mean'])
            overall_mean = sum(all_scores) / len(all_scores) if all_scores else 0
            
            st.metric(
                "전체 평균",
                f"{overall_mean:.2f}",
                help="모든 질문의 평균 점수"
            )
        
        st.divider()
        
        # 질문별 상세 분석
        st.markdown("### 📋 질문별 상세 분석")
        
        # 데이터 준비
        question_data = []
        for qid, data in analysis['questions'].items():
            if 'mean' in data:
                question_data.append({
                    '질문 ID': qid,
                    '질문': data['question'],
                    '평균': data['mean'],
                    '최소': data['min'],
                    '최대': data['max'],
                    '응답 수': data['count'],
                    '표준편차': pd.Series(data['scores']).std() if data['scores'] else 0
                })
        
        if question_data:
            df_questions = pd.DataFrame(question_data)
            
            # 테이블 표시
            st.dataframe(
                df_questions.style.background_gradient(
                    subset=['평균'],
                    cmap='RdYlGn',
                    vmin=1,
                    vmax=7
                ),
                use_container_width=True,
                hide_index=True
            )
            
            st.divider()
            
            # 시각화
            st.markdown("### 📊 시각화")
            
            # 평균 점수 막대 그래프
            fig_bar = px.bar(
                df_questions,
                x='질문 ID',
                y='평균',
                title='질문별 평균 점수',
                labels={'평균': '평균 점수 (1-7)', '질문 ID': '질문'},
                color='평균',
                color_continuous_scale='RdYlGn',
                range_color=[1, 7],
                hover_data=['질문']
            )
            fig_bar.update_layout(height=400)
            st.plotly_chart(fig_bar, use_container_width=True)
            
            # 분포 분석
            st.markdown("### 📊 응답 분포 분석")
            
            selected_question = st.selectbox(
                "질문 선택",
                options=list(analysis['questions'].keys()),
                format_func=lambda x: f"{x}: {analysis['questions'][x]['question'][:50]}..."
            )
            
            if selected_question:
                q_data = analysis['questions'][selected_question]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # 히스토그램
                    if 'distribution' in q_data:
                        dist_df = pd.DataFrame([
                            {'점수': k, '응답 수': v}
                            for k, v in q_data['distribution'].items()
                        ])
                        
                        fig_hist = px.bar(
                            dist_df,
                            x='점수',
                            y='응답 수',
                            title=f'{selected_question} 응답 분포',
                            labels={'점수': '점수 (1-7)', '응답 수': '응답 수'},
                            color='응답 수',
                            color_continuous_scale='Blues'
                        )
                        fig_hist.update_layout(height=350)
                        st.plotly_chart(fig_hist, use_container_width=True)
                
                with col2:
                    # 파이 차트
                    if 'distribution' in q_data:
                        fig_pie = px.pie(
                            dist_df,
                            values='응답 수',
                            names='점수',
                            title=f'{selected_question} 점수 비율',
                            color_discrete_sequence=px.colors.sequential.RdBu
                        )
                        fig_pie.update_layout(height=350)
                        st.plotly_chart(fig_pie, use_container_width=True)
                
                # 상세 통계
                with st.expander("📊 상세 통계"):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("평균", f"{q_data['mean']:.2f}")
                    with col2:
                        st.metric("중앙값", f"{pd.Series(q_data['scores']).median():.1f}")
                    with col3:
                        st.metric("최빈값", f"{pd.Series(q_data['scores']).mode()[0]}")
                    with col4:
                        st.metric("표준편차", f"{pd.Series(q_data['scores']).std():.2f}")
            
            st.divider()
            
            # 카테고리별 분석
            categories = set()
            for resp in responses:
                if resp.get('category'):
                    categories.add(resp['category'])
            
            if categories:
                st.markdown("### 🏷️ 카테고리별 분석")
                
                category_stats = {}
                for resp in responses:
                    cat = resp.get('category', '미분류')
                    score = resp.get('score')
                    
                    if cat not in category_stats:
                        category_stats[cat] = []
                    
                    if score is not None:
                        category_stats[cat].append(score)
                
                cat_df = pd.DataFrame([
                    {
                        '카테고리': cat,
                        '평균 점수': sum(scores) / len(scores),
                        '응답 수': len(scores)
                    }
                    for cat, scores in category_stats.items()
                    if scores
                ])
                
                fig_cat = px.bar(
                    cat_df,
                    x='카테고리',
                    y='평균 점수',
                    title='카테고리별 평균 점수',
                    color='평균 점수',
                    color_continuous_scale='RdYlGn',
                    range_color=[1, 7],
                    hover_data=['응답 수']
                )
                fig_cat.update_layout(height=400)
                st.plotly_chart(fig_cat, use_container_width=True)
        
        st.divider()
        
        # 다운로드
        st.markdown("### 💾 설문조사 결과 다운로드")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            json_data = json.dumps(responses, ensure_ascii=False, indent=2)
            st.download_button(
                label="📥 JSON",
                data=json_data,
                file_name=f"survey_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col2:
            csv_data = pd.DataFrame(responses).to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 CSV",
                data=csv_data,
                file_name=f"survey_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col3:
            if st.button("📥 Excel", use_container_width=True):
                filepath = results_manager.export_to_excel(survey_responses=responses)
                st.success(f"✅ 저장됨: {filepath}")
        
        with col4:
            if st.button("📄 전체 저장", use_container_width=True):
                saved = results_manager.save_survey_results(responses)
                st.success("✅ 모든 형식으로 저장 완료!")
                for fmt, path in saved.items():
                    st.code(path, language="text")
    
    tab_idx += 1

# 인터뷰 분석 탭
if has_interview:
    with selected_tab[tab_idx]:
        st.markdown("## 💬 인터뷰 결과 분석")
        
        interviews = st.session_state.interview_results
        
        # 기본 통계
        st.markdown("### 📈 기본 통계")
        
        total_responses = sum(len(i.get('responses', [])) for i in interviews)
        total_words = sum(
            len(r.get('response', '')) 
            for i in interviews 
            for r in i.get('responses', [])
        )
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("인터뷰 수", len(interviews))
        
        with col2:
            st.metric("총 응답", total_responses)
        
        with col3:
            avg_length = total_words / total_responses if total_responses > 0 else 0
            st.metric("평균 응답 길이", f"{avg_length:.0f}자")
        
        with col4:
            st.metric("총 텍스트", f"{total_words:,}자")
        
        st.divider()
        
        # 인터뷰 목록
        st.markdown("### 📝 인터뷰 목록")
        
        interview_summary = []
        for i, interview in enumerate(interviews):
            total_chars = sum(
                len(r.get('response', ''))
                for r in interview.get('responses', [])
            )
            
            interview_summary.append({
                '번호': i + 1,
                '응답자 ID': interview['persona_id'],
                '인터뷰 제목': interview['interview_title'],
                '응답 수': len(interview.get('responses', [])),
                '총 글자 수': total_chars,
                '일시': interview['timestamp'][:19]
            })
        
        df_interviews = pd.DataFrame(interview_summary)
        st.dataframe(df_interviews, use_container_width=True, hide_index=True)
        
        st.divider()
        
        # 응답 길이 분석
        st.markdown("### 📏 응답 길이 분석")
        
        response_lengths = []
        for interview in interviews:
            for resp in interview.get('responses', []):
                response_lengths.append({
                    '응답자 ID': interview['persona_id'],
                    '질문 ID': resp.get('question_id', ''),
                    '응답 길이': len(resp.get('response', ''))
                })
        
        df_lengths = pd.DataFrame(response_lengths)
        
        col1, col2 = st.columns(2)
        
        with col1:
            # 응답자별 평균 길이
            avg_by_persona = df_lengths.groupby('응답자 ID')['응답 길이'].mean().reset_index()
            
            fig_persona = px.bar(
                avg_by_persona,
                x='응답자 ID',
                y='응답 길이',
                title='응답자별 평균 응답 길이',
                labels={'응답 길이': '평균 글자 수'},
                color='응답 길이',
                color_continuous_scale='Blues'
            )
            fig_persona.update_layout(height=350)
            st.plotly_chart(fig_persona, use_container_width=True)
        
        with col2:
            # 질문별 평균 길이
            avg_by_question = df_lengths.groupby('질문 ID')['응답 길이'].mean().reset_index()
            
            fig_question = px.bar(
                avg_by_question,
                x='질문 ID',
                y='응답 길이',
                title='질문별 평균 응답 길이',
                labels={'응답 길이': '평균 글자 수'},
                color='응답 길이',
                color_continuous_scale='Greens'
            )
            fig_question.update_layout(height=350)
            st.plotly_chart(fig_question, use_container_width=True)
        
        st.divider()
        
        # 인터뷰 내용 보기
        st.markdown("### 📖 인터뷰 내용")
        
        selected_idx = st.selectbox(
            "인터뷰 선택",
            range(len(interviews)),
            format_func=lambda x: f"응답자 #{interviews[x]['persona_id']} - {interviews[x]['interview_title']}"
        )
        
        if selected_idx is not None:
            interview = interviews[selected_idx]
            
            for resp in interview.get('responses', []):
                with st.expander(f"**{resp['question_id']}:** {resp['question']}", expanded=False):
                    st.markdown(f"**질문:** {resp['question']}")
                    st.markdown("---")
                    st.markdown(f"**응답:**\n\n{resp.get('response', '[응답 없음]')}")
                    if resp.get('category'):
                        st.caption(f"카테고리: {resp['category']}")
                    st.caption(f"글자 수: {len(resp.get('response', ''))}자")
        
        st.divider()
        
        # 다운로드
        st.markdown("### 💾 인터뷰 결과 다운로드")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            json_data = json.dumps(interviews, ensure_ascii=False, indent=2)
            st.download_button(
                label="📥 JSON",
                data=json_data,
                file_name=f"interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
        
        with col2:
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
            
            csv_data = pd.DataFrame(rows).to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="📥 CSV",
                data=csv_data,
                file_name=f"interview_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col3:
            if st.button("📥 Excel", key="interview_excel", use_container_width=True):
                filepath = results_manager.export_to_excel(interviews=interviews)
                st.success(f"✅ 저장됨: {filepath}")
        
        with col4:
            if st.button("📄 전체 저장", key="interview_save_all", use_container_width=True):
                saved = results_manager.save_interview_results(interviews)
                st.success("✅ 모든 형식으로 저장 완료!")
                for fmt, path in saved.items():
                    st.code(path, language="text")
    
    tab_idx += 1

# 통합 다운로드 탭
with selected_tab[tab_idx]:
    st.markdown("## 📥 통합 다운로드")
    
    st.info("💡 설문조사와 인터뷰 결과를 하나의 파일로 통합하여 다운로드할 수 있습니다.")
    
    st.divider()
    
    # 포함할 데이터 선택
    st.markdown("### 📋 포함할 데이터")
    
    col1, col2 = st.columns(2)
    
    with col1:
        include_survey = st.checkbox(
            "설문조사 결과 포함",
            value=has_survey,
            disabled=not has_survey
        )
    
    with col2:
        include_interview = st.checkbox(
            "인터뷰 결과 포함",
            value=has_interview,
            disabled=not has_interview
        )
    
    st.divider()
    
    if not include_survey and not include_interview:
        st.warning("⚠️ 최소 하나의 데이터 유형을 선택해주세요.")
    else:
        st.markdown("### 💾 다운로드 옵션")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # 통합 JSON
            combined_data = {}
            
            if include_survey:
                combined_data['survey'] = st.session_state.survey_responses
            
            if include_interview:
                combined_data['interviews'] = st.session_state.interview_results
            
            combined_data['metadata'] = {
                'export_date': datetime.now().isoformat(),
                'total_personas': len(st.session_state.get('selected_personas', [])),
                'has_survey': include_survey,
                'has_interview': include_interview
            }
            
            json_data = json.dumps(combined_data, ensure_ascii=False, indent=2)
            st.download_button(
                label="📥 통합 JSON",
                data=json_data,
                file_name=f"combined_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True,
                type="primary"
            )
        
        with col2:
            # 통합 Excel
            if st.button("📥 통합 Excel", use_container_width=True, type="primary"):
                survey_data = st.session_state.survey_responses if include_survey else None
                interview_data = st.session_state.interview_results if include_interview else None
                
                filepath = results_manager.export_to_excel(
                    survey_responses=survey_data,
                    interviews=interview_data
                )
                
                st.success(f"✅ Excel 파일이 저장되었습니다!")
                st.code(filepath, language="text")
        
        with col3:
            # 전체 저장 (모든 형식)
            if st.button("📄 전체 저장", use_container_width=True):
                saved_files = []
                
                if include_survey:
                    survey_files = results_manager.save_survey_results(
                        st.session_state.survey_responses
                    )
                    saved_files.extend(survey_files.values())
                
                if include_interview:
                    interview_files = results_manager.save_interview_results(
                        st.session_state.interview_results
                    )
                    saved_files.extend(interview_files.values())
                
                st.success(f"✅ 총 {len(saved_files)}개의 파일이 저장되었습니다!")
                
                with st.expander("저장된 파일 목록"):
                    for filepath in saved_files:
                        st.code(filepath, language="text")
        
        st.divider()
        
        # 저장 위치 안내
        st.info("""
        📁 **저장 위치**: `results/` 폴더
        
        파일들은 프로젝트의 `results` 폴더에 저장됩니다.
        다양한 형식(JSON, CSV, Excel, TXT)으로 저장되어 원하는 방식으로 분석할 수 있습니다.
        """)

st.divider()

# 데이터 초기화
st.markdown("### 🔄 데이터 관리")

with st.expander("⚠️ 데이터 초기화 (주의)", expanded=False):
    st.warning("현재 세션의 모든 데이터가 삭제됩니다. 저장하지 않은 결과는 복구할 수 없습니다.")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        confirm_text = st.text_input(
            "초기화하려면 'DELETE'를 입력하세요",
            key="confirm_delete"
        )
    
    with col2:
        if st.button("🗑️ 초기화", type="secondary", disabled=(confirm_text != "DELETE")):
            st.session_state.selected_personas = []
            st.session_state.survey_responses = []
            st.session_state.interview_results = []
            st.session_state.current_survey = None
            st.session_state.current_interview_guide = None
            st.session_state.survey_questions = []
            st.session_state.interview_questions = []
            
            st.success("✅ 모든 데이터가 초기화되었습니다.")
            st.rerun()

