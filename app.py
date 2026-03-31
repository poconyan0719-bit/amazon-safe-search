import streamlit as st
import urllib.parse
import requests
from bs4 import BeautifulSoup
import time
import re

# ページ設定
st.set_page_config(
    page_title="Amazon安心検索",
    page_icon="🛒",
    layout="wide",  # 一覧表示のためにワイドレイアウトに変更
    initial_sidebar_state="collapsed"
)

# 定数
AFFILIATE_TAG = "tripnotes-22"
BASE_URL = "https://www.amazon.co.jp"
SEARCH_URL = f"{BASE_URL}/s?k={{query}}&emi=AN1VRQENFRJN5"
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
    'Accept-Language': 'ja,en-US;q=0.9,en;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Referer': 'https://www.google.com/',
}

# カスタムCSSの適用
st.markdown("""
<style>
/* タイトルのフォントサイズを少し小さく */
h1 {
    font-size: 2.1rem !important;
}
/* 商品カードのスタイル */
.product-card {
    border: 1px solid #e0e0e0;
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 20px;
    background-color: white;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    transition: transform 0.2s;
}
.product-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 12px rgba(0,0,0,0.1);
}
.product-image {
    width: 100%;
    height: 180px;
    object-fit: contain;
    margin-bottom: 15px;
}
.product-title {
    font-size: 0.9rem;
    font-weight: bold;
    height: 3.6rem;
    overflow: hidden;
    display: -webkit-box;
    -webkit-line-clamp: 3;
    -webkit-box-orient: vertical;
    margin-bottom: 10px;
    color: #333;
}
.product-price {
    font-size: 1.2rem;
    color: #B12704;
    font-weight: bold;
    margin-bottom: 15px;
}
.btn-container {
    display: flex;
    flex-direction: column;
    gap: 8px;
}
.custom-btn {
    display: block;
    width: 100%;
    padding: 8px;
    text-align: center;
    text-decoration: none;
    font-size: 0.85rem;
    font-weight: bold;
    border-radius: 5px;
    transition: opacity 0.2s;
}
.custom-btn:hover {
    opacity: 0.8;
}
.btn-amazon {
    background-color: #FF9900;
    color: white !important;
}
.btn-sakura {
    background-color: #0088CC;
    color: white !important;
}
</style>
""", unsafe_allow_html=True)

def is_sponsored(item):
    """スポンサー商品かどうかを判定する"""
    # 複数のセレクタで判定
    if item.select_one('.puis-sponsored-label-text'):
        return True
    if item.select_one('[data-component-type="sp-sponsored-result"]'):
        return True
    # テキストで「スポンサー」を含む span を探す（部分一致）
    for span in item.find_all('span'):
        txt = span.get_text(strip=True)
        if txt in ('スポンサー', 'Sponsored'):
            return True
    return False

