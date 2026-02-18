"""
블록 기반 응답자 선택 페이지
"""

import streamlit as st
import pandas as pd
import json
import os
from typing import List, Dict, Any
from block_based_selector import BlockBasedSelector, Persona

def initialize_block_selector():
    """블록 기반 선택 시스템을 초기화합니다."""
    if 'block_selector' not in st.session_state:
        st.session_state.block_selector = None
    
    if st.session_state.block_selector is None:
        with st.spinner("🔄 블록 기반 선택 시스템 초기화 중..."):
            try:
                selector = BlockBasedSelector()
                selector.load()
                st.session_state.block_selector = selector
                st.success("✅ 블록 기반 선택 시스템 준비 완료!")
            except Exception as e:
                st.error(f"❌ 초기화 실패: {e}")
                return False
    
    return True

def main():
    """메인 함수"""
    st.markdown("## 📋 응답자 선택 (블록 기반)")
    
    # 시스템 초기화
    if not initialize_block_selector():
        st.stop()
    
    selector = st.session_state.block_selector
    
    # 선택 방법
    st.markdown("### 🎯 선택 방법")
    selection_method = st.radio(
        "선택 방법을 선택하세요",
        ["블록 기반 필터링", "랜덤 샘플링", "ID 직접 입력"],
        horizontal=True
    )
    
    if selection_method == "블록 기반 필터링":
        st.markdown("### 🔍 블록 기반 필터링")
        
        # 블록 카테고리 표시
        categories = selector.get_block_categories()
        if categories:
            st.markdown("#### 📂 사용 가능한 블록 카테고리")
            
            for category, blocks in categories.items():
                with st.expander(f"🔹 {category.replace('_', ' ').title()}"):
                    st.write(f"총 {len(blocks)}개 블록")
                    
                    # 블록 통계 표시
                    stats = selector.get_block_statistics()
                    for block in blocks[:10]:  # 처음 10개만 표시
                        if block in stats:
                            stat = stats[block]
                            st.write(f"• **{block}**: {stat['presence_rate']:.1f}% ({stat['presence_count']:,}명)")
                    
                    if len(blocks) > 10:
                        st.caption(f"... 외 {len(blocks) - 10}개 블록")
        
        # 필터링 조건 설정
        st.markdown("#### ⚙️ 필터링 조건")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**필수 블록 (모든 조건을 만족해야 함)**")
            required_blocks = st.multiselect(
                "필수로 포함되어야 할 블록을 선택하세요",
                options=selector.get_available_blocks(),
                help="선택한 블록을 모두 가진 페르소나만 필터링됩니다."
            )
        
        with col2:
            st.markdown("**선택적 블록 (하나라도 포함되면 됨)**")
            optional_blocks = st.multiselect(
                "선택적으로 포함될 블록을 선택하세요",
                options=selector.get_available_blocks(),
                help="선택한 블록 중 하나라도 가진 페르소나가 필터링됩니다."
            )
        
        # 질문 수 조건
        st.markdown("#### 📊 질문 수 조건")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            question_block = st.selectbox(
                "질문 수를 확인할 블록",
                options=selector.get_available_blocks(),
                help="특정 블록의 질문 수로 필터링합니다."
            )
        
        with col2:
            min_questions = st.number_input(
                "최소 질문 수",
                min_value=0,
                value=1,
                help="최소 질문 수"
            )
        
        with col3:
            max_questions = st.number_input(
                "최대 질문 수",
                min_value=0,
                value=None,
                help="최대 질문 수 (0이면 제한 없음)"
            )
        
        # 필터링 실행
        if st.button("🔍 필터링 실행", type="primary"):
            with st.spinner("필터링 중..."):
                # 블록 기반 필터링
                if required_blocks or optional_blocks:
                    filtered_personas = selector.filter_by_blocks(
                        required_blocks=required_blocks,
                        optional_blocks=optional_blocks
                    )
                else:
                    filtered_personas = selector.personas
                
                # 질문 수 기반 추가 필터링
                if question_block:
                    if max_questions and max_questions > 0:
                        filtered_personas = selector.filter_by_question_count(
                            question_block, min_questions, max_questions
                        )
                    else:
                        filtered_personas = selector.filter_by_question_count(
                            question_block, min_questions
                        )
                
                st.session_state.selected_personas = filtered_personas
                st.success(f"✅ {len(filtered_personas)}명의 응답자가 선택되었습니다!")
    
    elif selection_method == "랜덤 샘플링":
        st.markdown("### 🎲 랜덤 샘플링")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            sample_size = st.number_input(
                "샘플 크기",
                min_value=1,
                max_value=1000,
                value=10
            )
        
        with col2:
            seed = st.number_input("랜덤 시드", value=42)
        
        with col3:
            required_blocks = st.multiselect(
                "필수 블록 (선택사항)",
                options=selector.get_available_blocks(),
                help="선택한 블록을 가진 페르소나 중에서만 샘플링합니다."
            )
        
        if st.button("🎲 샘플 추출", type="primary"):
            with st.spinner("샘플링 중..."):
                sample_personas = selector.get_random_sample(
                    n=sample_size,
                    seed=seed,
                    required_blocks=required_blocks
                )
                st.session_state.selected_personas = sample_personas
                st.success(f"✅ {len(sample_personas)}명의 응답자가 선택되었습니다!")
    
    else:  # ID 직접 입력
        st.markdown("### 🆔 ID 직접 입력")
        
        indices_input = st.text_area(
            "ID를 입력하세요 (쉼표로 구분)",
            placeholder="574, 1234, 5678",
            height=100
        )
        
        if st.button("✅ 선택", type="primary"):
            try:
                selected_ids = [id.strip() for id in indices_input.split(",") if id.strip()]
                selected_personas = []
                
                for persona_id in selected_ids:
                    persona = selector.get_persona_by_id(persona_id)
                    if persona:
                        selected_personas.append(persona)
                    else:
                        st.warning(f"⚠️ ID {persona_id}를 찾을 수 없습니다.")
                
                st.session_state.selected_personas = selected_personas
                st.success(f"✅ {len(selected_personas)}명의 응답자가 선택되었습니다!")
                
            except Exception as e:
                st.error(f"❌ 오류 발생: {e}")
    
    # 선택된 응답자 표시
    if hasattr(st.session_state, 'selected_personas') and st.session_state.selected_personas:
        st.divider()
        st.markdown(f"### 👥 선택된 응답자: {len(st.session_state.selected_personas)}명")
        
        # 통계 정보
        if st.session_state.selected_personas:
            st.markdown("#### 📊 선택된 응답자 통계")
            
            # 블록별 통계
            block_stats = {}
            for persona in st.session_state.selected_personas:
                for key, value in persona.data.items():
                    if key.startswith('has_') and value == 1:
                        block_name = key.replace('has_', '').replace('_', ' ').title()
                        block_stats[block_name] = block_stats.get(block_name, 0) + 1
            
            if block_stats:
                st.markdown("**블록별 분포:**")
                sorted_stats = sorted(block_stats.items(), key=lambda x: x[1], reverse=True)
                
                for block_name, count in sorted_stats[:10]:  # 상위 10개만 표시
                    percentage = (count / len(st.session_state.selected_personas)) * 100
                    st.write(f"• **{block_name}**: {count}명 ({percentage:.1f}%)")
        
        # 미리보기
        show_preview = st.checkbox("미리보기 표시", value=True)
        
        if show_preview:
            preview_count = min(5, len(st.session_state.selected_personas))
            
            for i, persona in enumerate(st.session_state.selected_personas[:preview_count]):
                with st.expander(f"응답자 #{persona.id}"):
                    # 기본 정보
                    st.write(f"**PID**: {persona.id}")
                    
                    # Persona Text 미리보기
                    if 'persona_text' in persona.data:
                        text = str(persona.data['persona_text'])
                        if len(text) > 500:
                            text = text[:500] + "..."
                        st.write(f"**Persona Text**: {text}")
                    
                    # Persona Summary
                    if 'persona_summary' in persona.data:
                        summary = str(persona.data['persona_summary'])
                        if len(summary) > 300:
                            summary = summary[:300] + "..."
                        st.write(f"**Summary**: {summary}")
                    
                    # 보유 블록 정보
                    st.write("**보유 블록:**")
                    blocks = []
                    for key, value in persona.data.items():
                        if key.startswith('has_') and value == 1:
                            block_name = key.replace('has_', '').replace('_', ' ').title()
                            question_count = persona.data.get(f"questions_{key.replace('has_', '')}", 0)
                            blocks.append(f"{block_name} ({question_count}개 질문)")
                    
                    if blocks:
                        for block in blocks[:10]:  # 처음 10개만 표시
                            st.write(f"• {block}")
                        if len(blocks) > 10:
                            st.caption(f"... 외 {len(blocks) - 10}개 블록")
        
        # 결과 저장
        st.markdown("#### 💾 결과 저장")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("📥 CSV로 저장"):
                try:
                    # 페르소나 데이터를 DataFrame으로 변환
                    data = [persona.data for persona in st.session_state.selected_personas]
                    df = pd.DataFrame(data)
                    
                    # CSV 저장
                    csv_data = df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        "📥 CSV 다운로드",
                        data=csv_data,
                        file_name="selected_respondents.csv",
                        mime="text/csv"
                    )
                except Exception as e:
                    st.error(f"❌ 저장 실패: {e}")
        
        with col2:
            if st.button("📥 JSON으로 저장"):
                try:
                    # 페르소나 데이터를 JSON으로 변환
                    data = [persona.data for persona in st.session_state.selected_personas]
                    json_data = json.dumps(data, ensure_ascii=False, indent=2)
                    
                    st.download_button(
                        "📥 JSON 다운로드",
                        data=json_data,
                        file_name="selected_respondents.json",
                        mime="application/json"
                    )
                except Exception as e:
                    st.error(f"❌ 저장 실패: {e}")

if __name__ == "__main__":
    main()
