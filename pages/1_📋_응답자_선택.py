"""
응답자 선택 페이지
"""

import os
import streamlit as st
import pandas as pd
from src.dataset_loader import Persona

st.set_page_config(page_title="응답자 선택", page_icon="📋", layout="wide")

st.title("📋 응답자 선택")
st.markdown("연구에 참여할 디지털 트윈 페르소나를 선택하세요.")

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
if st.session_state.loader is None:
    st.warning("⚠️ 시스템을 초기화하는 중...")
    try:
        from src.dataset_loader import DatasetLoader
        from src.ai_agent import AIAgent
        
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

loader = st.session_state.loader

st.divider()

# 선택 방법 선택
st.markdown("## 🎯 선택 방법")

selection_method = st.radio(
    "응답자를 어떻게 선택하시겠습니까?",
    ["무작위 샘플링", "조건 필터링", "전체 선택", "ID 직접 입력"],
    horizontal=True
)

st.divider()

selected_personas = []

# 1. 무작위 샘플링
if selection_method == "무작위 샘플링":
    st.markdown("### 🎲 무작위 샘플링")
    
    total_count = len(loader.get_all_personas())
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        sample_size = st.slider(
            "샘플 크기를 선택하세요",
            min_value=1,
            max_value=min(total_count, 500),
            value=min(50, total_count),
            step=1
        )
    
    with col2:
        random_seed = st.number_input(
            "랜덤 시드 (재현성)",
            min_value=0,
            max_value=9999,
            value=42,
            help="동일한 시드 값으로 동일한 샘플을 생성할 수 있습니다"
        )
    
    if st.button("🎲 샘플 추출", type="primary"):
        with st.spinner("샘플 추출 중..."):
            selected_personas = loader.get_random_sample(n=sample_size, seed=random_seed)
            st.session_state.selected_personas = selected_personas
            st.success(f"✅ {len(selected_personas)}명의 응답자가 선택되었습니다!")