def get_amazon_products(query, target_count=100):
    """Amazonから商品を取得する(スクレイピング)"""
    products = []
    page = 1
    
    progress_bar = st.progress(0, text="商品の取得を開始します...")
    
    while len(products) < target_count:
        # URLの生成 (ページ番号含む)
        encoded_query = urllib.parse.quote_plus(query)
        current_url = f"{SEARCH_URL.format(query=encoded_query)}&page={page}"
        
        try:
            response = requests.get(current_url, headers=HEADERS, timeout=10)
            if response.status_code != 200:
                st.error(f"Amazonへのアクセスに失敗しました (Status: {response.status_code})")
                break
                
            soup = BeautifulSoup(response.text, 'html.parser')
            # 商品アイテムの取得
            items = soup.find_all('div', {'data-component-type': 's-search-result'})
            
            if not items:
                break
                
            for item in items:
                if len(products) >= target_count:
                    break

                # スポンサー商品の除外
                if is_sponsored(item):
                    continue

                try:
                    # ASINを data-asin 属性から直接取得
                    asin = item.get('data-asin', '').strip()
                    if not asin:
                        continue

                    # 商品名（複数のセレクタを試みる）
                    title_elem = (
                        item.select_one('h2 .a-text-normal') or
                        item.select_one('h2 a span') or
                        item.select_one('[data-cy="title-recipe"] span')
                    )
                    title = title_elem.get_text(strip=True) if title_elem else "商品名なし"

                    # アフィリエイトリンク生成
                    affiliate_link = f"{BASE_URL}/dp/{asin}/?tag={AFFILIATE_TAG}"

                    # サクラチェッカーリンク（ASINで直接）
                    sakura_link = f"https://sakura-checker.jp/search/{asin}/"

                    # 画像
                    img_elem = item.select_one('img.s-image')
                    img_url = img_elem.get('src', '') if img_elem else ""

                    # 価格（整数部分のみ、末尾の区切り文字を除去）
                    price_whole = item.select_one('.a-price-whole')
                    if price_whole:
                        price = f"￥{price_whole.get_text(strip=True).rstrip('.,')}"
                    else:
                        price = "価格不明"

                    products.append({
                        'title': title,
                        'asin': asin,
                        'affiliate_link': affiliate_link,
                        'sakura_link': sakura_link,
                        'img_url': img_url,
                        'price': price
                    })

                except Exception:
                    continue
            
            # ページ更新
            page += 1
            progress_percent = min(len(products) / target_count, 1.0)
            progress_bar.progress(progress_percent, text=f"商品を取得中... ({len(products)} / {target_count} 件)")
            
            # アクセス制限回避のためのウェイト
            time.sleep(1)
            
            # 次のページがない場合
            if not soup.select_one('.s-pagination-next'):
                break
                
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
            break
            
    progress_bar.empty()
    return products

# タイトル
st.title("🛒 Amazon安心検索")
st.markdown("販売元が「Amazon.co.jp」のみの商品を最大100件取得し、サクラチェッカーへのリンクと共に表示します。")

# 検索フォーム
with st.form("search_form"):
    col_input, col_btn = st.columns([4, 1])
    with col_input:
        search_query = st.text_input("検索キーワード", placeholder="例：モバイルバッテリー", label_visibility="collapsed")
    with col_btn:
        submit_button = st.form_submit_button("安心検索を実行", use_container_width=True)

if submit_button and search_query:
    results = get_amazon_products(search_query)
    
    if results:
        st.success(f"「{search_query}」の検索結果: {len(results)}件の商品が見つかりました")
        
        # グリッド表示 (4列)
        cols = st.columns(4)
        for idx, product in enumerate(results):
            with cols[idx % 4]:
                st.markdown(f"""
                <div class="product-card">
                    <img src="{product['img_url']}" class="product-image">
                    <div class="product-title" title="{product['title']}">{product['title']}</div>
                    <div class="product-price">{product['price']}</div>
                    <div class="btn-container">
                        <a href="{product['affiliate_link']}" target="_blank" class="custom-btn btn-amazon">🛒 Amazon (直販)</a>
                        <a href="{product['sakura_link']}" target="_blank" class="custom-btn btn-sakura">🌸 サクラチェッカー</a>
                    </div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.warning("商品が見つかりませんでした。別のキーワードでお試しください。")

st.markdown("---")
st.info("💡 **このアプリについて**: 販売元がAmazon.co.jp直販の商品、かつスポンサーを除外して検索します。また、各商品に対してサクラチェッカーでの評価をワンクリックで確認できます。")

st.markdown("""
<div style="text-align: center; color: #888; font-size: 0.8rem; margin-top: 10px; padding: 10px;">
    本サイトはAmazonアソシエイト・プログラムの参加者です。<br>
    Amazon、Amazon.co.jpおよびそれらのロゴはAmazon.com, Inc.またはその関連会社の商標です。<br>
    当サイトの商品リンクを経由してご購入いただいた場合、当サイトは紹介料を受け取ることがあります。
</div>
""", unsafe_allow_html=True)

