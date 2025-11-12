import streamlit as st
import pandas as pd
from price_search import search_product_prices

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="쇼핑 가격 비교",
    page_icon=None,
    layout="wide",
)

# -----------------------------
# 사이드바 색상 커스텀 (IMK Blue #003594)
# -----------------------------
IMK_BLUE = "#003594"  # Pantone 661C의 웹 근사값
st.markdown(
    f"""
    <style>
    [data-testid="stSidebar"] {{
        background: {IMK_BLUE} !important;
    }}
    [data-testid="stSidebar"] * {{
        color: #000000 !important; /* 글씨 검정색으로 변경 */
    }}
    [data-testid="stSidebar"] a {{
        color: #000000 !important;
        text-decoration: underline;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# 세션 상태 초기화 (검색 이력)
# -----------------------------
if "search_history" not in st.session_state:
    st.session_state.search_history = []  # 최신이 뒤에 쌓임

# -----------------------------
# 본문 UI
# -----------------------------
st.title("쇼핑 가격 비교")
st.write("상품명을 입력하면 네이버 쇼핑 API를 통해 가격/이미지/쇼핑몰 정보를 최저가 순으로 표로 제공합니다.")

# 검색 입력
query = st.text_input("상품명 입력", value="")

# 슬라이더 → 클릭형 선택
# Streamlit 1.22+ 에서는 radio(horizontal=True) 지원. 구버전이면 selectbox로 바꿔도 됨.
count_options = [5, 10, 15, 20]
max_results = st.radio("표시할 상품 개수", options=count_options, index=1, horizontal=True)

# 조회 버튼
do_search = st.button("검색")

# -----------------------------
# 사이드바: 검색 이력, 관리
# -----------------------------
with st.sidebar:
    st.header("검색 이력")
    if st.button("검색 이력 초기화"):
        st.session_state.search_history = []

    # 이력 리스트 출력 (최신이 아래로)
    if st.session_state.search_history:
        for i, q in enumerate(st.session_state.search_history[-10:], start=1):
            if st.button(f"{i}. {q}", key=f"hist_{i}"):
                # 이력 클릭 시 현재 입력창을 해당 값으로 바꾸고 재실행 유도
                st.session_state["last_clicked_query"] = q

    # 힌트 안내
    st.caption("최근 10개 검색어까지만 유지됩니다.")

# 이력 클릭 시 입력창에 반영
if "last_clicked_query" in st.session_state:
    query = st.session_state["last_clicked_query"]
    # 한 번 반영 후 키 제거
    del st.session_state["last_clicked_query"]

# -----------------------------
# 검색 실행 로직
# -----------------------------
items = []
if do_search:
    if not query.strip():
        st.warning("상품명을 입력해 주세요.")
    else:
        with st.spinner("네이버 쇼핑에서 가격 정보를 가져오는 중입니다..."):
            try:
                items = search_product_prices(query, max_results=max_results)
            except Exception as e:
                st.error(f"검색 중 오류가 발생했습니다: {e}")
                items = []

        # 검색 이력 업데이트: 동일 검색어가 연속으로 쌓이지 않도록 처리(선택사항)
        if query and (not st.session_state.search_history or st.session_state.search_history[-1] != query):
            st.session_state.search_history.append(query)
            # 최대 10개 유지: 초과 시 앞에서 제거
            if len(st.session_state.search_history) > 10:
                overflow = len(st.session_state.search_history) - 10
                st.session_state.search_history = st.session_state.search_history[overflow:]

# -----------------------------
# 결과 표시
# -----------------------------
if do_search:
    if not items:
        st.info("검색 결과가 없거나, 가격/이미지 정보가 없는 상품입니다.")
    else:
        st.success(f"총 {len(items)}개 상품을 최저가 순으로 정렬했습니다.")

        # DataFrame 변환 및 컬럼 정리
        df = pd.DataFrame(items)
        df = df[["image_url", "title", "price", "mall_name", "link"]]

        st.subheader("최저가 순 정렬")
        st.dataframe(
            df,
            column_config={
                "image_url": st.column_config.ImageColumn(
                    "이미지",
                    help="상품 썸네일",
                    width="small",
                ),
                "title": "상품명",
                "price": "최저가",
                "mall_name": "쇼핑몰",
                "link": st.column_config.LinkColumn(
                    "링크",
                    help="네이버 쇼핑 상품 페이지로 이동",
                ),
            },
            hide_index=True,
            use_container_width=True,
        )