# 2. 조건 필터링
elif selection_method == "조건 필터링":
    st.markdown("### 🔍 조건 필터링")
    
    st.info("💡 카테고리별로 세부 조건을 선택하여 응답자를 필터링하세요.")
    
    # 필터 저장
    filters = {}
    
    # 카테고리별 필드 가져오기
    categorized_fields = loader.get_categorized_fields()
    
    if not categorized_fields:
        st.error("❌ 필드 정보를 불러올 수 없습니다.")
        st.stop()
    
    # 전체 필드 수 표시
    total_fields = sum(len(fields) for fields in categorized_fields.values())
    st.success(f"✅ 총 **{total_fields}개**의 필드를 사용할 수 있습니다!")
    
    st.divider()
    st.markdown("#### 🗂️ 카테고리별 필터 선택")
    
    # 이모지 맵핑
    category_emoji = {
        "인구통계": "📊",
        "직업경제": "💼",
        "교육": "🎓",
        "성격심리": "🧠",
        "경제특성": "💰",
        "라이프스타일": "🏠",
        "지리위치": "🌍",
        "관계가족": "❤️",
        "가치관태도": "🎯",
        "기술미디어": "📱",
        "기타": "🔢"
    }
    
    # 대분류 선택 (이모지 포함)
    category_options = [f"{category_emoji.get(cat, '📂')} {cat}" for cat in categorized_fields.keys()]
    category_display = st.selectbox(
        "📂 대분류 선택",
        options=category_options,
        key="main_category"
    )
    
    # 실제 카테고리 이름 추출
    selected_category = category_display.split(' ', 1)[1] if ' ' in category_display else category_display
    
    if selected_category:
        category_fields = categorized_fields[selected_category]
        
        st.markdown(f"**{selected_category}** - {len(category_fields)}개 필드")
        
        # 여러 필드 선택 가능
        num_filters = st.number_input(
            "이 카테고리에서 필터 개수",
            min_value=0,
            max_value=min(10, len(category_fields)),
            value=min(2, len(category_fields)),
            key="num_filters"
        )
        
        for i in range(num_filters):
            st.markdown(f"**필터 {i+1}**")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # 소분류(필드) 선택
                selected_field = st.selectbox(
                    "필드 선택",
                    options=category_fields,
                    key=f"field_select_{i}"
                )
            
            with col2:
                if selected_field:
                    # 해당 필드의 고유 값 가져오기
                    unique_values = loader.get_field_unique_values(selected_field)
                    
                    if unique_values and len(unique_values) < 100:
                        # 선택 가능한 값이 적으면 multiselect
                        selected_values = st.multiselect(
                            "값 선택 (복수 가능)",
                            options=unique_values,
                            key=f"value_select_{i}"
                        )
                        
                        if selected_values:
                            if len(selected_values) == 1:
                                filters[selected_field] = selected_values[0]
                            else:
                                filters[selected_field] = selected_values
                    else:
                        # 값이 많거나 숫자인 경우 텍스트 입력
                        value_input = st.text_input(
                            "값 입력",
                            key=f"value_input_{i}",
                            help="정확한 값을 입력하거나 부분 검색어를 입력하세요"
                        )
                        
                        if value_input:
                            filters[selected_field] = value_input
            
            if i < num_filters - 1:
                st.markdown("---")
    
    st.divider()
    
    # 다른 카테고리 필터 추가
    with st.expander("➕ 다른 카테고리 필터 추가", expanded=False):
        st.markdown("**추가 필터**")
        
        other_category_options = ["선택 안 함"] + [
            f"{category_emoji.get(cat, '📂')} {cat}" 
            for cat in categorized_fields.keys() 
            if cat != selected_category
        ]
        
        other_category_display = st.selectbox(
            "다른 카테고리 선택",
            options=other_category_options,
            key="other_category"
        )
        
        # "선택 안 함"인 경우 처리
        if other_category_display == "선택 안 함":
            other_category = "선택 안 함"
        else:
            # 이모지 제거하고 카테고리 이름만 추출
            other_category = other_category_display.split(' ', 1)[1] if ' ' in other_category_display else other_category_display
        
        if other_category != "선택 안 함" and other_category in categorized_fields:
            other_fields = categorized_fields[other_category]
            
            if other_fields:
                other_field = st.selectbox(
                    "필드 선택",
                    options=other_fields,
                    key="other_field_select"
                )
            else:
                other_field = None
                st.info("이 카테고리에는 사용 가능한 필드가 없습니다.")
            
            if other_field:
                other_values = loader.get_field_unique_values(other_field)
                
                if other_values and len(other_values) < 100:
                    other_selected = st.multiselect(
                        "값 선택",
                        options=other_values,
                        key="other_value_select"
                    )
                    
                    if other_selected:
                        if len(other_selected) == 1:
                            filters[other_field] = other_selected[0]
                        else:
                            filters[other_field] = other_selected
                else:
                    other_input = st.text_input(
                        "값 입력",
                        key="other_value_input"
                    )
                    
                    if other_input:
                        filters[other_field] = other_input
    
    # 현재 선택된 필터 표시
    st.divider()
    
    if filters:
        st.markdown("#### 📋 선택된 필터")
        for key, value in filters.items():
            if isinstance(value, list):
                st.write(f"**{key}**: {', '.join(map(str, value))}")
            else:
                st.write(f"**{key}**: {value}")
        
        st.divider()
    
    if st.button("🔍 필터 적용", type="primary", use_container_width=True):
        if filters:
            with st.spinner("필터링 중..."):
                selected_personas = loader.search_personas(filters)
                st.session_state.selected_personas = selected_personas
                
                if selected_personas:
                    st.success(f"✅ {len(selected_personas)}명의 응답자가 선택되었습니다!")
                else:
                    st.warning("⚠️ 조건에 맞는 응답자가 없습니다. 필터를 조정해주세요.")
        else:
            st.warning("⚠️ 최소 1개의 필터를 선택해주세요.")

