import streamlit as st
import pandas as pd
from price_search import search_product_prices

st.set_page_config(
    page_title="네이버 쇼핑 가격 비교",
    page_icon="💸",
    layout="wide",
)

st.title("💸 네이버 쇼핑 가격 비교 대시보드")
st.write(
    "상품명을 입력하면 네이버 쇼핑 API를 통해 **가격, 이미지, 쇼핑몰 정보**를 "
    "최저가 순으로 표 형식으로 보여줍니다."
)

# 🔍 검색창
query = st.text_input("상품명 입력", value="아이패드")

# 결과 개수 선택
max_results = st.slider("표시할 상품 개수", 5, 30, 10, 5)

# 버튼 클릭 시 실행
if st.button("검색"):
    if not query.strip():
        st.warning("상품명을 입력해주세요.")
    else:
        with st.spinner("네이버 쇼핑에서 데이터 가져오는 중..."):
            try:
                items = search_product_prices(query, max_results=max_results)
            except Exception as e:
                st.error(f"오류 발생: {e}")
                items = []

        if not items:
            st.info("검색 결과가 없거나, 가격/이미지 정보가 없는 상품입니다.")
        else:
            st.success(f"총 {len(items)}개 상품을 찾았습니다 (최저가 순).")

            # 🔽 DataFrame으로 변환
            df = pd.DataFrame(items)

            # 우리가 보고 싶은 순서대로 컬럼 재정렬
            df = df[["image_url", "title", "price", "mall_name", "link"]]

            st.subheader("📋 이미지 포함 표 형식 보기")

            st.dataframe(
                df,
                column_config={
                    "image_url": st.column_config.ImageColumn(
                        "이미지",
                        help="상품 썸네일",
                        width="small",  # small/medium/large
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
