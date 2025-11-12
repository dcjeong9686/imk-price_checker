import requests

# 네이버 개발자센터 클라이언트 정보
NAVER_CLIENT_ID = "A4iaEzPgpbxGewkEWvyW"
NAVER_CLIENT_SECRET = "DPyZaHzOEZ"

API_URL = "https://openapi.naver.com/v1/search/shop.json"


def search_product_prices(query, max_results=10, sort_mode="sim"):
    """
    네이버 쇼핑 Open API로 상품 검색.
    - sort_mode: "sim"(관련도순) / "asc"(가격낮은순)
    - 이미지/가격 없는 항목은 제외
    """
    query = query.strip()
    if not query:
        return []

    if sort_mode not in ("sim", "asc"):
        sort_mode = "sim"

    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
    }

    params = {
        "query": query,
        "display": max_results,
        "start": 1,
        "sort": sort_mode,
    }

    resp = requests.get(API_URL, headers=headers, params=params, timeout=15)
    print(f"[DEBUG] 요청 URL: {resp.url}")
    print(f"[DEBUG] 응답 코드: {resp.status_code}")
    resp.raise_for_status()

    data = resp.json()
    items = data.get("items", [])

    results = []
    for item in items:
        title = (item.get("title") or "").replace("<b>", "").replace("</b>", "")
        link = item.get("link", "")
        lprice = item.get("lprice", "")
        mall_name = item.get("mallName", "")
        image_url = item.get("image", "")

        if not lprice.isdigit() or not image_url:
            continue

        price_num = int(lprice)
        results.append({
            "title": title,
            "price": f"{price_num:,}원",
            "mall_name": mall_name,
            "link": link,
            "image_url": image_url,
            "price_num": price_num
        })

    # 가격순일 때는 로컬에서 다시 정렬
    if sort_mode == "asc":
        results.sort(key=lambda x: x["price_num"])

    for r in results:
        r.pop("price_num", None)

    print(f"[DEBUG] 최종 결과 개수: {len(results)}")
    return results


if __name__ == "__main__":
    test = search_product_prices("아이패드", max_results=5, sort_mode="asc")
    for r in test:
        print(r)