# 3. 전체 선택
elif selection_method == "전체 선택":
    st.markdown("### 📚 전체 선택")
    
    total_count = len(loader.get_all_personas())
    
    st.warning(f"⚠️ 전체 {total_count}명을 선택합니다. 처리 시간이 오래 걸릴 수 있습니다.")
    
    estimate_time = total_count * 1.5  # 응답자당 약 1.5초
    st.info(f"💡 예상 소요 시간: 약 {estimate_time/60:.1f}분")
    
    if st.button("✅ 전체 선택", type="primary"):
        selected_personas = loader.get_all_personas()
        st.session_state.selected_personas = selected_personas
        st.success(f"✅ {len(selected_personas)}명의 응답자가 선택되었습니다!")

# 4. ID 직접 입력
elif selection_method == "ID 직접 입력":
    st.markdown("### 🔢 ID 직접 입력")
    
    st.info("💡 쉼표로 구분하여 여러 ID를 입력할 수 있습니다. (예: 1, 2, 3, 4, 5)")
    
    id_input = st.text_area(
        "페르소나 ID를 입력하세요",
        placeholder="1, 2, 3, 4, 5",
        height=100
    )
    
    if st.button("✅ ID로 선택", type="primary"):
        if id_input.strip():
            ids = [id.strip() for id in id_input.split(",")]
            selected = []
            not_found = []
            
            for pid in ids:
                persona = loader.get_persona_by_id(pid)
                if persona:
                    selected.append(persona)
                else:
                    not_found.append(pid)
            
            if selected:
                st.session_state.selected_personas = selected
                st.success(f"✅ {len(selected)}명의 응답자가 선택되었습니다!")
                
                if not_found:
                    st.warning(f"⚠️ 다음 ID를 찾을 수 없습니다: {', '.join(not_found)}")
            else:
                st.error("❌ 유효한 ID가 없습니다.")
        else:
            st.error("❌ ID를 입력해주세요.")

st.divider()

# 선택된 응답자 미리보기
if st.session_state.selected_personas:
    st.markdown("## 👥 선택된 응답자")
    
    st.success(f"✅ 총 **{len(st.session_state.selected_personas)}명**이 선택되었습니다.")
    
    # 미리보기 옵션
    show_preview = st.checkbox("미리보기 표시", value=True)
    
    if show_preview:
        preview_count = st.slider(
            "미리보기 개수",
            min_value=1,
            max_value=min(20, len(st.session_state.selected_personas)),
            value=min(5, len(st.session_state.selected_personas))
        )
        
        st.markdown(f"### 처음 {preview_count}명")
        
        for i, persona in enumerate(st.session_state.selected_personas[:preview_count], 1):
            with st.expander(f"응답자 #{persona.id}", expanded=(i == 1)):
                # 페르소나 정보를 표로 표시
                info = persona.data
                
                # 중요 필드만 표시
                display_fields = {}
                for key, value in info.items():
                    if value and str(value).strip():
                        # 너무 긴 값은 잘라냄
                        str_value = str(value)
                        if len(str_value) > 200:
                            str_value = str_value[:200] + "..."
                        display_fields[key] = str_value
                
                # DataFrame으로 표시
                if display_fields:
                    df = pd.DataFrame([display_fields]).T
                    df.columns = ['값']
                    st.dataframe(df, use_container_width=True)
                else:
                    st.write(persona.data)
        
        if len(st.session_state.selected_personas) > preview_count:
            st.info(f"... 외 {len(st.session_state.selected_personas) - preview_count}명")
    
    # 선택 초기화
    if st.button("🔄 선택 초기화", type="secondary"):
        st.session_state.selected_personas = []
        st.rerun()
    
    # 다음 단계 안내
    st.divider()
    st.success("✅ 응답자 선택이 완료되었습니다! 이제 설문조사나 인터뷰를 진행하세요.")
    
    col1, col2 = st.columns(2)
    with col1:
        st.page_link("pages/2_📊_설문조사.py", label="📊 설문조사 시작", icon="📊")
    with col2:
        st.page_link("pages/3_💬_인터뷰.py", label="💬 인터뷰 시작", icon="💬")

else:
    st.info("💡 위에서 선택 방법을 선택하고 응답자를 선택하세요.")

