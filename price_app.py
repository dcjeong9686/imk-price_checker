import streamlit as st
import pandas as pd
from price_search import search_product_prices

st.set_page_config(
    page_title="가격 비교",
    page_icon=None,
    layout="wide",
)

st.title("가격 비교")
st.write("상품명을 입력하면 네이버 쇼핑 API를 통해 가격/이미지/쇼핑몰 정보를 표로 제공합니다.")

# -----------------------------
# 1. 검색어 입력
# -----------------------------
query = st.text_input("상품명 입력", value="")

# -----------------------------
# 2. 정렬 옵션 + 표시 개수 → 같은 줄에 배치
# -----------------------------
col_sort, col_count = st.columns([1, 1.2])

with col_sort:
    sort_choice = st.radio("정렬 옵션", ["관련도순", "가격순"], index=0, horizontal=True)
    sort_mode = "sim" if sort_choice == "관련도순" else "asc"

with col_count:
    max_results = st.radio("표시할 상품 개수", [5, 10, 15, 20], index=1, horizontal=True)

# -----------------------------
# 3. 제외 키워드
# -----------------------------
exclude_text = st.text_input("제외 키워드 (쉼표로 구분, 예: 중고,케이스,리퍼)")
exclude_keywords = [t.strip() for t in exclude_text.split(",") if t.strip()]

# -----------------------------
# 4. 검색 버튼
# -----------------------------
do_search = st.button("검색")

# -----------------------------
# 5. 메모장 기능
# -----------------------------
if "memo_text" not in st.session_state:
    st.session_state.memo_text = ""

with st.expander("메모장", expanded=False):
    st.session_state.memo_text = st.text_area("메모", value=st.session_state.memo_text, height=160)
    colm1, colm2, colm3 = st.columns([1, 1, 2])
    with colm1:
        if st.button("메모 저장"):
            st.success("메모가 저장되었습니다.")
    with colm2:
        if st.button("메모 지우기"):
            st.session_state.memo_text = ""
            st.experimental_rerun()
    with colm3:
        st.download_button(
            label="메모 다운로드(.txt)",
            data=st.session_state.memo_text.encode("utf-8"),
            file_name="memo.txt",
            mime="text/plain",
        )

# -----------------------------
# 6. 검색 실행
# -----------------------------
items = []
if do_search:
    if not query.strip():
        st.warning("상품명을 입력해 주세요.")
    else:
        with st.spinner("네이버 쇼핑에서 가격 정보를 가져오는 중입니다..."):
            try:
                items = search_product_prices(query, max_results=max_results, sort_mode=sort_mode)
            except Exception as e:
                st.error(f"검색 중 오류가 발생했습니다: {e}")
                items = []

        # 제외 키워드 필터링
        if exclude_keywords and items:
            filtered = []
            for row in items:
                title_lower = row["title"].lower()
                if any(kw.lower() in title_lower for kw in exclude_keywords):
                    continue
                filtered.append(row)
            items = filtered

# -----------------------------
# 7. 결과 표시
# -----------------------------
if do_search:
    if not items:
        st.info("검색 결과가 없거나, 가격/이미지 정보가 없는 상품입니다.")
    else:
        st.success(f"총 {len(items)}개 상품을 표시합니다. (정렬: {sort_choice})")

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
