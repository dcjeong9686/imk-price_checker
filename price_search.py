import requests

# ✅ 네이버 개발자센터(developers.naver.com)에서 발급받은 실제 값
NAVER_CLIENT_ID = "A4iaEzPgpbxGewkEWvyW"
NAVER_CLIENT_SECRET = "DPyZaHzOEZ"

API_URL = "https://openapi.naver.com/v1/search/shop.json"


def search_product_prices(query, max_results=10):
    """
    네이버 쇼핑 Open API를 사용해서
    상품명 / 최저가 / 쇼핑몰 / 링크 / 이미지 정보를 가져옵니다.
    가격이 있는 상품만 남기고, 최저가 순으로 정렬합니다.
    """
    query = query.strip()
    if not query:
        return []

    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }

    params = {
        "query": query,
        "display": max_results,
        "start": 1,
        "sort": "sim",
    }

    resp = requests.get(API_URL, headers=headers, params=params)
    print(f"[DEBUG] 요청 URL: {resp.url}")
    print(f"[DEBUG] 응답 코드: {resp.status_code}")
    resp.raise_for_status()

    data = resp.json()
    items = data.get("items", [])

    raw_results = []
    for item in items:
        title = item.get("title", "").replace("<b>", "").replace("</b>", "")
        link = item.get("link", "")
        lprice = item.get("lprice", "")
        mall_name = item.get("mallName", "")
        image_url = item.get("image", "")

        if not lprice.isdigit():
            continue

        price_num = int(lprice)

        raw_results.append(
            {
                "title": title,
                "price_num": price_num,
                "mall_name": mall_name,
                "link": link,
                "image_url": image_url,
            }
        )

    # 최저가 순 정렬
    raw_results.sort(key=lambda x: x["price_num"])

    # 보기 좋게 포맷된 데이터 반환
    results = []
    for r in raw_results[:max_results]:
        results.append(
            {
                "title": r["title"],
                "price": f"{r['price_num']:,}원",
                "mall_name": r["mall_name"],
                "link": r["link"],
                "image_url": r["image_url"],
            }
        )

    print(f"[DEBUG] 최종 결과 개수: {len(results)}")
    return results


# 테스트 실행
if __name__ == "__main__":
    keyword = "아이패드"
    items = search_product_prices(keyword, max_results=5)
    for item in items:
        print(item)
