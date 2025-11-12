import streamlit as st
import pandas as pd
from price_search import search_product_prices

# -----------------------------
# 페이지 설정
# -----------------------------
st.set_page_config(
    page_title="네이버 쇼핑 가격 비교",
    page_icon=None,
    layout="wide",
)

# -----------------------------
# 사이드바 색상/스타일 (IMK Blue)
# -----------------------------
IMK_BLUE = "#003594"  # 아이마켓코리아 블루 근사값

st.markdown(
    f"""
    <style>
    /* 사이드바 배경 */
    [data-testid="stSidebar"] {{
        background: {IMK_BLUE} !important;
    }}

    /* 사이드바 기본 글씨: 흰색 */
    [data-testid="stSidebar"] * {{
        color: #ffffff !important;
    }}

    /* 사이드바 내 버튼(검색 이력/초기화)은 흰 배경 + 검정 글씨 */
    [data-testid="stSidebar"] button {{
        background-color: #ffffff !important;
        color: #000000 !important;
        border-radius: 6px !important;
        border: none !important;
        margin-bottom: 6px !important;
        font-weight: 600 !important;
        box-shadow: none !important;
    }}

    /* 사이드바 링크 가독성 */
    [data-testid="stSidebar"] a {{
        color: #ffffff !important;
        text-decoration: underline;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# -----------------------------
# 세션 상태 초기화 (검색 이력/트리거)
# -----------------------------
if "search_history" not in st.session_state:
    st.session_state.search_history = []          # 검색어 저장 (최대 10개, 최신이 뒤)
if "selected_query" not in st.session_state:
    st.session_state.selected_query = None        # 이력 클릭 시 사용할 값
if "trigger_research" not in st.session_state:
    st.session_state.trigger_research = False     # 자동 재검색 트리거

# -----------------------------
# 본문
# -----------------------------
st.title("네이버 쇼핑 가격 비교 대시보드")
st.write("상품명을 입력하면 네이버 쇼핑 API를 통해 가격/이미지/쇼핑몰 정보를 최저가 순으로 표로 제공합니다.")

# 입력 영역
query = st.text_input("상품명 입력", value="아이패드")

# 표시 개수: 슬라이더 → 라디오(클릭형)로 변경
count_options = [5, 10, 15, 20]
max_results = st.radio("표시할 상품 개수", options=count_options, index=1, horizontal=True)

# 검색 버튼
do_search = st.button("검색")

# -----------------------------
# 사이드바: 검색 이력
# -----------------------------
with st.sidebar:
    st.header("검색 이력")

    if st.button("검색 이력 초기화"):
        st.session_state.search_history = []

    # 최신 10개만 표시 (최신이 아래에 쌓이므로 슬라이스 후 순방향 출력)
    if st.session_state.search_history:
        last_10 = st.session_state.search_history[-10:]
        for i, q in enumerate(last_10, start=1):
            # 각 이력은 버튼으로 표시: 흰 배경/검정 글씨(위 CSS 적용)
            if st.button(f"{i}. {q}", key=f"hist_{i}"):
                st.session_state.selected_query = q
                st.session_state.trigger_research = True  # 클릭 즉시 재검색 트리거

    st.caption("최근 10개 검색어까지만 유지됩니다.")

# -----------------------------
# 이력 클릭 시 자동 재검색
# -----------------------------
if st.session_state.get("trigger_research", False):
    query = st.session_state.selected_query or query
    st.session_state.trigger_research = False
    do_search = True  # 버튼을 누르지 않아도 재검색하도록 플래그 설정

# -----------------------------
# 검색 실행
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

        # 검색 이력 업데이트 (연속 중복 방지 + 최대 10개 유지)
        if query:
            if not st.session_state.search_history or st.session_state.search_history[-1] != query:
                st.session_state.search_history.append(query)
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

        # DataFrame으로 변환 및 컬럼 순서 정리
        df = pd.DataFrame(items)
        df = df[["image_url", "title", "price", "mall_name", "link"]]

        st.subheader("이미지 포함 표 보기")
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
